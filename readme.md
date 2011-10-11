# CRAM

Comparative Rapid Annotation of Metagenomes

CRAM is a framework for building pipelines for metagenomic annotation.

Pipelines for Illumina and 454 are included.

CRAM is licensed under the GNU GPL v3 Open Source license.

Austin G. Davis-Richardson

## Overview

The pipeline follow these steps.

- Quality Trimming
- _De Novo_ assembly
- Open Reading Frame prediction
- ORF annotation via the SEED database and PHMMER
- ORF coverage estimation by reference assembly
- Subsystem table generation
- 16S rRNA classification using the Ribosomal Database Project 16S rRNA database and TaxCollector.

## Installation

Made for UNIX-like operating systems. Tested with Python 2.7.

To download and install required binaries and database, simply type `make all` in the terminal.

## Usage

CRAM is invoked via the command-line.

### Setting up an experiment

CRAM is meant to be run on one sample at a time. Outputs are then combined to create tables that can be used to perform comparative analysis.

Raw reads go into the `data/` directory. For 454, these reads are expected to be in FASTQ format. For Illumina, they are expected to be in QSEQ format.

The directory structure looks like this:

```
# Main Directory
cram/

# Input
cram/data               # Raw Reads (left.qseq and right.qseq for illumina)
cram/db                 # Databases

# Output
cram/out/               
├── trimmed             # Trimmed reads
├── contigs_31          # contigs at K = 31
├── contigs_51          #                51
├── contigs_71          #                71
├── contigs_final       # Previous assemblies joined, assembled w/ K = 51
├── orfs                # ORF predictions
├── anno                # PHMMER protein annotations
├── refs                # Reference assemblies
└── tables              # Output tables
```

CRAM checks for output files and will skip any steps that have already been completed. If you want to re-do a step, delete the appropriate output directory or file(s).

I suggest making a new CRAM directory for each sample. If you use Git, this can easily be achieved by the command:

`git clone http://github.com/audy/cram.git <experiment-name>`

This will clone a fresh copy of CRAM into your experiment directory. However, the `db/` and `bin/` directories will be empty. Instead of copying these directories (which can be large), use symbolic links.

```bash
ln -s experiment1/db/* exerpiment2/db/*
ln -s experiment1/bin/* experiment2/bin/*
```

This will save space and create consistency between experiments

### Merging Output

Output tables can be merged into Functional and Taxonomic Abundancy Matrices. These matrices can be merged allowing for standardization, normalization, visualization and analysis of results.

There are scripts located in the `misc/` directory to help achieve this.