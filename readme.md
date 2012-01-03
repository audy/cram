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

## Installation & Usage

Please refer to the [wiki](https://github.com/audy/cram/wiki)