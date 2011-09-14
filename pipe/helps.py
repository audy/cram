# encoding: utf-8

import time
import os

def log(s):
    ''' prints to a log file '''
    message = "%s\t%s" % (time.strftime('%c'), s)
    with open('log.txt', 'a') as out:
        print >> out, message

def get_outdir(out):
    ''' Create a function to add output directory to a given directory
    
    >>> d_func = get_outdir('test')
    >>> print d_func('another_directory')
    test/another_directory
    
     '''
    def s(s):
        # TODO make sure directories exist and if not, make them
        return out + '/' + s.lstrip('/')
    return s

def ohai(s):
    '''
    Status message for when something mediocre happens
    
    Used for general status messages
    
    >>> ohai('I am a test AMA')
     ✪ I am a test AMA
    '''
    log(s)
    print ' ✪ %s' % (s)

def okay(s):
    '''
    Status message for when something good happens
    
    >>> okay('I did something cool')
     ✓ I did something cool
    '''
    log(s)
    print ' ✓ %s' % (s)

def ohno(s):
    '''
    Status message for when something bad happens
    Terminates the program with an exit status of 1
    
    # didnt write test for this because it always fails
    
    '''
    log(s)
    print '\n ✖ %s' % (s)
    quit(1)

def run(cmd, generates=False, force=False):
    ''' Runs a system command unless output exists unless forced.
    Prints a message when it's done'
    
    # run a command
    >>> run('ls > /dev/null')
     ✓ ls > /dev/null
    
    # run a command unless a file already exists
    >>> run('ls helps.py', generates='helps.py')
     ✓ skipping
    
    # run a command and force it
    # (same as taking out the generates)
    >>> run('ls helps.py > /dev/null', generates='helps.py', force=True)
     ✓ forced
     ✓ complete
    '''
    
    # check if output already exists, skip if it does.
    if generates and not force:
        if type(generates) == str:
                generates = [generates]
        for f in generates:
            if os.path.exists(f):    
                okay('skipping')
                return
    if force:
        okay('forced')
    
    res = os.system(cmd)
    if res == 0:
        if generates:
            okay('complete')
        else:
            okay(cmd)
    else:
        if generates:
            for f in generates:
                if os.path.exists(f):
                    os.unlink(f)
        ohno(cmd)

if __name__ == '__main__':
    import doctest
    doctest.testmod()