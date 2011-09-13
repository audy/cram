def log(s):
    ''' updates log file '''
    message = "%s\t%s" % (time.strftime('%c'), s)
    with open('log.txt', 'a') as out:
        print >> out, message

def get_outdir(out):
    ''' append config to d '''
    def s(s):
        # TODO make sure directories exist and if not, make them
        return out + '/' + s.lstrip('/')
    return s

def ohai(s):
    ''' simple status message '''
    log(s)
    c = '\033[96m'
    e = '\033[0m'
    print ' %s✪ %s%s' % (c, s, e)

def okay(s):
    log(s)
    ''' successfully did something '''
    c = '\033[92m'
    e = '\033[0m'
    print ' %s✓%s %s' % (c, e, s)

def ohno(s):
    log(s)
    ''' did something and AAH! failure! '''
    c = '\033[91m'
    e = '\033[0m'
    print '\n %s✖%s %s' % (c, e, s)
    quit(1)

def run(cmd, generates=False, force=False):
    ''' runs a system command, unless output exists '''
    
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