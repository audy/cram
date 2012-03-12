def split_fasta(**kwargs):
    ''' split a fasta file into x fasta files with n records '''
    
    infile  = kwargs['in']
    out_dir = kwargs['out_dir']
    n       = int(kwargs['n'])
    format  = kwargs.get('format', 'fasta')
    
    i = 0
    with open(infile) as handle:
        out_handle = open('%s/%s.%s' % (out_dir, i, format))
        for record in Dna(handle, type='fasta'):
            if i > n:
                i = 0
                out_handle = open('%s/%s.%s' % (out_dir, i, format))
            print >> out_handle, record
            i += 1