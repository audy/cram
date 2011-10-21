#!/usr/bin/env python

# this executable combines illumina and 454 py and
# is meant to be stored somewhere in PATH

# how to require lib?

def main():

    import sys
    import os

    _root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, _root_dir)

    import pipelines

    def epic_fail():
        print 'epic fail'
        quit(-1)

    # parse arguments
    if len(sys.argv) < 2:
        epic_fail()
    
    task = sys.argv[1]

    options = {
        'directory': '/Users/erictriplett/Desktop/illumina_test'
    }

    {
         'illumina': pipelines.illumina.init,
         'roche454': pipelines.roche454,
     }.get(task, epic_fail).__call__(options)
     

if __name__ == '__main__':
    main()