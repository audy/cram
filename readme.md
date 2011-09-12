# Metagenome Pipeline

Austin G. Davis-Richardson

## Overview

## Installation

Tested on Mac OSX and Ubuntu using Python 2.7.

Before installing, make sure you have the following:

- A unix-like operating system (Mac OS X, Ubuntu, _et cetera_).
- A licensed copy of [CLC Assembly Cell 3](http://clcbio.com).

Download and extract the pipeline, and type `make install` in the directory. This will download and install Phmmer, Prodigal, & Velvet.

Type `make databases` to download and create necessary databases (SEED, RDP-TaxCollector).