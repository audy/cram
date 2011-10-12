PLATFORM = $(shell uname)

ifeq ($(PLATFORM), Darwin)
	SMALT = smalt-0.5.7/smalt_MacOSX_i386
endif
ifeq ($(PLATFORM), Linux)
	SMALT = smalt-0.5.7/smalt_i686
endif

default: ~/cram/db/ ~/cram/bin binaries databases

~/cram/db/:
	mkdir -p ~/cram/db/

~/cram/bin:
	mkdir -p ~/cram/bin

update:
	git pull git@heyaudy.com:git/cram.git master

binaries: ~/cram/bin/velvetg ~/cram/bin/prodigal ~/cram/bin/phmmer ~/cram/bin/smalt

databases: ~/cram/db/subsystems2peg ~/cram/db/subsystems2role ~/cram/db/seed.fasta ~/cram/db/taxcollector.fa

~/cram/bin/velvetg:
	curl -O http://www.ebi.ac.uk/~zerbino/velvet/velvet_1.1.05.tgz
	tar -zxvf velvet_1.1.05.tgz
	make -C velvet_1.1.05 velveth velvetg MAXKMERLENGTH=71 OPENMP=1 LONGSEQUENCES=1
	mv velvet_1.1.05/velvetg ~/cram/bin/
	mv velvet_1.1.05/velveth ~/cram/bin/
	rm -rf velvet_1.1.05*

~/cram/bin/prodigal:
	curl -O http://prodigal.googlecode.com/files/prodigal.v2_00.tar.gz
	tar -zxvf prodigal.v2_00.tar.gz
	make -C prodigal.v2_00
	mv prodigal.v2_00/prodigal ~/cram/bin/
	rm -rf prodigal.v2_00*

~/cram/bin/phmmer:
	curl -O http://selab.janelia.org/software/hmmer3/3.0/hmmer-3.0.tar.gz
	tar -zxvf hmmer-3.0.tar.gz
	cd hmmer-3.0; ./configure; make; cd -
	mv hmmer-3.0/src/phmmer ~/cram/bin/
	rm -r hmmer-3.0*

~/cram/bin/smalt:
	curl -O ftp://ftp.sanger.ac.uk/pub4/resources/software/smalt/smalt-0.5.7.tgz
	tar -zxvf smalt-0.5.7.tgz
	mv $(SMALT) ~/cram/bin/smalt
	rm -rf smalt-0.5.7*

~/cram/db/subsystems2peg:
	curl ftp://ftp.theseed.org/subsystems/subsystems2peg.gz | gunzip > ~/cram/db/subsystems2peg

~/cram/db/subsystems2role:
	curl ftp://ftp.theseed.org/subsystems/subsystems2role.gz | gunzip > ~/cram/db/subsystems2role

~/cram/db/taxcollector.fa:
	curl http://microgator.org/taxcollector.fa.gz | gunzip > ~/cram/db/taxcollector.fa

~/cram/db/seed.fasta:
	curl ftp://ftp.theseed.org/genomes/SEED/SEED.fasta.gz | gunzip > ~/cram/db/seed.fasta
