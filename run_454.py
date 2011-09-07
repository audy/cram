#!/usr/bin/env python
# encoding: utf-8

import os
from pipe import *
from glob import glob

# shorten names a bit
cutoff = 70
out    = 'out'
reads  = glob('data/*')[0]

# Creates a simple function to prepend the output directory
# to the directory/filename you specify
d = get_outdir('out')

ohai('running pipeline!')

## MAKE DIRECTORIES
[ run('mkdir -p %s' % i, generates=i) for i in [
    out,
    d('orfs'),
    d('anno'),
    d('refs'),
    d('tables') ] ]

## TRIM READS
if not os.path.exists(d('reads_trimmed.fasta')):
    ohai('trimming sequences')
    sequences = (r for r in Dna(open(reads), type='fastq'))
    trimmed = (Trim.trim(r) for r in sequences)

    # filter by minimum length (no need for this w/ Velvet?)
    trimmed = (i for i in trimmed if len(i) > cutoff)
 
    with open(d('reads_trimmed.fasta'), 'w') as handle:
        for t in trimmed:
            print >> handle, t.fasta
else:
    ohai('trimming sequences [skipping]')

# ASSEMBLE W/ VELVET
kmers = {
     31: d('contigs_31'),
     51: d('contigs_51'),
     71: d('contigs_71')
}

for k in kmers:
    velvet(
        reads  = [('fasta', 'short', d('reads_trimmed.fasta'))],
        outdir = kmers[k],
        k      = kmer
    )
    
# run final assembly
velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('contigs_final'),
    k        = 51
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
run('misc/flatten_phmmer.py %s > %s' % (
    d('anno/proteins.txt.table'),
    d('anno/proteins_flattened.txt')),
    generates=d('anno/proteins_flattened.txt'))

## GET ORF COVERAGE

# reference assemble
reference_assemble( # clc specific
    query     = d('reads_trimmed.fasta'),
    reference = d('orfs/predicted_orfs.fna'),
    out       = d('refs/reads_versus_orfs.txt')
)

# make coverage table
make_coverage_table( # clc specific
    reads     = d('reads_trimmed.fasta'),
    reference = d('orfs/predicted_orfs.fna'),
    clc_table = d('refs/reads_versus_orfs.txt'),
    phmmer    = d('anno/proteins_flattened.txt'),
    out       = d('tables/orfs_coverage.txt')
)

# make subsystems table from coverage table
# TODO split up into 4 hierarchy tables
make_subsystems_table(
    reads          = d('reads_trimmed.fasta'),
    subsnames      = 'db/seed_ss.txt',
    coverage_table = d('tables/orfs_coverage.txt'),
    out            = d('tables/subsystems_coverage.txt')
)

# GET OTU COVERAGE
reference_assemble(
    query     = d('reads_trimmed.fasta'),
    reference = 'db/taxcollector.fa',
    out       = d('refs/reads_vs_taxcollector.txt'),
)

make_otu_coverage_table(
    reads     = d('reads_trimmed.fasta'),
    reference = 'db/taxcollector.fa',
    clc_table = d('refs/reads_vs_taxcollector.txt'),
    out       = d('tables/otu_coverage.txt'),
)
