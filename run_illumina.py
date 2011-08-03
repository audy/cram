#!/usr/bin/env python
# encoding: utf-8

from pipe import *

# check if user ran make    
if not os.path.exists('bin'):
    ohno('bin/ doesn\'t exist. Did you run make?')

cutoff = 70
out    = 'out'
left_mates = 'data/s71.qseq'
right_mates = 'data/s73.qseq'

# Creates a simple function to prepend the output directory
# to the directory/filename you specify
d = get_outdir(out)

ohai('running pipeline!')

## MAKE DIRECTORIES
[ run('mkdir -p %s' % i) for i in [
    out,
    d('orfs'),
    d('anno'),
    d('refs'),
    d('tables') ] ]

trim_pairs(
    left_mates  = left_mates,
    right_mates = right_mates,
    out_left    = d('singletons_left.fastq'),
    out_right   = d('singletons_right.fastq'),
    out         = d('reads_trimmed.fastq'),
    cutoff      = cutoff
)

# ASSEMBLE W/ VELVET
kmers = {
     31: d('contigs_31'),
     51: d('contigs_51'),
     71: d('contigs_71')
}

for kmer in kmers:
    velvet(
        reads = [
            ('fastq', 'shortPaired', d('reads_trimmed.fastq')),
            # ('fastq', 'short', d('singletons_left.fastq')),
            # ('fastq', 'short', d('singletons_right.fastq'))
        ],
        outdir = kmers[kmer],
        kmer   = kmer
    )

# run final assembly
# type of assembly depends on whether or not contigs from first
# 3 assemblies are actually long.

velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('final_contigs'),
    kmer     = 51
)

# PREDICT OPEN READING FRAMES
prodigal(
    input  = d('final_contigs/contigs.fa'),
    out    = d('orfs/predicted_orfs') # prefix*
)

# create table connecting seed and subsystems
# seed_sequence_number -> system;subsystem;subsubsystem;enzyme
# use this later to make functions tables
prepare_seed(
    seed = 'db/seed.fasta',
    peg  = 'db/subsystems2peg',
    role = 'db/subsystems2role',
    out  = 'db/seed_ss.txt'
)
 
## IDENTIFY ORFS WITH PHMMER
phmmer( 
    query = d('orfs/predicted_orfs.faa'),
    db    = 'db/seed.fasta',
    out   = d('anno/proteins.txt')
)

# flatten phmmer file (we only need top hit)
run('misc/flatten_phmmer.py anno/proteins.txt.table > anno/proteins_flattened.txt')

## GET ORF COVERAGE

# reference assemble
reference_assemble( # clc specific
    query     = 'reads.fasta',
    reference = d('orfs/predicted_orfs.fna'),
    out       = d('refs/reads_versus_orfs.txt')
)

# make coverage table
make_coverage_table( # clc specific
    reads     = 'reads.fasta',
    reference = d('orfs/predicted_orfs.fna'),
    clc_table = d('refs/reads_versus_orfs.txt'),
    phmmer    = d('anno/proteins_flat.txt'),
    out       = d('tables/orfs_coverage.txt')
)

# make subsystems table from coverage table
make_subsystems_table(
    reads          = 'data/reads.fasta',
    subsnames      = 'db/seed_ss.txt',
    coverage_table = d('tables/orfs_coverage.txt'),
    out            = d('tables/subsystems_coverage.txt')
)

# ## GET OTU COVERAGE
reference_assemble(
    query     = 'reads.txt',
    reference = 'db/taxcollector.fa',
    out       = d('refs/reads_vs_taxcollector.txt'),
)

make_coverage_Table(
    reads = 'reads.fasta',
    reference = d('db/taxcollector.fa'),
    clc_table = d('refs/16s_table.txt')
)

# TODO make OTU abundancy matrices
# *NOTE I should just make those scripts part of
# taxcollector :\

# estimate average genome size and use to normalize?

# make_subsystems_table()
# make_phylogeny_table()
