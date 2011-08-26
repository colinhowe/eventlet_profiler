import os
import time
import eventlet_profiler

def profile_eventlet(log_file, add_timestamp=False):
    """Decorator to profile something in a way that understands the magic
    eventlet performs.
    """

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            if add_timestamp:
                base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = eventlet_profiler.Profile()
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.create_stats()
                prof.dump_stats(final_log_file)
            return ret

        return _inner
    return _outer
