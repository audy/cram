PLATFORM = $(shell uname)

bin:
	mkdir bin

db:
	mkdir db

binaries: bin/velvetg bin/prodigal bin/phmmer bin/smalt

databases: db/subsystems2peg db/subsystems2role db/seed.fasta

all: binaries databases

bin/velvetg: bin
	curl -O http://www.ebi.ac.uk/~zerbino/velvet/velvet_1.1.05.tgz
	tar -zxvf velvet_1.1.05.tgz
	make -C velvet_1.1.05 velveth velvetg MAXKMERLENGTH=71 OPENMP=1 LONGSEQUENCES=1
	mv velvet_1.1.05/velvet{g,h} bin/
	rm -rf velvet_1.1.05*

bin/prodigal: bin
	curl -O http://prodigal.googlecode.com/files/prodigal.v2_00.tar.gz
	tar -zxvf prodigal.v2_00.tar.gz
	make -C prodigal.v2_00
	mv prodigal.v2_00/prodigal bin/
	rm -rf prodigal.v2_00*

bin/phmmer: bin
	curl -O http://selab.janelia.org/software/hmmer3/3.0/hmmer-3.0.tar.gz
	tar -zxvf hmmer-3.0.tar.gz
	cd hmmer-3.0; ./configure; make; cd -
	mv hmmer-3.0/src/phmmer bin/
	rm -r hmmer-3.0*

bin/smalt: bin
	curl -O ftp://ftp.sanger.ac.uk/pub4/resources/software/smalt/smalt-0.5.7.tgz
	tar -zxvf smalt-0.5.7.tgz
	%if $(PLATFORM) == Darwin
		mv smalt-0.5.7/smalt_MacOSX_i386 bin/smalt
	%elif $(PLATFORM) == Linux
		mv smalt-0.5.7/smalt_i686 bin/smalt
	%endif
	rm -rf smalt-0.5.7*

db/subsystems2peg: db
 	curl ftp://ftp.theseed.org/subsystems/subsystems2peg.gz | gunzip > db/subsystems2peg

db/subsystems2role: db
	curl ftp://ftp.theseed.org/subsystems/subsystems2role.gz | gunzip > db/subsystems2peg

db/taxcollector.fa: db
	curl http://microgator.org/taxcollector.fa.gz | gunzip > db/taxcollector.fa

db/seed.fasta: db
	curl ftp://ftp.theseed.org/genomes/SEED/SEED.fasta.gz | gunzip > db/seed.fasta
