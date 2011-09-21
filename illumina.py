#!/usr/bin/env python
# encoding: utf-8

# location of left and right mate pairs
left_mates = 'data/s71.qseq'
right_mates = 'data/s73.qseq'

# BEGIN:

from pipe import *
from glob import glob

ref = 'SMALT' # 'CLC'
out = 'out'

# check if user ran make    
if not os.path.exists('bin'):
    ohno('bin/ doesn\'t exist. Did you run make?')

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
    d('tables') ] ]

## TRIM PAIRS BASED ON QUALITY SCORES
counts = trim_pairs(
    left_mates  = open(left_mates),
    right_mates = open(right_mates),
    out_left    = d('singletons_left.fastq'),
    out_right   = d('singletons_right.fastq'),
    out         = d('reads_trimmed.fastq'),
    cutoff      = 70
)

## ASSEMBLE WITH VELVET
# 3 sub assemblies:
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

## IDENTIFY ORFS WITH PHMMER
phmmer( 
    query = d('orfs/predicted_orfs.faa'),
    db    = 'db/seed.fasta',
    out   = d('anno/proteins.txt')
)

# flatten phmmer file (we only need top hit)
run('misc/flatten_phmmer.py out/anno/proteins.txt.table > out/anno/proteins_flat.txt',
    generates='out/anno/proteins_flat.txt')

## GET ORF COVERAGE using CLC

# create table connecting seed and subsystems
# seed_sequence_number -> system;subsystem;subsubsystem;enzyme
# use this later to make functions tables

if ref == 'CLC':
    # reference assemble
    clc_reference_assemble( # clc specific
        reference = d('orfs/predicted_orfs.fna'),
        out       = d('refs/reads_versus_orfs.txt'),
        query     = [
            ('unpaired', d('reads_trimmed.fastq')),
            ('unpaired', d('singletons_left.fastq')),
            ('unpaired', d('singletons_right.fastq'))
        ]
    )

    # make coverage table (clc)
    clc_coverage_table(
        reference = d('orfs/predicted_orfs.fna'),
        clc_table = d('refs/reads_versus_orfs.txt'),
        phmmer    = d('anno/proteins_flat.txt'),
        out       = d('tables/orfs_coverage.txt')
    )

elif ref == 'SMALT':
    # index reference database
    smalt_index(
        reference = d('orfs/predicted_orfs.fna'),
        name      = d('orfs/predicted_orfs')
    )
    
    # reference assemble
    queries = glob('out/*.fastq') 
    for q in queries:
        ohai('smalt mapping %s' % q)
        smalt_map(
            query     = q,
            reference = d('orfs/predicted_orfs'),
            out       = d('refs/%s.cigar' % os.path.basename(q)),
            identity  = 0.80
        )
        
        ohai('coverage table %s' % q)
        # make coverage table
        smalt_coverage_table(
            assembly = d('refs/%s.cigar' % os.path.basename(q)),
            phmmer   = d('anno/proteins_flat.txt'),
            out      = d('tables/%s_coverage.txt' % os.path.basename(q))
        )

    # concatenate assembly coverage tables
    ohai('concatenating assembly coverage tables')
    
    # TODO make this nicer:
    coverage_tables = [ d('tables/%s' % i) for i in [
        'singletons_left.fastq_coverage.txt',
        'singletons_right.fastq_coverage.txt',
        'reads_trimmed.fastq_coverage.txt',
        ]]
    
    run('cat %s > %s' % \
        (' '.join(coverage_tables), d('tables/SMALT_orfs_coverage.txt')),
        generates=d('tables/SMALT_orfs_coverage.txt')
    )

prepare_seed(
    seed = 'db/seed.fasta',
    peg  = 'db/subsystems2peg',
    role = 'db/subsystems2role',
    out  = 'db/seed_ss.txt'
)

subsystems_table(
    subsnames      = 'db/seed_ss.txt',
    coverage_table = d('tables/%s_orfs_coverage.txt' % ref),
    out            = d('tables/%s_subsystems_coverage.txt' % ref),
    reads_type     = 'fastq',
    total_reads   = total_reads,
)

## GET OTU COVERAGE
if ref == 'CLC':    
    clc_reference_assemble(
        reference = 'db/taxcollector.fa',
        out       = d('refs/reads_vs_taxcollector.txt'),
        query     = [
            ('unpaired', d('reads_trimmed.fastq')),
            ('unpaired', d('singletons_left.fastq')),
            ('unpaired', d('singletons_right.fastq')) ],
    )

    # Filter CLC output
    [ clc_filter(
        assembly   = d('refs/reads_vs_taxcollector.txt.clc'),
        similarity = phylo[p]['sim'],
        length     = 0.80,
        out        = d('refs/%s.clc' % p)
    ) for p in phylo ]

    # Convert from CLC table to text-file
    [ clc_assembly_table(
        input  = d('refs/%s.clc' % p),
        out    = d('refs/%s.txt' % p)
    ) for p in phylo ]

    # Make coverage table (at a certain level)
    [ clc_make_otu_coverage_table(
        reference    = 'db/taxcollector.fa',
        clc_table    = d('refs/%s_reads_vs_taxcollector.txt' % ref),
        reads_format = 'fastq',
        out          = d('tables/%s_%s.txt' % (ref, p)),
        level        = phylo[p]['num']
    ) for p in phylo ]
    
elif ref == 'SMALT':
    pass
