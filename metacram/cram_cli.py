#!/usr/bin/env python

import sys
import os
from glob import glob

from metacram import *

# get list of pipelines
# this returns a list of paths to pipelines
# pipeline name is the full path minus directories and extension
# PIPELINES = { 'name': 'path', ... }

this_dir, this_filename = os.path.split(__file__)
PIPELINES = { os.path.basename(i).replace('.py',''): i for i in glob(os.path.join(this_dir, 'pipelines', '*.py')) }

def create_project(script, directory):
    ''' creates a new pipeline in directory given a pipeline module '''
        
    # create directory
    if os.path.exists(directory):
        print >> sys.stderr, "%s exists. Move or delete yourself" % directory
        # quit(-1)
    else:
        os.mkdir(directory)

    # Copy pipeline script to directory
    script_out_file = os.path.join(directory, os.path.basename(script))
    with open(script_out_file, 'w') as output:
        # open script for reading
        with open(script) as handle:
            output.write(handle.read())
            
    ohai('%s created in %s' % (os.path.basename(script), directory))
    ohai('run %s to execute pipeline' % os.path.basename(script))
    

def main():
    ''' meat & potatoes '''
    
    # TODO add this to ARGV. Value gets sent to task function

    if len(sys.argv) < 2:
        print_usage()
        quit(-1)

    # run task or die
    # forward argv to task
    task = sys.argv[1]
    directory = sys.argv[2]
    path = PIPELINES.get(task, False)
    
    # Do something
    if path:
        create_project(path, directory)
    # Print task list
    elif task in ['-h', '--help', 'tasks', 'list']:
        print_usage()
    # Break
    else:
        epic_fail('no task, %s' % task)
        
     
def epic_fail(msg):
    ''' when something goes wrong '''
    print 'ERROR: %s' % msg
    quit(-1)
    
def print_usage():
    ''' prints usage '''
    print "** MetaCRAM **\n\nPipelines:"
    print "    Type metacram <name> <directory> to create a new project.\n"
    for name in PIPELINES:
        print "    %s" % (name)
        

if __name__ == '__main__':
    main()