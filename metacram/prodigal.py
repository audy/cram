# For using Prodigal Gene Prediction

from helps import *

def prodigal(**ops):
    ''' run prodigal '''
    
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