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

Tested on Mac OSX and Ubuntu using Python 2.7.

Before installing, make sure you have the following:

- A unix-like operating system (Mac OS X, Ubuntu, _et cetera_).
- A licensed copy of [CLC Assembly Cell 3](http://clcbio.com).

Download and extract the pipeline, and type `make install` in the directory. This will download and install Phmmer, Prodigal, & Velvet.

Type `make databases` to download and create necessary databases (SEED, RDP-TaxCollector).

## Usage