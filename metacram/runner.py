import os

def run(cmd, generates=False, force=False, silent=False, sgi=False):
    ''' Runs a system command unless output exists unless forced.
    Prints a message when it's done'
    
    # run a command
    >>> run('ls > /dev/null')
    ls > /dev/null
    
    # run a command unless a file already exists
    >>> run('ls helps.py', generates='helps.py')
    skipping
    
    # run a command and force it
    # (same as taking out the generates)
    >>> run('ls helps.py > /dev/null', generates='helps.py', force=True)
    forced
    complete
    
    # This should raise an exception
    # >>> run('thisisnotacommand')
    # Traceback (most recent call last):
    #     ...
    # Exception, thisisnotacommand
    
         
    # remove the log file without logging or printing a message or logging :)
    >>> run('rm log.txt', silent=True)
    
    '''
    
    # check if output already exists, skip if it does.
    if generates and not force:
        if type(generates) == str:
                generates = [generates]
        for f in generates:
            # dont skip if output is to std*
            if f in ['/dev/null', '/dev/stdout', '/dev/stderr']:
                break
            if os.path.exists(f) and not silent:    
                okay('skipping')
                return
    if force:
        okay('forced')
    
    res = os.system(cmd)
    if res == 0:
        if generates:
            okay('complete')
        elif not silent:
            okay(cmd)
    else:
        if generates:
            for f in generates:
                if os.path.exists(f):
                    os.unlink(f)
        if not silent:
            ohno(cmd)

if __name__ == '__main__':
    import doctest
    doctest.testmod()