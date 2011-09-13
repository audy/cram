# For using SMALT reference assembler

from helps import *

def smalt_index(**ops):
    ''' build reference index '''
    reference = ops['reference']
    name      = ops['name']
    
    cmd = 'smalt index %s %s' % (name, reference)
    run(cmd, generates='%s.smi' % name)

def smalt_map(**ops):
    ''' reference assemble using smalt '''
    
    query     = ops['query']
    reference = ops['reference']
    identity  = ops['identity']
    out       = ops['out']
    threads   = ops.get('threads', 8)
    
    if type(query) is str:
        query_ops = '-q %s' % ops['query']
    elif type(query) in (list, tuple):
        raise Exception, 'currently SMALT can only deal with one reference at a time'
    
    # reference assemble creating .cigar files
    
    cmd = 'smalt map -n %s -y %s -o %s %s %s > /dev/null' % (threads, identity, out, reference, query)
    
    run(cmd, generates=out)
    
def smalt_coverage_table(**opse):
    ''' generate coverage table from smalt cigar output '''
    # this should be easy :)
    pass
