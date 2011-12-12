# For using Velvet de-novo assembler

from helps import *

def velvet(**ops):
    ''' Performs a de novo assembly using Velvet
    
    Example:
    
    >>> velvet(
    ... outdir = 'output_directory',
    ... # reads must be an array of tuples (even if you're only using one file)
    ... # in the following form:
    ...
    ... reads = [
    ... ('format', 'short long or paired', 'filename.fastq'), ... ]
    ...
    ... # example:
    ... reads = [
    ... ('fastq', 'paired', 'paired_reads.fastq'), ...
    ... ],
    ... kmer = 31, # see velvet readme for why this is important
    ... )
    
    
    '''
    read_ops = ['-%s -%s %s' % r for r in ops['reads'] ]
    
    cmd = ' '.join([
        '~/cram/bin/velveth',
        '%(outdir)s',
        '%(k)s']) % ops
        
    velveth = cmd + ' ' + ' '.join(read_ops) + '>/dev/null'
    velvetg = '~/cram/bin/velvetg %(outdir)s -very_clean yes > /dev/null' % ops
    
    ohai('running velveth: %(reads)s, k = %(k)s' % ops)
    run(velveth, generates=ops['outdir']) # run hash algorithm
    ohai('running velvetg: %(outdir)s' % ops)
    run(velvetg, generates=ops['outdir'] + '/contigs.fa') # run assembly algorithm