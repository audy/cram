# For using Velvet de-novo assembler

def velvet(**ops):
    ''' run velvet assembly
        outdir = 'output_directory',
        reads = [
            ('fastq', 'short', 'filename.fastq'),
            ('fastq', 'paired', 'paired_reads.fastq'), ...
            ],
        kmer = 31, # see velvet readme
    '''
    read_ops = ['-%s -%s %s' % r for r in ops['reads'] ]
    
    cmd = ' '.join([
        'bin/velveth',
        '%(outdir)s',
        '%(k)s']) % ops
        
    velveth = cmd + ' ' + ' '.join(read_ops) + '>/dev/null'
    velvetg = 'bin/velvetg %(outdir)s -very_clean yes > /dev/null' % ops
    
    ohai('running velveth: %(reads)s, k = %(k)s' % ops)
    run(velveth, generates=ops['outdir']) # run hash algorithm
    ohai('running velvetg: %(outdir)s' % ops)
    run(velvetg, generates=ops['outdir'] + '/contigs.fa') # run assembly algorithm