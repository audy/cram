# encoding: utf-8

import os
import sys
import time

from trim import *
from dnaio import *

# TODO fix colors, my colorscheme is weird and they look wrong on all other terminals.

def log(s):
    ''' updates log file '''
    message = "%s\t%s" % (time.strftime('%c'), s)
    with open('log.txt', 'a') as out:
        print >> out, message

def get_outdir(out):
    ''' append config to d '''
    def s(s):
        # TODO make sure directories exist and if not, make them
        return out + '/' + s.lstrip('/')
    return s

def ohai(s):
    ''' simple status message '''
    log(s)
    c = '\033[96m'
    e = '\033[0m'
    print ' %s✪ %s%s' % (c, s, e)

def okay(s):
    log(s)
    ''' successfully did something '''
    c = '\033[92m'
    e = '\033[0m'
    print ' %s✓%s %s' % (c, e, s)

def ohno(s):
    log(s)
    ''' did something and AAH! failure! '''
    c = '\033[91m'
    e = '\033[0m'
    print '\n %s✖%s %s' % (c, e, s)
    quit(1)

def run(cmd, generates=False, force=False):
    ''' runs a system command, unless output exists '''
    
    # check if output already exists, skip if it does.
    if generates and not force:
        if type(generates) == str:
                generates = [generates]
        for f in generates:
            if os.path.exists(f):    
                okay('skipping')
                return
    if force:
        okay('forced')
    
    res = os.system(cmd)
    if res == 0:
        if generates:
            okay('complete')
        else:
            okay(cmd)
    else:
        if generates:
            for f in generates:
                if os.path.exists(f):
                    os.unlink(f)
        ohno(cmd)

def trim_pairs(**ops):
    ''' trim paired reads, output interleaved fastq and singletons files '''
    
    ohai('trimming pairs')
    for f in [ops['out_left'], ops['out_right'], ops['out']]:
        if os.path.exists(f):
            okay('skipping!')
            return
    
    input_format = ops.get('input_format', 'qseq')
    
    left_mates  = Dna(ops['left_mates'], type=input_format)
    right_mates = Dna(ops['right_mates'], type=input_format)
    out_left    = open(ops['out_left'], 'w')
    out_right   = open(ops['out_right'], 'w')
    out_trimmed = open(ops['out'], 'w')
    cutoff      = int(ops['cutoff'])
    
    from itertools import izip
    
    for left, right in izip(left_mates, right_mates):
        left_trimmed, right_trimmed = Trim.trim(left), Trim.trim(right)
        
        if len(right_trimmed) < cutoff and len(left_trimmed) < cutoff:
            # both reads suck
            continue
        elif len(right_trimmed) < cutoff:
            # keep left pair
            print >> out_left, left_trimmed.fastq
        elif len(left_trimmed) < cutoff:
            # keep right pair
            print >> out_right, right_trimmed.fastq
        else:
            # both are good, keep both!
            print >> out_trimmed, left_trimmed.fastq
            print >> out_trimmed, right_trimmed.fastq
    
    # way too many file handles :[
    out_left.close()
    out_right.close()
    out_trimmed.close()
    left_mates.close()
    right_mates.close()

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
        '--similaritys %(similarity)s'
        ]) % ops
        
    run(cmd, generates="%(out)s" % ops)

def assembly_table(**ops):
    ''' generate an assembly table from clc output '''
    
    cmd = 'bin/assembly_table -n -s %(input)s > %(out)s' % ops
    run(cmd, generates="%(out)s" % ops)


def reference_assemble(**ops):
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
    assembly_table(
        input  = ops['out'] + '.clc',
        out    = ops['out']
    )

def prodigal(**ops):
    ''' run prodigal '''
    
    prodigal = ' '.join([
        'bin/prodigal',
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

def phmmer(**ops):
    ''' run phmmer '''
    
    # phmmer doesn't like to use as many cpus as you specify
    # so it would be a good idea to put some kind of simple
    # map reduce in here,  ala: from concurrent.futures import *
    
    # phmmer is slow when it comes to threading. I don't think has
    # anything to do with Disk IO as it's still slow even with a
    # ram disk. I may have to use some kind of map-reduce to speed
    # this up.
    
    phmmer = ' '.join([
        'bin/phmmer',
        '--notextw',
        '--domE 0.001',
        '--incE 0.00001',
        '--cpu 24',
        '--incdomE 0.00001',
        '--noali',
        '-o /dev/null',
        '--tblout %(out)s.table',
        '-E 0.00001',
        #'/dev/stdin',
        '%(query)s',
        '%(db)s'
    ]) % ops
    
    ohai('running phmmer: %(query)s vs. %(db)s' % ops)
    run(phmmer, generates=ops['out'] + '.table')

def prepare_seed(**ops):
    ''' create table of seed_id -> subsystems '''
    
    ohai('generating subsystems table')
    if os.path.exists(ops['out']):
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
            
            a, b, c, d = line
            
            name_to_ss[d] = [b, a, c]
    
    # Print table, using SEED headers
    with open(ops['seed']) as handle, open(ops['out'], 'w') as out:
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

def make_otu_coverage_table(**ops):
    ''' create table of reference sequence, no. hits
    specially for TaxCollector
    '''
    
    reference = ops['reference']
    clc_table = ops['clc_table']
    out       = ops['out']
    
    ohai('creating coverage table')
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
            n_to_counts[orf_name] += 1
            
    # convert back into regs dictionary
    n_to_counts = dict(n_to_counts)

    # print coverage table
    with open(out, 'w') as handle:
        print >> handle, '# function\t%s' % clc_table
        
        for orf_name in n_to_counts:
            count = n_to_counts[orf_name]
            print >> handle, '%s\t%s' % (orf_name, count)


def make_coverage_table(**ops):
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
    # XXX start counting at 1 or 0?
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


def make_subsystems_table(**ops):
    ''' converts a coverage table to a subsystems table given
    the figid -> subsystems info '''
        
    subsnames      = ops['subsnames']
    coverage_table = ops['coverage_table']
    out            = ops['out']
    reads          = ops['reads']
    reads_type     = ops.get('reads_type', 'fasta')
    
    ohai('creating subsystems table')
    if os.path.exists(out):
        okay('skipping')
        return
    
    # get total number of reads
    from itertools import count
    c = count()

    print 'counting reads'

    if type(reads) in (list, tuple):
        for r in reads:
            with open(r) as handle:
                for i in Dna(handle, type=reads_type):
                    total_reads = c.next()
    elif type(reads) is str:
        with open(reads) as handle:
            for i in Dna(handle, type=reads_type):
                total_reads = c.next()
                
    print 'loading names'
    
    # load subsystem names
    with open(subsnames) as handle:
        fig_to_name = {}
        for line in handle:
            if line.startswith('#'): continue
            
            figid, name = line.strip().split('\t')
            
            # what if this happens?
            assert figid not in fig_to_name
            
            fig_to_name[figid] = name
    
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
            subsystems = fig_to_name.get(figid, 'UNIDENTIFIED;' + figid).split(';')
            
            # This merges subsystem hierarchies and sums their counts
            # TODO I really ought to create a test for this as it's pretty
            # crucial and breakeable
            for i in range(len(subsystems)):
                hierarchy = ';'.join(subsystems[:i])
                if hierarchy == '':
                    hierarchy = 'TOTAL'
                merged_counts[hierarchy] += count
    
    with open(out, 'w') as handle:
        print >> handle, "TOTAL\t%s" % total_reads
        for s in sorted(merged_counts, key = lambda x: merged_counts[x], reverse=True):
            print >> handle, "%s\t%s" % (s, merged_counts[s])
