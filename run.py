#!/usr/bin/env python

CUTOFF = 70 # read length cutoff

from pipe import *

run('mkdir -p test_out/')

# Trim Reads
sequences = (r for r in Dna(open('reads.txt'), type='fastq'))
trimmed = (Trim.trim(r) for r in sequences)
trimmed = (i for i in trimmed if len(i) > CUTOFF)

with open('test_out/reads_trimmed.txt', 'w') as handle:
    for t in trimmed:
        print >> handle, t.fasta

# assemble with velvet
kmers = {
    35: 'test_out/contigs_35',
    45: 'test_out/contigs_45',
    55: 'test_out/contigs_55'
}

for kmer in kmers:
    velvet(
        reads  = 'test_out/reads_trimmed.txt',
        outdir = kmers[kmer],
        kmer   = kmer
    )
    


# concatenate all contigs
run('cat %s > %s' % (' '.join(i + '/Sequences' for i in kmers.values()), 'test_out/joined_contigs.txt'))


# run final assembly
velvet(
    reads    = 'test_out/joined_contigs.txt',
    outdir   = 'test_out/final_contigs',
    kmer     = 35
)

# predict ORFs
prodigal(
    input  = 'test_out/final_contigs/Sequences',
    out    = 'test_out/predicted_orfs' # prefix*
)

# identify ORFs using phmmer
phmmer(
    query = 'test_out/predicted_orfs.faa',
    db    = 'db/seed.fasta',
    out   = 'test_out/identified_proteins.txt'
)

quit()

# separate unidentified ORFs
get_unidentified_orfs(
    orfs     = 'test_out/predicted_orfs.ffn',
    proteins = 'test_out/identified_proteins.txt',
    out      = 'test_out/unidentified_orfs.ffn'
)

# obtain coverage of ORFs
orf_coverage = reference_assemble(
    query = 'reads.txt',
    db    = 'predicted_orfs.ffn',
    out   = 'reads_versus_orfs.txt'
)

# obtain coverage of taxonomy
taxonomic_coverage = reference_assemble(
    query = 'unidentified_orfs.txt',
    db    = 'taxcollector.fasta',
    out   = 'orfs_versus_tc.txt'
)

# make_subsystems_table()
# make_phylogeny_table()