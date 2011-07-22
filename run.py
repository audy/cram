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

ohai('running pipeline!')

dirs = [
    out,
    out + '/orfs',
    out + '/anno',
    out + '/refs']

[ run('mkdir -p %s' % i) for i in dirs ]

# Trim Reads
sequences = (r for r in Dna(open(reads), type='fastq'))
trimmed = (Trim.trim(r) for r in sequences)
trimmed = (i for i in trimmed if len(i) > cutoff)

with open(out + '/reads_trimmed.txt', 'w') as handle:
    for t in trimmed:
        print >> handle, t.fasta

# assemble with velvet

kmers = {
    35: out + '/contigs_35',
    45: out + '/contigs_45',
    55: out + '/contigs_55'
}

for kmer in kmers:
    velvet(
        reads  = out + '/reads_trimmed.txt',
        outdir = kmers[kmer],
        kmer   = kmer
    )

# concatenate all contigs
run('cat %s > %s' % (
    ' '.join(i + '/Sequences' for i in kmers.values()),
    out + '/joined_contigs.txt')
)

# run final assembly
velvet(
    reads    = out + '/joined_contigs.txt',
    outdir   = out + '/final_contigs',
    kmer     = 35
)

# predict ORFs
prodigal(
    input  = out + '/final_contigs/Sequences',
    out    = out + '/orfs/predicted_orfs' # prefix*
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

# identify ORFs using phmmer
phmmer(
    query = out + '/orfs/predicted_orfs.faa',
    db    = 'db/seed.fasta',
    out   = out + '/anno/proteins.txt'
)

# obtain coverage of ORFs
orf_coverage = reference_assemble(
    query = 'reads.txt',
    db    = out + '/orfs/predicted_orfs.ffn',
    out   = out + '/refs/reads_versus_orfs.txt'
)

# separate unidentified ORFs
# these get clustered at 40% AA identity using cd-hit
get_unidentified_orfs(
    orfs     = out + '/predicted_orfs.ffn',
    proteins = out + '/identified_proteins.txt',
    out      = out + '/unidentified_orfs.ffn'
)

# align reads to taxcollector
reference_assemble(
    query = 'reads.txt',
    db    = 'db/taxcollector.fa',
    out   = out + '/reads_vs_taxcollector.txt'
)

# estimate average genome size and use to normalize?

# make_subsystems_table()
# make_phylogeny_table()