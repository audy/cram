#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from glob import glob

from metacram import *

target_directory = sys.argv[1]
out = 'out'
d = get_outdir(os.path.join(target_directory, out))

ohai('output: %s' % d(''))

ohai('ILLUMINA PIPELINE: %s' % target_directory)

left_mates = glob('data/left*')
right_mates = glob('data/right*')

for i, j in zip(left_mates, right_mates):
    ohai('%s + %s' % (i, j))

read_format = 'qseq' # fastq, fasta, qseq
alignment = 'blast' # blast, phmmer
kmer_lengths = [21, 31, 51, 71] # for assembling
final_kmer_length = 31

# location of databases
db = {
    'tc_seed': '~/cram/db/tc_seed.fasta',
    'taxcollector': '~/cram/db/taxcollector.fa',
}

# expand tilde to home directory
for k in db:
    db[k] = os.path.expanduser(db[k])

# Define how to filter taxonomic matches
phylo = {
    'phylum': { 'num': 2, 'sim': 0.80 },
    'genus': { 'num': 8, 'sim': 0.95 },
}

ohai('running pipeline!')

## MAKE DIRECTORIES
[ run('mkdir -p %s' % i) for i in [
    d(''),
    d('orfs'),
    d('anno'),
    d('refs'),
    d('tables'),
    d('trimmed') ] ]

## TRIM PAIRS BASED ON QUALITY SCORES
counts = trim_pairs(
    left_mates   = [ open(i) for i in left_mates ],
    right_mates  = [ open(i) for i in right_mates ],
    input_format = read_format,
    out_left     = d('trimmed/singletons_left.fastq'),
    out_right    = d('trimmed/singletons_right.fastq'),
    out          = d('trimmed/reads_trimmed.fastq'),
    cutoff       = 70
)

## ASSEMBLE WITH VELVET
for k in kmer_lengths:
    velvet(
        reads = [
            ('fastq', 'shortPaired', d('trimmed/reads_trimmed.fastq')),
            ('fastq', 'short', d('trimmed/singletons_left.fastq')),
            ('fastq', 'short', d('trimmed/singletons_right.fastq'))
        ],
        outdir = d('contigs_%s' % k),
        k      = k
    )

# run final assembly
velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmer_lengths],
    outdir   = d('contigs_final'),
    k        = final_kmer_length
)

## PREDICT OPEN READING FRAMES
prodigal(
    input  = d('contigs_final/contigs.fa'),
    out    = d('orfs/predicted_orfs')
)

## SPLIT ORF FILES
split_fasta(
    infile  = d('orfs/predicted_orfs.faa'),
    out_dir = d('orfs/split/'),
    n       = 1000,
)

## IDENTIFY ORFS WITH PHMMER or BLAST
for q in glob(d('orfs/split/*.faa')):
    if alignment == 'phmmer':
        phmmer(
            query = q,
            db    = db['tc_seed'],
            out   = d('anno/proteins.%s.txt' % q)
        )
    elif alignment == 'blast':
        blastp(
            query = q,
            db    = db['tc_seed'],
            out   = d('anno/proteins.%s.txt' % q)
        )

## GET ORF COVERAGE using SMALT

# reference assemble trimmed reads against ORFs
left, right, paired = d('trimmed/singletons_left.fastq'), d('trimmed/singletons_right.fastq'), d('trimmed/reads_trimmed.fastq')

# index predicted orfs

smalt_index(
    reference = d('orfs/predicted_orfs.fna'),
    name      = d('orfs/predicted_orfs') # prefix*
)

for r in glob(d('trimmed/*.fastq')):
    ohai('smalt mapping %s' % r)
    smalt_map(
        query     = r,
        reference = d('orfs/predicted_orfs'),
        out       = d('refs/%s_vs_orfs.cigar' % os.path.basename(r)),
        identity  = 0.80
    )

ohai('combining SMALT tables')
run('cat %s > %s' % (d('refs/*.cigar'), d('refs/combined.txt')), generates=d('refs/combined.txt'))

quit()

smalt_coverage_table(
    assembly = d('refs/combined.txt'),
    out      = d('tables/%s_seed_coverage.txt' % os.path.basename(o))
)

# concatenate coverage tables


# concatenate assembly coverage tables
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

## GET OTU COVERAGE
ohai('building index of taxcollector database')
smalt_index(
    reference = db['taxcollector'], 
    name      = '~/cram/db/taxcollector'
)

# reference assemble
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