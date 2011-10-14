#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from glob import glob

from metacram import *

def init(args):
    ''' create a project '''
    
    directory = args['directory']
    
    # create directory
    if os.path.exists(directory):
        print >> sys.stderr, "%s exists. Move or delete yourself" % directory
        quit(-1)
    os.mkdir(directory)
    
    script_file = '%s/illumina.py' % directory
    
    # copy this file to that directory
    with open(script_file, 'w') as output:
        # This is bound to cause problems
        # but I don't want to write the byte encoded program
        # TODO find another way
        with open(__file__.replace('.pyc', '.py')) as handle:
            output.write(handle.read())
            
    ohai('project created in %s' % directory)
    ohai('executable: %s' % script_file)
    

def run(**args):
    ''' the actual pipeline '''
    left_mates = args['left_mates'] # glob('data/left*')
    right_mates = args['right_mates'] # glob('data/right*')
    
    out = args.get('out', 'out')
    read_format = args.get('read_format')
    
    # location of databases
    db = args.get('db',{
        'seed': '~/cram/db/seed.fasta',
        'taxcollector': '~/cram/db/taxcollector.fa',
        'subsystems2peg': '~/cram/db/subsystems2peg',
        'subsystems2role': '~/cram/db/subsystems2role',
        'seed_ss': '~/cram/db/seed_ss.txt',
    })
    
    # name of reference assembler
    # (CLC used to be supported)
    ref = 'SMALT'
    
    # expand tilde to home directory
    for k in db:
        db[k] = os.path.expanduser(db[k])

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
        d('tables'),
        d('trimmed') ] ]

    ## TRIM PAIRS BASED ON QUALITY SCORES
    counts = trim_pairs(
        left_mates   = [ open(i) for i in left_mates ],
        right_mates  = [ open(i) for i in right_mates ],
        input_format = READ_FORMAT,
        out_left     = d('trimmed/singletons_left.fastq'),
        out_right    = d('trimmed/singletons_right.fastq'),
        out          = d('trimmed/reads_trimmed.fastq'),
        cutoff       = 70
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
            ('fastq', 'shortPaired', d('trimmed/reads_trimmed.fastq')),
            ('fastq', 'short', d('trimmed/singletons_left.fastq')),
            ('fastq', 'short', d('trimmed/singletons_right.fastq'))
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
        db    = db['seed'],
        out   = d('anno/proteins.txt')
    )

    # flatten phmmer file (we only need top hit)
    run('misc/flatten_phmmer.py out/anno/proteins.txt.table > out/anno/proteins_flat.txt',
        generates='out/anno/proteins_flat.txt')

    ## GET ORF COVERAGE using CLC

    # create table connecting seed and subsystems
    # seed_sequence_number -> system;subsystem;subsubsystem;enzyme
    # use this later to make functions tables
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
        seed = db['seed'],
        peg  = db['subsystems2peg'],
        role = db['subsystems2role'],
        out  = db['seed_ss']
    )

    subsystems_table(
        subsnames      = db['seed_ss'],
        coverage_table = d('tables/%s_orfs_coverage.txt' % ref),
        out            = d('tables/%s_subsystems_coverage.txt' % ref),
        reads_type     = 'fastq',
    )

    ## GET OTU COVERAGE
    ohai('building index of taxcollector database')
    smalt_index(
        reference = db['taxcollector'], 
        name      = '~/cram/db/taxcollector'
    )

    # reference assemble
    queries = glob('out/*.fastq') 
    for q in queries:
        ohai('smalt mapping %s' % q)
        smalt_map(
            query     = q,
            reference = '~/cram/db/taxcollector',
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
    ohai('concatenating OTU coverage tables')
    run('cat %s > %s' % \
        (' '.join(coverage_tables), d('tables/SMALT_otu_coverage.txt')),
        generates=d('tables/SMALT_otu_coverage.txt')
    )

if __name__ == '__main__':
    # default parameters
    # should replace this with test.
    run(
        left_mates  = glob('data/left*'),
        right_mates = glob('data/right*'),
        read_format = 'qseq'
    )