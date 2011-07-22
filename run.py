#!/usr/bin/env python
# encoding: utf-8

from pipe import *

# Define configuration:
# TODO: read this from a config file? options?
class Config:
    cutoff = 70
    out    = 'out'
    reads  = 'reads.txt'

# shorten names a bit
cutoff = Config.cutoff
out    = Config.out
reads  = Config.reads

# Creates a simple function to prepend the output directory
# to the directory/filename you specify
d = get_outdir(Config.out)

ohai('running pipeline!')

## MAKE DIRECTORIES
dirs = [
    out,
    d('orfs'),
    d('anno'),
    d('refs')]

[ run('mkdir -p %s' % i) for i in dirs ]

## TRIM READS
sequences = (r for r in Dna(open(reads), type='fastq'))
trimmed = (Trim.trim(r) for r in sequences)
trimmed = (i for i in trimmed if len(i) > cutoff)

with open(out + '/reads_trimmed.txt', 'w') as handle:
    for t in trimmed:
        print >> handle, t.fasta

## ASSEMBLE W/ VELVET
kmers = {
    35: d('contigs_35'),
    45: d('contigs_45'),
    55: d('contigs_55')
}

for kmer in kmers:
    velvet(
        reads  = d('reads_trimmed.txt'),
        outdir = kmers[kmer],
        kmer   = kmer
    )

# concatenate all contigs
run('cat %s > %s' % (
    ' '.join(i + '/Sequences' for i in kmers.values()),
    d('joined_contigs.txt'))
)

# run final assembly
velvet(
    reads    = d('joined_contigs.txt'),
    outdir   = d('final_contigs'),
    kmer     = 35
)

## PREDICT OPEN READING FRAMES
prodigal(
    input  = d('final_contigs/Sequences'),
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

## GET ORF COVERAGE
orf_coverage = reference_assemble(
    query = 'reads.txt',
    db    = d('orfs/predicted_orfs.ffn'),
    out   = d('refs/reads_versus_orfs.txt')
)

# separate unidentified ORFs
# these get clustered at 40% AA identity using cd-hit
get_unidentified_orfs(
    orfs     = d('predicted_orfs.ffn'),
    proteins = d('identified_proteins.txt'),
    out      = d('unidentified_orfs.ffn')
)

# align reads to taxcollector
reference_assemble(
    query = 'reads.txt',
    db    = 'db/taxcollector.fa',
    out   = d('reads_vs_taxcollector.txt')
)

# estimate average genome size and use to normalize?

# make_subsystems_table()
# make_phylogeny_table()