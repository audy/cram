from runner import *
from logger import *

def formatdb(**args):
    ''' run NCBI formatdb '''
    
    database = args['database']
    
    cmd = ' '.join([
        '~/cram/bin/formatdb',
        '-i %s' % database,
    ])
    
    ohai('running formatdb')
    
    run(cmd, generates='%s.psq' % database)

def blastp(**args):
    ''' run BLASTALL (default is blastp, can be overriden with program=) '''
    
    cmd = ' '.join([
        '~/cram/bin/blastall',
        '-p %s' % args.get('program', 'blastp'),
        '-d %s' % args['db'],
        '-i %s' % args['query'],
        '-e %s' % args.get('evalue', 10),
        '-o %s' % args['out'],
        '-v %s' % args.get('alignments', 1),
        '-b %s' % args.get('descriptions', 1),
        '-a %s' % args.get('threads', 24),
        '-m %s' % args.get('format', 8)
    ])
    
    ohai('running blastp')
    
    run(cmd, generates=args['out'])
