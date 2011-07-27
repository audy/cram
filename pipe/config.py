# Define configuration:
# TODO: read this from a config file? options?

from glob import glob
import os

class Config:
    cutoff = 70
    out    = 'out'
    reads  = glob('data/*.fastq')
    
    if type(reads) == list:
        reads = reads[0]
        
    if not os.path.exists(reads):
        ohno('%s does not exist!' % reads)

    assert type(reads) == str
