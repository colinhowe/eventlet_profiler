Eventlet Profiler
=================

Author: Colin Howe (http://www.colinhowe.co.uk @colinhowe)

License: Apache 2.0 license.

A profiler that understands Eventlet.

Usage
=====

Decorate a method to be sampled like so::

    from eventlet_profiler import profile_eventlet

    @profile_eventlet('/tmp/profile')
    def some_method():
        pass

The output will be generated in /tmp/profile. This can then be analysed using
the analyser::

    ./analyser.py /tmp/profile

The difference between this profiler and most is that the output can be drilled 
into and the time spent calling functions from within specific functions can be 
found out.

Sample session
==============

A sample session based on python sample.py and then analysing the results::

    # NB. I've trimmed some of the reptitive stuff to keep this lean

    < ./analyser.py /tmp/profile-sample 
    > qq. Quit
    >
    > Current: 0.000s 0 calls
    >
    > 0. <<idle time>> - 1.047s 0 calls
    > 1. <<tasks>> - 0.520s 10 calls
    > 2. entrance [/.../eventlet_profiler/sample.py:8] - 0.003s 1 calls
    > 3. <setprofile> - 0.000s 0 calls
    
    # The times displayed a wall clock time spent in the function

    < 1
    > Current: 0.520s 10 calls
    >
    > u. Go up a level
    > 0. main [/.../eventlet/greenthread.py:190] - 0.520s 10 calls

    < 0
    > Current: 0.520s 10 calls
    >
    > u. Go up a level
    > 0. fetcher [/.../eventlet_profiler/sample.py:5] - 0.517s 10 calls
    > 1. _resolve_links [/.../eventlet/greenthread.py:201] - 0.002s 10 calls
    > 2. send [/.../eventlet/event.py:123] - 0.001s 10 calls
    
    < qq

Feedback
========

Please raise any issues in the github issue tracker (https://github.com/colinhowe/eventlet_visualiser/issues).
Any feedback is welcome on github or Twitter @colinhowe.

Thanks to
=========

RTyler (https://bitbucket.org/rtyler/) - the eventlet profiling code was heavily
influenced by the code that he wrote to do a similar job.
