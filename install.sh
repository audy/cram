#!/bin/bash

mkdir -p bin

cd bin
    # INSTALL VELVET
    git clone https://github.com/dzerbino/velvet.git
    cd velvet
        make velveth velvetg MAXKMERLENGTH=71 OPENMP=1 LONGSEQUENCES=1
        mv velvetg ..
        mv velveth ..
    cd ..
    
    # INSTALL PRODIGAL
    curl -O http://prodigal.googlecode.com/files/prodigal.v2_00.tar.gz
    tar -zxvf prodigal.v2_00.tar.gz
    cd prodigal.v2_00
      make
      mv prodigal ..
    cd .
    
    # INSTALL PHMMER
    curl -O http://selab.janelia.org/software/hmmer3/3.0/hmmer-3.0.tar.gz
    tar -zxvf hmmer-3.0.tar.gz
    cd hmmer-3.0
      ./configure
      make
      cp src/phmmer ..
    cd ..
    
    # INSTALL BOWTIE
    curl -LO http://downloads.sourceforge.net/project/bowtie-bio/bowtie/0.12.7/bowtie-0.12.7-src.zip
    unzip bowtie-0.12.7-src.zip
    cd bowtie-0.12.7
      make
      cp bowtie ..
    cd ..
cd ..
