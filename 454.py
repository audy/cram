#!/usr/bin/env python
# encoding: utf-8

import os
from pipe import *
from glob import glob

# shorten names a bit
cutoff = 70
out    = 'out'
reads  = glob('data/*')[0]
ref = 'SMALT'

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
    d('tables'),
    d('trimmed') ] ]

## TRIM READS
if not os.path.exists(d('trimmed/reads_trimmed.fasta')):
    ohai('trimming sequences')
    sequences = (r for r in Dna(open(reads), type='fastq'))
    trimmed = (Trim.trim(r) for r in sequences)

    # filter by minimum length (no need for this w/ Velvet?)
    trimmed = (i for i in trimmed if len(i) > cutoff)
 
    with open(d('trimmed/reads_trimmed.fasta'), 'w') as handle:
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
        reads  = [('fasta', 'short', d('trimmed/reads_trimmed.fasta'))],
        outdir = kmers[k],
        k      = k
    )
    
# run final assembly
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
 
## IDENTIFY ORFS WITH PHMMER
phmmer( 
    query = d('orfs/predicted_orfs.faa'),
    db    = 'db/seed.fasta',
    out   = d('anno/proteins.txt')
)

# flatten phmmer file (we only need top hit)
run('misc/flatten_phmmer.py %s > %s' % (
    d('anno/proteins.txt.table'),
    d('anno/proteins_flat.txt')),
    generates=d('anno/proteins_flat.txt'))

## GET ORF COVERAGE
if ref == 'CLC':
    # reference assemble
    clc_reference_assemble( # clc specific
        query     = d('trimmed/reads_trimmed.fasta'),
        reference = d('orfs/predicted_orfs.fna'),
        out       = d('refs/reads_versus_orfs.txt')
    )

    # make coverage table
    clc_coverage_table( # clc specific
        reads     = d('trimmed/reads_trimmed.fasta'),
        reference = d('orfs/predicted_orfs.fna'),
        clc_table = d('refs/reads_versus_orfs.txt'),
        phmmer    = d('anno/proteins_flat.txt'),
        out       = d('tables/orfs_coverage.txt')
    )

    # make subsystems table from coverage table
    # TODO split up into 4 hierarchy tables
    clc_subsystems_table(
        reads          = d('reads_trimmed.fasta'),
        subsnames      = 'db/seed_ss.txt',
        coverage_table = d('tables/orfs_coverage.txt'),
        out            = d('tables/subsystems_coverage.txt')
    )

    # GET OTU COVERAGE
    clc_reference_assemble(
        query     = d('trimmed/reads_trimmed.fasta'),
        reference = 'db/taxcollector.fa',
        out       = d('refs/reads_vs_taxcollector.txt'),
    )

    clc_otu_coverage_table(
        reads     = d('trimmed/reads_trimmed.fasta'),
        reference = 'db/taxcollector.fa',
        clc_table = d('refs/reads_vs_taxcollector.txt'),
        out       = d('tables/otu_coverage.txt'),
    )
    
elif ref == 'SMALT':
    # index reference database
    ohai('indexing orfs')
    smalt_index(
        reference = d('orfs/predicted_orfs.fna'),
        name      = d('orfs/predicted_orfs')
    )
    
    q = d('trimmed/reads_trimmed.fasta')
    
    # reference assemble
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

    # concatenate assembly coverage tables
    ohai('concatenating assembly coverage tables')
    
    # TODO make this nicer:
    coverage_tables = glob(d('tables/*_seed_coverage.txt'))
    
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
)

## GET OTU COVERAGE
if ref == 'CLC':    
    clc_reference_assemble(
        reference = 'db/taxcollector.fa',
        out       = d('refs/reads_vs_taxcollector.txt'),
        query     = [
            ('unpaired', d('trimmed/reads_trimmed.fastq')),
            ('unpaired', d('trimmed/singletons_left.fastq')),
            ('unpaired', d('trimmed/singletons_right.fastq')) ],
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
    # index database
    ohai('indexing taxcollector')
    smalt_index(
        reference = 'db/taxcollector.fa', 
        name      = 'db/taxcollector'
    )
    
    # reference assemble
    q = d('trimmed/reads_trimmed.fasta')

    ohai('smalt mapping %s' % q)
    smalt_map(
        query     = q,
        reference = 'db/taxcollector',
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

    run('cat %s > %s' % \
        (' '.join(coverage_tables), d('tables/SMALT_otu_coverage.txt')),
        generates=d('tables/SMALT_otu_coverage.txt')
    )