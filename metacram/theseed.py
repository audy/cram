from dnaio import *
from runner import *
from logger import *

def prepare_seed(**ops):
    '''
    This is to be made obsolete by an executable that prepares the seed
    database by altering the headers and places it in ~/cram/db
    
    Create table of seed_id -> subsystems for use later when creating
    subsystem coverage tables with make_subsystem_table()
    
    >>> prepare_seed(
    ...    seed = '../test/sample_seed.fna',
    ...    peg  = '../test/subsystems2peg',
    ...    role = '../test/subsystems2role',
    ...    out  = '/dev/null'
    ... )
    preparing SEED subsystems database
    '''
    
    ohai('preparing SEED subsystems database')
    if os.path.exists(ops['out']) and '/dev' not in ops['out']:
        okay('skipping')
        return
        
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
            
            a, c, b, d = line[1], line[2], line[0], line[3]
            
            name_to_ss[d] = [a, b, c]
    
    # Print table, using SEED headers
    with open(ops['seed']) as handle:
        with open(ops['out'], 'w') as out:
            for line in handle:
                if line.startswith('>'):
                
                    fig = line.split()[0][1:]
                    name = figs_to_name.get(fig, fig)
                    ss = name_to_ss.get(name, 'NA')
                
                    if ss == 'NA':
                        names = 'NA;%s' % name
                    else:
                        names = '%s;%s;%s;%s' % (ss[0], ss[1], ss[2], name)
                
                    print >> out, "%s\t%s" % (fig, names)


def subsystems_table(**ops):
    ''' Converts an ORFs coverage table to a subsystems table given
    the figid -> subsystems info
    
    The ORFs coverage table contains the ORF annotation (or ORF name if not
    found in the SEED database) and the number of reads that mapped to it
    by the reference assembly (SMALT).
    
    Example:
    
    fig|296591.12.peg.5415  15
    NODE_89_length_964_cov_3.000000_85_3    1
    _Delta-9_fatty_acid_desaturase_(EC_1.14.19.1)_[SS]_(GI:91791132)        3
    
    This table is converted to a table containing the annotation of the
    fig ID given by the SEED database using this function.
    
    Example:
    
    >>> subsystems_table(
    ... seed_db = 'tc_seed.fasta',
    ... coverage_table = '',
    ... out = 'subsystems_table.txt'
    ... )
    
    The SEED database has to have the full annotation in the headers. This is
    not provided by the original seed database but can be created using
    SeedCollector.
    
    The headers look like this:
    
    >Carbohydrates;Xylose_utilization;Monosaccharides;Beta-xylosidase_(EC_3.2.1.37);fig|100226.1.peg.99
    
    The subsystems are in order from broadest to most-specific, separated by
    semicolons and followed by the fig ID:
    
    >Sub1;Sub2;Sub3;Sub4;FIG_ID
    
    If subsystems are missing, they are to be replaced by 'NA':
    
    >NA;NA;NA;unknown_function_(GI:334129254);fig|1000565.3.peg.15
    
    The output of this table will not only contain the number of reads for
    each subsystem:
    
    Sub1;Sub2;Sub3;Sub4 500
    Sub1;Sub2;SubX;SubY 400
    
    But also aggregate broader subsystems and give their cumulative coverage
    
    Sub1;Sub2;Sub3;Sub4 500
    Sub1;Sub2;Sub3      500
    Sub1;Sub2;SubX;SubY 400
    Sub1;Sub2;SubX      400
    Sub1;Sub2           900
    Sub1;               900
    
    This is so that metabolic potential can be compared across samples at
    different degrees of specificity.
    
    '''
    
    ohai('generating subsystems coverage table')
    seed_db        = ops['seed_db']
    coverage_table = ops['coverage_table']
    out            = ops['out']
    
    ohai('creating subsystems table')
    # if os.path.exists(out):
    #     okay('skipping')
    #     return
    
    # load subsystem names from seed_tc.fasta
    fig_to_name = {}
    with Dna(open(seed_db)) as records:
        for record in records:
            names = record.header.split(';')
            figid = names[-1]
            names = names[0:-1]
            
            # what if this happens?
            if figid in fig_to_name:
                assert names == fig_to_name[figid]
            
            fig_to_name[figid] = names
    
    # the output table should look like this:
    # sys_a,\t10
    # sys_a;sys_a.1\t5
    # sys_a;sys_a.2\t5 etc...
    
    # parse coverage table and output hierarchies based on SEED subsystems
    from collections import defaultdict
    merged_counts = defaultdict(int)
    
    with open(coverage_table) as handle:
        for line in handle:
            if line.startswith('#'): continue
            figid, count = line.strip().split('\t')
            count = int(count)
            
            # use figid to get the ss name, or just keep the figid
            # that usually means that the ORF was not identified
            # in the SEED database and it's still useful to have
            # them in the subsystems table. However, we append
            # 'unidentified' at the beginning
            subsystems = fig_to_name.get(figid, figid).split(';')
            
            # This merges subsystem hierarchies and sums their counts
            # TODO I really ought to create a test for this as it's pretty
            # crucial and breakeable
            for i in range(len(subsystems)):
              for i, s in enumerate(subsystems):
                  if s == '':
                      subsystems[i] = '-'
                  hierarchy = ';'.join(subsystems[:i])
                  merged_counts[hierarchy] += count
    
    with open(out, 'w') as handle:
        for s in sorted(merged_counts, key = lambda x: merged_counts[x], reverse=True):
            print >> handle, "%s\t%s" % (s, merged_counts[s])

