# encoding: utf-8

import sys

from dnaio import *
from helps import *

def prepare_seed(**ops):
    ''' Create table of seed_id -> subsystems for use later when creating
    subsystem coverage tables with make_subsystem_table()
    
    >>> prepare_seed(
    ...    seed = '../test/sample_seed.fna',
    ...    peg  = '../test/subsystems2peg',
    ...    role = '../test/subsystems2role',
    ...    out  = '/dev/null'
    ... )
     ✪ preparing SEED subsystems database
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
    ''' converts a coverage table to a subsystems table given
    the figid -> subsystems info
    
    '''

    ohai('generating subsystems coverage table')
    
    # TODO: I used to take into account CLC's paired-end data and get the
    # LCA of the two proteins if they didn't match. However, I stopped doing
    # this for two reasons:
    #
    # 1.) It doesn't make sense: If mates in a pair match different references
    # they are unlikely to match different references with similar functions
    # (I saw this when looking at the output)
    #
    # 2.) CLCs output for paired-data has bugs and is meaningless
        
    subsnames      = ops['subsnames']
    coverage_table = ops['coverage_table']
    out            = ops['out']
    print_unknown  = ops.get('print_unknown', False)
    
    ohai('creating subsystems table')
    if os.path.exists(out):
        okay('skipping')
        return
    
    # load subsystem names
    with open(subsnames) as handle:
        fig_to_name = {}
        for line in handle:
            if line.startswith('#'): continue
            
            figid, name = line.strip().split('\t')
            
            # what if this happens?
            if figid in fig_to_name:
                    assert name == fig_to_name[figid]
            
            fig_to_name[figid] = name
    
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
            # them in the subsystems table.


            if figid in fig_to_name:
                subsystems = fig_to_name[figid]
                subsystems = subsystems.split(';')
                hierarchies = split_hierarchies(subsystems)
                for h in hierarchies:
                    merged_counts[h] += count
            else:
                h = "unidentified_orfs;%s" % figid
                merged_counts[h] += count

    with open(out, 'w') as handle:
        for s in sorted(merged_counts, key = lambda x: merged_counts[x], reverse=True):
            if not print_unknown and s.startswith('unidentified_orfs;'):
                continue
            print >> handle, "%s\t%s" % (s, merged_counts[s])


def split_hierarchies(subsystems):
    ''' splits a subsystem into hierarchies
    
    >>> split_hierarchies('a;b;c;d')
    ... ['a', 'a;b', 'a;b;c', 'a;b;c;d']
    '''
    
    hierarchies = []
    for i in range(len(subsystems)):
      for i, s in enumerate(subsystems):
        if s == '':
          subsystems[i] = '-'
        hierarchy = ';'.join(subsystems[:i])
        hierarchies.append(hierarchy)
    return hierarchies


if __name__ == '__main__':
    import doctest
    doctest.testmod()
