# these functions are for dealing with CLC Assembly Cell and its output

# clc_filter
# assembly_table
# reference_assemble_clc
# make_otu_coverage_table
# make_coverage_table

import re
from helps import *

def clc_filter(**ops):
    ''' filter clc output generating more clc output
    
    clc_filter(assembly = 'assembly.clc',
               out = 'assembly_50_95.txt'.
               length = 0.5,
               similarity = 0.95)    
    '''
    
    ohai('clc_filter: %(assembly)s, o=%(out)s, l=%(length)s, s=%(similarity)s')
    
    cmd = ' '.join([
        'bin/filter_matches',
        '--assembly %(assembly)s',
        '--output %(out)s',
        '--lengthfraction %(length)s',
        '--similarity %(similarity)s'
        ]) % ops
    print cmd        
    run(cmd, generates="%(out)s" % ops)


def clc_assembly_table(**ops):
    ''' generate an assembly table from clc output '''
    
    cmd = 'bin/assembly_table -n -s %(input)s > %(out)s' % ops
    run(cmd, generates="%(out)s" % ops)

def clc_reference_assemble(**ops):
    ''' reference assemble using clc_ref_assemble_long '''

    query = ops['query']

    # TODO add support for interleaving two files!
    # TODO and add support for other read orientations :\
    querytypes = {'paired': '-q -p fb ss 0 500', 'unpaired': '-q' }

    if type(query) is str:
        query_ops = '-q %s' % ops['query']
    elif type(query) in (list, tuple):
        query_ops = ' '.join("%s %s" % (querytypes[i[0]], i[1]) for i in query)

    clc = ' '.join([
      'bin/clc_ref_assemble_long',
      '-d %(reference)s',
      '-o %(out)s.clc',
      '-a local', # todo, make an option?
      '--cpus 16', # todo, autodetect.
      ]) % ops

    clc = clc + ' ' + query_ops

    ohai('running reference assembly %(query)s vs. %(reference)s' % ops)
    run(clc, generates=ops['out'] + '.clc')

    # generate assembly table
    clc_assembly_table(
        input  = ops['out'] + '.clc',
        out    = ops['out']
    )
    

def clc_otu_coverage_table(**ops):
    ''' create table of reference sequence, no. hits
    specially for TaxCollector
    '''

    reference = ops['reference']
    clc_table = ops['clc_table']
    out       = ops['out']
    level     = ops['level']

    if level:
        regex = re.compile(r'\[%s\](.*?)($|;\[)' % level)

    ohai('Creating OTU Coverage table from CLC assembly')
    if os.path.exists(out):
        okay('skipping')
        return

    from itertools import count
    from collections import defaultdict

    c, n_to_orf = count(), {}
    n_to_orf[-1] = 'unmatched'
    with open(reference) as handle:
        for line in handle:
            if line.startswith('>'):
                n = c.next()
                orf = line.lstrip('>').rstrip().split()[0]
                n_to_orf[n] = orf

    # get sequence # -> header from reference db
    # * fix this for paired output!?
    # * clc has a bug in table output, might not even need to do this.
    n_to_counts = defaultdict(int) # { reference: reads that mapped to it }
    with open(clc_table) as handle:
        for line in handle:
            line = line.strip().split()
            ref_n = int(line[5])
            orf_name = n_to_orf.get(ref_n, 'DB ERROR?')
            print orf_name
            n_to_counts[orf_name] += 1

    # convert back into regs dictionary
    n_to_counts = dict(n_to_counts)

    # print coverage table
    with open(out, 'w') as handle:
        print >> handle, '# OTU\t%s' % clc_table

        for orf_name in n_to_counts:
            count = n_to_counts[orf_name]

            # get orf name at level
            if level:
                m = re.search(regex).span()
                if m:
                    start, end = m
                    orf_name = orf_name[start, end]
                else:
                    orf_name = 'NULL'

            print >> handle, '%s\t%s' % (orf_name, count)


def clc_coverage_table(**ops):
    ''' create table of reference sequence, no. hits
    specially for SEED.
    '''

    # TODO: if I "taxcollect" the SEED database first, 
    # then it will be possible to merge this
    # with make_otu_coverage_table()

    reference = ops['reference']
    clc_table = ops['clc_table']
    out       = ops['out']
    phmmer    = ops['phmmer']

    ohai('creating coverage table')
    if os.path.exists(out):
        okay('skipping')
        return

    from itertools import count
    from collections import defaultdict

    # get sequence # -> header from reference db
    # * fix this for paired output!?
    # * clc has a bug in table output, might not even need to do this.
    n_to_counts = defaultdict(int) # { reference: reads that mapped to it }
    with open(clc_table) as handle:
        for line in handle:
            line = line.strip().split()
            ref_n = int(line[5])

            n_to_counts[ref_n] += 1

    # convert to a regs dictionary
    n_to_counts = dict(n_to_counts)

    # which names to keep?
    keep = set(n_to_counts.keys())

    # get names of references that we care about
    
    c, n_to_orf = count(), {}
    n_to_orf[-1] = 'unmatched'

    with open(reference) as handle:
        for line in handle:
            if line.startswith('>'):
                n = c.next()
                orf = line.lstrip('>').rstrip().split()[0]
                if n in keep:
                    n_to_orf[n] = orf

    # load phmmer output table to get figids from ORF names
    orf_to_figid = {}
    with open(phmmer) as handle:
        for line in handle:
            if line.startswith('#'): continue
            line = line.strip().split()

            figid, orf = line[0], line[2]

            assert orf not in orf_to_figid

            orf_to_figid[orf] = figid

    # print coverage table
    with open(out, 'w') as handle:
        print >> handle, '# function\t%s' % clc_table
        for n in n_to_counts:
            orf = n_to_orf[n]
            figid = orf_to_figid.get(orf, orf)

            count = n_to_counts[n]
            print >> handle, '%s\t%s' % (figid, count)
