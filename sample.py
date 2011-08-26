from decorators import profile_eventlet
from eventlet.green import urllib2
from eventlet.greenpool import GreenPool

def fetcher():
    urllib2.urlopen('http://twitter.com/colinhowe').read()

@profile_eventlet('/tmp/profile-sample')
def entrance():
    pool = GreenPool(100)
    for x in range(10):
        pool.spawn(fetcher)
    pool.waitall()

if __name__ == "__main__":
    entrance()
