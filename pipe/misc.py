import os

def ohai(s):
    ''' simple status message '''
    c = '\033[90m'
    e = '\033[0m'
    print '   %s %s%s ' % (c, s, e)

def okay(s):
    ''' successfully did something '''
    c = '\033[92m'
    e = '\033[0m'
    print ' %s-%s  %s' % (c, e, s)


def ohno(s):
    ''' did something and AAH! failure! '''
    c = '\033[91m'
    e = '\033[0m'
    print ' %s-%s  %s' % (c, e, s)
    quit()

def run(cmd):
    ''' runs a system command '''
    res = os.system(cmd)
    if res == 0:
        okay(cmd)
    else:
        ohno(cmd)

def velvet(**ops):
    ''' run velvet assembly '''
    
    velveth = ' '.join([
        'bin/velveth',
        '%(outdir)s',
        '%(kmer)s',
        '-fasta',
        '-short',
        ' %(reads)s',
        '> /dev/null']) % ops
    
    velvetg = 'bin/velvetg %(output)s > /dev/null'
    
    ohai('running velvet: %(reads)s, k = %(kmer)s' % ops)
    
    run(velveth)
    run(velveth)

def reference_assemble(**orfs):
    ''' reference assemble using clc_ref_assemble_long '''
    
    clc = 'bin/clc_ref_assemble_long'

def prodigal(**ops):
    ''' run prodigal '''
    
    prodigal = ' '.join([
        'bin/prodigal',
        '-q',
        '-f gff',
        '-i %(input)s',
        '-o %(out)s.gff',
        '-a %(out)s.faa',
        '-d %(out)s.fnn',
        '-p meta'
    ]) % ops
    
    ohai('running prodigal: %(input)s' % ops)
    
    run(prodigal)

def phmmer(**ops):
    ''' run phmmer '''
    
    # phmmer doesn't like to use as many cpus as you specify
    # so it would be a good idea to put some kind of simple
    # map reduce in here,  ala: from concurrent.futures import *
    
    phmmer = ' '.join([
        'bin/phmmer',
        '--notextw',
        '--domE 0.001',
        '--incE 0.00001',
        '--cpu 24',
        '--incdomE 0.00001',
        '--noali',
        '-o /dev/null',
        '--tblout %(out)s.table',
        '-E 0.00001',
        '%(query)s',
        '%(db)s'
    ]) % ops
    
    ohai('running phmmer: %(query)s vs. %(db)s' % ops)
    
    run(phmmer)
    
def prepare_seed(**ops):
    ''' create table of seed_id -> subsystems '''
    
    ohai('generating subsystem table %(out)s from %(seed)s' % ops)
    
    # TODO work out better fig id parsing?
    
    # load subsystems from figids using subsystems2peg
    figs_to_name = {}
    with open(ops['peg']) as handle:
        for line in handle:
            line = line.strip()
            line = line.split('\t')
            
            assert(len(line) == 3)
            
            _, name, fig = line
            
            assert type(fig) == str
            
            figs_to_name[fig] = name
            
    # load full subsystem names using subsystems2role
    name_to_ss = {}
    with open(ops['role']) as handle:
        for line in handle:
            line = line.strip()
            line = line.split('\t')
            
            assert(len(line) == 4)
            
            a, b, c, d = line

            name_to_ss[d] = [b, a, c]


    # Print table, using SEED headers
    with open(ops['seed']) as handle, open(ops['out'], 'w') as out:
        for line in handle:
            if line.startswith('>'):
                
                fig = line.split()[0][1:]
                
                name = figs_to_name.get(fig, fig)

                ss = name_to_ss.get(name, [None]*4)
                
                print >> out, "%s\t%s;%s;%s;%s" % (fig, ss[0], ss[1], ss[2], name)
                
            