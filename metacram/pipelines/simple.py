#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from glob import glob

from metacram import *

''' the actual pipeline '''
args = {}
out = args.get('out', 'out')
reads  = glob('data/*')[0]
read_format = args.get('read_format', 'fastq')

# location of databases
db = {
    'tc_seed': '~/cram/db/tc_seed.fasta',
    'taxcollector': '~/cram/db/taxcollector.fa',
}


# expand tilde to home directory
for k in db:
    db[k] = os.path.expanduser(db[k])

# Creates a simple function to prepend the output directory
# to the directory/filename you specify
d = get_outdir(out)

# Define how to filter taxonomic matches
phylo = {
    'phylum': { 'num': 2, 'sim': 0.80 },
    'genus': { 'num': 8, 'sim': 0.95 },
}

ohai('running pipeline!')

## MAKE DIRECTORIES
[ run('mkdir -p %s' % i) for i in [
    out,
    d('orfs'),
    d('anno'),
    d('refs'),
    d('tables'),
    d('trimmed') ] ]

## TRIM READS
if not os.path.exists(d('trimmed/reads_trimmed.fasta')):
    ohai('trimming sequences')
    sequences = (r for r in Dna(open(reads), type='fastq'))
    trimmed = (Trim.trim(r) for r in sequences)

    # filter by minimum length (no need for this w/ Velvet?)
    trimmed = (i for i in trimmed if len(i) > 70)

    with open(d('trimmed/reads_trimmed.fasta'), 'w') as handle:
        for t in trimmed:
            print >> handle, t.fasta
else:
    ohai('trimming sequences [skipping]')

## ASSEMBLE WITH VELVET
# 3 sub assemblies:
kmers = {
     31: d('contigs_31'),
     51: d('contigs_51'),
     71: d('contigs_71')
}

[ velvet(
    reads = [
        ('fasta', 'short', d('trimmed/reads_trimmed.fasta')),
    ],
    outdir = kmers[k],
    k      = k
) for k in kmers ]

# run final assembly
velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('contigs_final'),
    k        = 51
)

## PREDICT OPEN READING FRAMES
prodigal(
    input  = d('contigs_final/contigs.fa'),
    out    = d('orfs/predicted_orfs') # prefix*
)

## IDENTIFY ORFS WITH BLASTP
# misbehaving ! just assume someone ran it already.
# formatdb(database = db['tc_seed'])
blastp( 
  query = d("orfs/predicted_orfs.faa"),
  database =db['tc_seed'],
  out = d('anno/blast.txt' % os.path.basename(i)),
  evalue = 0.00001,
  threads = 24,
)


## GET ORF COVERAGE using CLC
# index reference database
ohai('indexing orfs')
smalt_index(
    reference = d('orfs/predicted_orfs.fna'),
    name      = d('orfs/predicted_orfs')
)

# reference assemble
ohai('smalt mapping reads to orfs')
smalt_map(
    query     = reads,
    reference = d('orfs/predicted_orfs'),
    out       = d('refs/reads_vs_orfs.cigar'),
    identity  = 0.80
)

ohai('coverage table: reads vs orfs')
# make coverage table
smalt_coverage_table(
    assembly = d('refs/reads_vs_orfs.cigar'),
    blast    = d('anno/blast.txt'),
    out      = d('tables/orfs_coverage.txt'),
    seed     = '~/cram/db/tc_seed.fasta'
)

# concatenate assembly coverage tables
ohai('concatenating assembly coverage tables')
