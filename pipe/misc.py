import os

def run(cmd):
    ''' runs a system command '''
    return os.system(cmd)

def velvet(**ops):
    ''' run velvet assembly '''
    
    velveth = 'bin/velveth %(outdir)s %(kmer)s -fasta -short %(reads)s' % ops
    velvetg = 'bin/velvetg %(output)s'
    
    run(velveth)
    run(velveth)
    

def trim(**ops):
    ''' run trim program '''
    pass

def reference_assemble(**orfs):
    ''' reference assemble '''
    pass

def prodigal(**ops):
    ''' run prodigal '''
    
    prodigal = 'bin/prodigal -q -f gff -i %(input)s -o %(out)s.gff -a %(out)s.faa -d %(out)s.fnn -p meta' % ops
    run(prodigal)

def phmmer(**ops):
    ''' run phmmer '''
    
    phmmer = 'bin/phmmer --cpu 24 --noali -o /dev/null --tblout %(out)s.table -E 0.00001 %(query)s %(db)s' % ops
    run(phmmer)