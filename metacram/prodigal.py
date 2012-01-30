# For using Prodigal Gene Prediction

from runner import *
from logger import *

def prodigal(**ops):
    ''' Performs ORF prediction using Prodigal
    
    Example: 
    
    >>> prodigal(
    ... input ='input.fasta',
    ... out = 'out_prefix'
    ... )
    
    This will create three files:
    
    out_prefix.gff - GFF file containing annotations.
    out_prefix.faa - Amino Acid sequences for ORF predictions.
    out_prefix.fna - Nucleotide sequences for ORF predictions.
    
    '''
    
    prodigal = ' '.join([
        '~/cram/bin/prodigal',
        '-q',
        '-f gff',
        '-i %(input)s',
        '-o %(out)s.gff',
        '-a %(out)s.faa',
        '-d %(out)s.fna',
        '-p meta'
    ]) % ops
    
    ohai('running prodigal: %(input)s' % ops)
    run(prodigal, generates=[ops['out'] + i for i in ('.gff', '.faa', '.fna')])