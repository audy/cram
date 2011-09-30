# CRAM

Comparative Rapid Annotation of Metagenomes

CRAM is a framework for building pipelines for metagenomic annotation. Two pipelines are included for 454 and Illumina generated metagenomes.

CRAM is licensed under the GNU GPL v3 Open Source license.

Austin G. Davis-Richardson

## Overview

The pipelines perform the following steps

- Quality Trimming
- _De Novo_ assembly
- Open Reading Frame prediction
- ORF annotation via the SEED database
- ORF coverage estimation by reference assembly (CLC or SMALT)
- Subsystem table generation
- 16S rRNA comparison (CLC or SMALT)

## Installation

Made for UNIX-like operating systems. Tested with Python 2.7.

```bash

make all # downloads and install binaries to bin/
make db # downloads databases to db/

```

## Usage

CRAM is meant to be run on one sample at a time. Outputs are then combined to create tables that can be used to perform comparative analysis.

Raw reads go into the `data/` directory. For 454, these reads are expected to be in FASTQ format. For Illumina, they are expected to be in QSEQ format.

The directory structure looks like this:

```
# Input
cram/data               # Raw Reads
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