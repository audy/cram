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

# Define how to filter taxonomic matches
phylo = {
    'phylum': { 'num': 2, 'sim': 0.80 },
    'genus': { 'num': 8, 'sim': 0.95 },
}

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
    left_mates  = open(left_mates),
    right_mates = open(right_mates),
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

[ velvet(
    reads = [
        ('fastq', 'shortPaired', d('reads_trimmed.fastq')),
        ('fastq', 'short', d('singletons_left.fastq')),
        ('fastq', 'short', d('singletons_right.fastq'))
    ],
    outdir = kmers[k],
    k      = k
) for k in kmers ]

# run final assembly
# type of assembly depends on whether or not contigs from first
# 3 assemblies are actually long.

velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('contigs_final'),
    k        = 51
)

# PREDICT OPEN READING FRAMES
prodigal(
    input  = d('contigs_final/contigs.fa'),
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
run('misc/flatten_phmmer.py out/anno/proteins.txt.table > out/anno/proteins_flat.txt',
    generates='out/anno/proteins_flat.txt')

## GET ORF COVERAGE

# reference assemble
reference_assemble( # clc specific
    reference = d('orfs/predicted_orfs.fna'),
    out       = d('refs/reads_versus_orfs.txt'),
    query     = [
        ('unpaired', d('reads_trimmed.fastq')),
        ('unpaired', d('singletons_left.fastq')),
        ('unpaired', d('singletons_right.fastq')) ],
)

# make coverage table
make_coverage_table( # clc specific
    reference = d('orfs/predicted_orfs.fna'),
    clc_table = d('refs/reads_versus_orfs.txt'),
    phmmer    = d('anno/proteins_flat.txt'),
    out       = d('tables/orfs_coverage.txt'),
)

# make subsystems table from coverage table
make_subsystems_table(
    subsnames      = 'db/seed_ss.txt',
    coverage_table = d('tables/orfs_coverage.txt'),
    out            = d('tables/subsystems_coverage.txt'),
    reads_type     = 'fastq',
    reads          = [
        d('reads_trimmed.fastq'),
        d('singletons_left.fastq'),
        d('singletons_right.fastq')
    ],
)

# GET OTU COVERAGE
reference_assemble(
    reference = 'db/taxcollector.fa',
    out       = d('refs/reads_vs_taxcollector.txt'),
    query     = [
        ('unpaired', d('reads_trimmed.fastq')),
        ('unpaired', d('singletons_left.fastq')),
        ('unpaired', d('singletons_right.fastq')) ],
)

# MAKE OTU COVERAGE TABLES
# Filter CLC output
[ clc_filter(
    assembly   = d('refs/reads_vs_taxcollector.txt.clc'),
    similarity = phylo[p]['sim'],
    length     = 0.80,
    out        = d('refs/%s.clc' % p)
) for p in phylo ]

# Convert from CLC table to text-file
[ assembly_table(
    input  = d('refs/%s.clc' % p),
    out    = d('refs/%s.txt' % p)
) for p in phylo ]

# Make coverage table (at a certain level)
[ make_otu_coverage_table(
    reference    = 'db/taxcollector.fa',
    clc_table    = d('refs/reads_vs_taxcollector.txt'),
    reads_format = 'fastq',
    out          = d('tables/%s.txt' % p),
    level        = phylo[p]['num']
) for p in phylo ]
