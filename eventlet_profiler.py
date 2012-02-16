# An eventlet profiler, heavily influenced and parts borrowed from:
#   https://bitbucket.org/rtyler/eventlet/src/6fab81818ccd/eventlet/green/profile.py
# 

import nested_profile
profile_orig = nested_profile

for var in profile_orig.__all__:
    exec "%s = profile_orig.%s" % (var, var)

import functools

from eventlet import greenthread
from eventlet import patcher
thread = patcher.original('thread')  # non-monkeypatched module needed

class Profile(profile_orig.Profile):
    base = profile_orig.Profile
    def __init__(self, timer = None):
        self.current_tasklet = greenthread.getcurrent()
        self.base.__init__(self, timer)
        self.sleeping = {}

    def _setup(self):
        self.tasks = self._create_timing_store()
        self.call = self._create_timing_store()
        self.call_stack = [self.call]
        self.current_tasklet = greenthread.getcurrent()
        self.start_call = self.call
        self.start_time = self.timer()

    def runcall(self, func, *args, **kw):
        self._setup()
        try:
            return profile_orig.Profile.runcall(self, func, *args, **kw)
        finally:
            self.TallyTimings()

    def runctx(self, cmd, globals, locals):
        self._setup()
        try:
            return profile_orig.Profile.runctx(self, cmd, globals, locals)
        finally:
            self.TallyTimings()

    dispatch = profile_orig.Profile.dispatch

    def SwitchTasklet(self, task_0, task_1, t):
        # The current task needs to store the time it was suspended so that
        # a discount can be applied to its timing later
        self.time_stack.append(t)
        self.sleeping[task_0] = self.call, self.call_stack, self.time_stack,
        self.current_tasklet = task_1

        try:
            self.call, self.call_stack, self.time_stack = self.sleeping[task_1]
            # The existing task will need its existing times adjusted to account
            # for the time spent sleeping
            suspended_time = t - self.time_stack.pop()
            self.time_stack = [x + suspended_time for x in self.time_stack]
        except KeyError:
            self.call = self._create_timing_store()
            self.time_stack = []
            self.call_stack = [self.call]

    def ContextWrap(f):
        @functools.wraps(f)
        def ContextWrapper(self, fn, t):
            current = greenthread.getcurrent()
            if current != self.current_tasklet:
                self.SwitchTasklet(self.current_tasklet, current, t)
            return f(self, fn, t)
        return ContextWrapper

    #Add automatic tasklet detection to the callbacks.
    dispatch = dict([(key, ContextWrap(val)) for key, val in dispatch.iteritems()])

    def merge_timings(self, a, b):
        if a is None:
            return b
        if b is None:
            return a

        total_calls = a['timings'][0] + b['timings'][0]
        total_time = a['timings'][1] + b['timings'][1]
        timings = { 'timings': (total_calls, total_time), 'callees': {} }
        
        all_fns = set(a['callees'].keys() + b['callees'].keys())
        for fn in all_fns:
            timings['callees'][fn] = self.merge_timings(
                a['callees'].get(fn), b['callees'].get(fn)
            )
        return timings

    def TallyTimings(self):
        end_time = self.timer()

        total_tasks = 0
        total_task_time = 0.0
        sleeping_tasks = {}
        for call, _, _ in self.sleeping.values():
            for fn, callee in call['callees'].items():
                total_task_time += callee['timings'][1]
                total_tasks += callee['timings'][0]

                sleeping_tasks[fn] = self.merge_timings(
                        sleeping_tasks.get(fn),
                        callee
                )

        self.call = self.start_call
        self.call_stack = [self.call]
        self.call['callees']['<<tasks>>'] = { 
                'timings': (total_tasks, total_task_time),
                'callees': sleeping_tasks
        }

        self.call['callees']['<<idle time>>'] = {
            'timings': (0, (end_time - self.start_time) - total_task_time),
            'callees': {}
        }
