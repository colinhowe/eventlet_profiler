#!/usr/bin/python
import sys
import marshal

GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'

class Analyser(object):
    def run(self, file_in):
        self.call = marshal.load(file_in)
        self.current = self.call
        self.stack = []

        while self.loop():
            pass

    def timing_string(self, call):
        return "%.3fs %d calls" % call['timings']

    def loop(self):
        print RED + 'qq. Quit' + ENDC
        print
        print 'Current: %s' % self.timing_string(self.current)
        print
        if self.stack:
            print GREEN + 'u.' + ENDC + ' Go up a level'

        callees = self.current['callees'].items()
        def sorter(a, b):
            return cmp(b[1]['timings'][1], a[1]['timings'][1])
        callees = sorted(callees, sorter)
        for i, callee in enumerate(callees):
            print (GREEN + '%d.' + ENDC + ' %s - %s') % (
                i, 
                callee[0], 
                self.timing_string(callee[1]),
            )

        print
        sys.stdout.write('> ')

        option = sys.stdin.readline().strip()
        if option == 'qq':
            return False
        elif option == 'u' and self.stack:
            self.current = self.stack.pop()
            return True
        else:
            try:
                i = int(option)
                if 0 <= i < len(callees):
                    self.stack.append(self.current)
                    self.current = callees[i][1]
                    return True
            except:
                pass
            print RED + 'Invalid option' + ENDC
            return True

if __name__ == "__main__":
    Analyser().run(file(sys.argv[1]))
