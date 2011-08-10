#!/usr/bin/env python

from pipe import *
from glob import glob

ohai('concatenate all files in data/* and de novo assemble at k={31, 51, 71}, and then all contigs at 51')

run('mkdir -p assembly')
d = get_outdir('assembly')

ohai('trimming/concatenating sequences\n')

run('rm -rf %s' % d('reads_trimmed.fastq'))

for reads in glob('data/*.fastq'):
    sequences = (r for r in Dna(open(reads), type='fastq'))
    trimmed = (Trim.trim(r) for r in sequences)

    # filter by minimum length (no need for this w/ Velvet?)
    trimmed = (i for i in trimmed if len(i) > 70)

    with open(d('reads_trimmed.fastq'), 'a') as handle:
        for t in trimmed:
            print >> handle, t.fastq

kmers = {
     31: d('contigs_31'),
     51: d('contigs_51'),
     71: d('contigs_71')
}

for kmer in kmers:
    velvet(
        reads  = [('fastq', 'short', d('reads_trimmed.fastq'))],
        outdir = kmers[kmer],
        kmer   = kmer
    )
    
# run final assembly
velvet(
    reads    = [('fasta', 'long', d('contigs_%s/contigs.fa' % k)) for k in kmers],
    outdir   = d('final_contigs'),
    kmer     = 51
)