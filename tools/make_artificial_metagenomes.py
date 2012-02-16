#!/usr/bin/env python

# Austin G. Davis-Richardson
# harekrishna@gmail.com

import sys
import random
import math
import os
from glob import glob

MU = 200
SIGMA = 100
MIN = 70 # minimum read length
random.seed(42) # for reproducibility

os.system('mkdir -p out')

usage = 'generate.py <total_number_of_reads> <genomes_to_sample_from>'

try:
    # total number of reads
    reads   = int(sys.argv[1])
    # total number of genomes to sample from
    no_genomes = int(sys.argv[2])
except IndexError:
    print >> sys.stderr, usage
    quit(-1)


# fasta file containing all genomes
genomes = glob('data/*/*.fna')
random.shuffle(genomes)

print "%s reads, %s genomes from %s total genomes" % (reads, no_genomes, len(genomes))

genomes = genomes[:no_genomes + 1]

# figure out how many reads per genome to get by doing random sampling
# with replacement.
# TODO this is a flat distribution. Experiment with others?
genomes = sorted( random.choice(genomes) for i in range(0, reads) )

# iterate over genomes, getting random reads, outputting into
# corresponding fasta files in out/
for genome in set(genomes):
    n = genomes.count(genome)
    print genome, n
    name = os.path.basename(genome).replace('/','_')
    
    with open(genome) as handle, open('out/%s' % name, 'w') as output:
        handle.next()
        
        # load DNA sequence into a big ol' string
        chromosome = ''.join([ i.strip() for i in handle ])
        
        # start making reads
        for i in range(0, n):
            # get start coordinate of read
            # XXX what's the distribution of the random numbers generated
            #     by the Blum Blum Shub algorithm?
            start = random.randint(0, len(chromosome)) - MU
            
            # get length of read using Gaussian distribution
            while True:
                length = int(math.fabs(random.gauss(mu=MU, sigma=SIGMA)))
                read = chromosome[start:start+length]
                if len(read) != MIN: # read is long enough, keep it
                    break
            
            # output read
            print >> output, '>%s\n%s' % (i, read)
