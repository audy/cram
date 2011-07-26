#!/usr/bin/env python

# calculate N50 from a fasta file

# N50 = contig length so that half of the contigs are longer and half of the
# contigs are shorter

# If you have R, this script will generate a PDF histogram of the contig lengths.


import commands
import sys
import os

sequence, lengths = [], []
with open(sys.argv[1]) as handle:
  for line in handle:
    if line.startswith('>'):
      lengths.append(len(''.join(sequence)))
      sequence = []
    else:
      sequence += line.strip()
      
      
n50 = sorted(lengths)[len(lengths)/2] # approximately?

print "N50 = %s" % n50

if os.path.exists(commands.getoutput('which r')):
    
    with open('all_lengths.txt', 'w') as handle:
      handle.write('\n'.join(str(i) for i in lengths))

    histogram_calculator = """
    data <- read.csv('all_lengths.txt', header=F)
    hist(as.matrix(data), main='N50 = %s', xlab='length', ylab='frequency')
    abline(v=%s, col='red')
    """ % (n50, n50)

    with open('histogram.r', 'w') as handle:
      handle.write(histogram_calculator)
    
    print commands.getoutput('r --slave < histogram.r')
    print commands.getoutput('rm histogram.r')
    print commands.getoutput(' '.join(['mv', 'Rplots.pdf', os.path.basename(sys.argv[1]) + '.pdf']))