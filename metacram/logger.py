import time

def log(s):
    ''' prints to a log file '''
    message = "%s\t%s" % (time.strftime('%c'), s)
    with open('log.txt', 'a') as out:
        print >> out, message

def ohai(s):
    '''
    Status message for when something mediocre happens
    
    Used for general status messages
    
    >>> ohai('I am a test AMA')
    I am a test AMA
    '''
    log(s)
    print '# %s' % (s)

def okay(s):
    '''
    Status message for when something good happens
    
    >>> okay('I did something cool')
    > I did something cool
    '''
    log(s)
    print '> %s' % (s)

def ohno(s):
    '''
    Status message for when something bad happens
    
    Also, raises an Exception
    
    >>> try:
    ...     ohno('fail')
    ... except:
    ...     pass
    ! fail
    
    '''
    
    log(s)
    print '! %s' % (s)
    raise Exception, s

if __name__ == '__main__':
    import doctest
    doctest.testmod()