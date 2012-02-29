#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from glob import glob
from metacram import *


# SETTINGS
read_format = 'fastq'
left_mates  = glob('data/*_left.%s' % read_format)
right_mates = glob('data/*_right.fastq' % read_format)
out_dir     = 'out'

# LOCATIONS OF DATABASES
db = {
    'taxcollector':    '~/cram/db/taxcollector.fa',
    'tc_seed':         '~/cram/db/tc_seed.fasta',
}

# DEFINE HOW TO FILTER TAXONOMY DESCRIPTIONS
# num is the number in the header of the RDP database
# that corresponds to the taxonomic level, (2 for phylum, 8 for genus)
# sim is the percent similarity to filter.
phylo = {
    'phylum': { 'num': 2, 'sim': 0.80 },
    'genus': { 'num': 8, 'sim': 0.95 },
}

#################################################################
##################### THE ACTUAL PIPELINE #######################
#################################################################

##
# PREPARATIONS
#

# Expand tidle to full path in database directories
for k in db:
    db[k] = os.path.expanduser(db[k])

# Creates a simple function to prepend the output directory
# to the directory/filename you specify
d = get_outdir(out)

ohai('running pipeline!')

directories = [
    out,
    d('orfs'),
    d('anno'),
    d('refs'),
    d('tables'),
    d('trimmed'),
]

## MAKE DIRECTORIES
for d in directories:
    run('mkdir -p %s' % i, generates=i)

##
# QUALITY CONTROL
#

# TRIM PAIRS BASED ON QUALITY SCORES
counts = trim_pairs(
    left_mates   = [ open(i) for i in left_mates ],
    right_mates  = [ open(i) for i in right_mates ],
    input_format = read_format,
    out_left     = d('trimmed/singletons_left.fastq'),
    out_right    = d('trimmed/singletons_right.fastq'),
    out          = d('trimmed/reads_trimmed.fastq'),
    cutoff       = 70
)

##
# ASSEMBLY
#

# 3 sub assemblies:
kmers = {
     21: d('contigs_21')
     31: d('contigs_31'),
     51: d('contigs_51'),
     71: d('contigs_71')
}

for k in kmers:
    velvet(
        reads = [
            ('fastq', 'shortPaired', d('trimmed/reads_trimmed.fastq')),
            ('fastq', 'short', d('trimmed/singletons_left.fastq')),
            ('fastq', 'short', d('trimmed/singletons_right.fastq'))
        ],
        outdir = kmers[k],
        k      = k
    )

## YOU MAY WANT TO STOP HERE AND CHECK YOUR ASSEMBLY!
# quit()

# run final assembly
velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('contigs_final'),
    k        = 51
)

##
# Functional Analysis
#

## PREDICT OPEN READING FRAMES
prodigal(
    input  = d('contigs_final/contigs.fa'),
    out    = d('orfs/predicted_orfs') # prefix*
)

## IDENTIFY ORFS WITH PHMMER
phmmer( 
    query = d('orfs/predicted_orfs.faa'),
    db    = db['seed'],
    out   = d('anno/proteins.txt')
)

## IDENTIFY ORFS WITH BLASH
## TODO

# FLATTEN PHMMER OUTPUT TO GET ONLY BEST HIT
run('misc/flatten_phmmer.py out/anno/proteins.txt.table > out/anno/proteins_flat.txt',
    generates='out/anno/proteins_flat.txt')

## GET ORF COVERAGE USING SMALT
smalt_index(
    reference = d('orfs/predicted_orfs.fna'),
    name      = d('orfs/predicted_orfs')
)

# REFERENCE ASSEMBLE WITH SMALT
# TODO we need to do fancy stuff with paired-end reads!
queries = glob('out/*.fastq') 
for q in queries:
    ohai('smalt mapping %s' % q)
    smalt_map(
        query     = q,
        reference = d('orfs/predicted_orfs'),
        out       = d('refs/%s_vs_orfs.cigar' % os.path.basename(q)),
        identity  = 0.80
    )

    ohai('coverage table %s' % q)
    # make coverage table
    smalt_coverage_table(
        assembly = d('refs/%s_vs_orfs.cigar' % os.path.basename(q)),
        phmmer   = d('anno/proteins_flat.txt'),
        out      = d('tables/%s_seed_coverage.txt' % os.path.basename(q))
    )

# CONCATENATE ASSEMBLY COVERAGE TABLES
ohai('concatenating assembly coverage tables')

# TODO make this nicer:
coverage_tables = glob(d('tables/*_seed_coverage.txt'))

run('cat %s > %s' % \
    (' '.join(coverage_tables), d('tables/SMALT_orfs_coverage.txt')),
    generates=d('tables/SMALT_orfs_coverage.txt')
)

subsystems_table(
    subsnames      = db['seed_ss'],
    coverage_table = d('tables/orfs_coverage.txt'),
    out            = d('tables/subsystems_coverage.txt'),
    reads_type     = 'fastq',
)

##
# PHYLOGENETIC ANALYSIS
#

# GET OTU COVERAGE
ohai('building index of taxcollector database')
smalt_index(
    reference = db['taxcollector'], 
    name      = '~/cram/db/taxcollector'
)

# REFERENCE ASSEMBLE AGAINST TAXCOLLECTOR
queries = glob('out/*.fastq') 
for q in queries:
    ohai('smalt mapping %s' % q)
    smalt_map(
        query     = q,
        reference = '~/cram/db/taxcollector',
        out       = d('refs/%s_vs_taxcollector.cigar' % os.path.basename(q)),
        identity  = 0.80
    )

    ohai('coverage table %s' % q)
    # make coverage table
    smalt_coverage_table(
        assembly = d('refs/%s_vs_taxcollector.cigar' % os.path.basename(q)),
        out      = d('tables/%s_otu_coverage.txt' % os.path.basename(q))
    )

coverage_tables = glob(d('tables/*_otu_coverage.txt'))
ohai('concatenating OTU coverage tables')
run('cat %s > %s' % \
    (' '.join(coverage_tables), d('tables/otu_coverage.txt')),
    generates=d('tables/SMALT_otu_coverage.txt')
)