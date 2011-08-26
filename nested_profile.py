import copy
import marshal
import sys
import time

__all__ = ["Profile"]

class Profile(object):

    def _create_timing_store(self):
        # Timings is # calls, wall time (s)
        return { 'timings': (0, 0), 'callees': {} }

    def __init__(self, timer=None):
        self.timer = timer
        if not self.timer:
            self.timer = time.time

        self.call = self._create_timing_store()
        self.call_stack = [self.call]
        self.time_stack = [self.timer()]

    def runcall(self, func, *args, **kw):
        sys.setprofile(self.trace_dispatch)
        try:
            return func(*args, **kw)
        finally:
            sys.setprofile(None)

    def trace_dispatch(self, frame, event, arg):
        t = self.timer()

        if event in ["c_call", "c_return", "c_exception"]:
            fn = "<%s>" % arg.__name__
        else:
            fcode = frame.f_code
            fn = "%s [%s:%d]" % (fcode.co_name, fcode.co_filename, fcode.co_firstlineno)

        self.dispatch[event](self, fn, t)

    def trace_dispatch_call(self, fn, t):
        callees = self.call['callees']
        if fn not in callees:
            callees[fn] = self._create_timing_store()
        self.call_stack.append(self.call)
        self.time_stack.append(t)
        self.call = callees[fn]
       
    def trace_dispatch_return(self, fn, t):
        call_length = t - self.time_stack.pop()
        cum_calls, cum_time = self.call['timings']
        self.call['timings'] = cum_calls + 1, cum_time + call_length
        self.call = self.call_stack.pop()

    dispatch = {
        "call": trace_dispatch_call,
        "exception": lambda *args, **kwargs: 0, # TODO?
        "return": trace_dispatch_return,
        "c_call": trace_dispatch_call,
        "c_exception": trace_dispatch_return,  # the C function returned
        "c_return": trace_dispatch_return,
    }

    def create_stats(self):
        self.stats = copy.deepcopy(self.call_stack[0])

    def print_stats(self, call, indent_size):
        indent = ' ' * indent_size
        for fn, data in call['callees'].items():
            print '%s%.2fs %d %s' % (
                    indent,
                    data['timings'][1],
                    data['timings'][0],
                    fn)
            self.print_stats(data, indent_size + 2)

    def dump_stats(self, file):
        f = open(file, 'wb')
        self.create_stats()
        marshal.dump(self.stats, f)
        f.close()
