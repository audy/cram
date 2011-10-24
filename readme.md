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

Databases and executables will be stored in `~/cram/db` and `~/cram/bin/`.

## Usage

CRAM is invoked via the command-line.

### Setting up an experiment

CRAM is a collection of tools used for creating metagenomics pipelines. Pipelines are defined in scripts that follow this pattern:

```python

from metacram import *

# do metagenome things using metacram

```

There are two pipelines included with this packages: Illumina and Roche 454 for analyzing metagenomes produced by their respective sequencing technologies. To define your own pipeline, see the docs.

One can create a project for analyzing an Illumina metagenome like this:

`metacram illumina ~/baby_drool_microbiome/`

A CRAM Project contains the pipeline script and a directory structure that contains the output of the various analyses that looks like this:

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

This will clone a fresh copy of CRAM into your experiment directory. However, the `db/` and `bin/` directories will be empty. Instead of copying these directories (which can be large), use symbolic links.

This will save space and create consistency between experiments

### Merging Output

Output tables can be merged into Functional and Taxonomic Abundancy Matrices. These matrices can be merged allowing for standardization, normalization, visualization and analysis of results.

There are scripts located in the `tools/` directory to help achieve this.