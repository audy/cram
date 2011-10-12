PLATFORM = $(shell uname)

ifeq ($(PLATFORM), Darwin)
	SMALT = smalt-0.5.7/smalt_MacOSX_i386

endif
ifeq ($(PLATFORM), Linux)
	SMALT = smalt-0.5.7/smalt_i686
endif

data:
	mkdir data

bin:
	mkdir bin

db:
	mkdir db

update:
	git pull git@heyaudy.com:git/cram.git master

binaries: bin/velvetg bin/prodigal bin/phmmer bin/smalt

databases: db/subsystems2peg db/subsystems2role db/seed.fasta db/taxcollector.fa

all: binaries databases data

bin/velvetg: bin
	curl -O http://www.ebi.ac.uk/~zerbino/velvet/velvet_1.1.05.tgz
	tar -zxvf velvet_1.1.05.tgz
	make -C velvet_1.1.05 velveth velvetg MAXKMERLENGTH=71 OPENMP=1 LONGSEQUENCES=1
	mv velvet_1.1.05/velvetg bin/
	mv velvet_1.1.05/velveth bin/
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
	mv $(SMALT) bin/smalt
	rm -rf smalt-0.5.7*

db/subsystems2peg: db
	curl ftp://ftp.theseed.org/subsystems/subsystems2peg.gz | gunzip > db/subsystems2peg

db/subsystems2role: db
	curl ftp://ftp.theseed.org/subsystems/subsystems2role.gz | gunzip > db/subsystems2peg

db/taxcollector.fa: db
	curl http://microgator.org/taxcollector.fa.gz | gunzip > db/taxcollector.fa

db/seed.fasta: db
	curl ftp://ftp.theseed.org/genomes/SEED/SEED.fasta.gz | gunzip > db/seed.fasta
