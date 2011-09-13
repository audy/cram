# For using SMALT reference assembler

def reference_assemble_smalt(**ops):
    ''' reference assemble using smalt '''
    query = ops['query']
    
    # first create index
    
    # reference assemble creating .cigar files