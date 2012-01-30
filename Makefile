PLATFORM = $(shell uname)

ifeq ($(PLATFORM), Darwin)
	SMALT = smalt-0.5.7/smalt_MacOSX_i386
	BLAST = blast-2.2.25-universal-macosx.tar.gz
endif
ifeq ($(PLATFORM), Linux)
	SMALT = smalt-0.5.7/smalt_i686
	BLAST = blast-2.2.25-x64-linux.tar.gz
endif

default: ~/cram/db/ ~/cram/bin binaries databases

~/cram/db/:
	mkdir -p ~/cram/db/

~/cram/bin:
	mkdir -p ~/cram/bin

update:
	git pull git@heyaudy.com:git/cram.git master

binaries: ~/cram/bin/velvetg ~/cram/bin/prodigal ~/cram/bin/smalt ~/cram/bin/blastall

databases: ~/cram/db/tc_seed.fasta ~/cram/db/taxcollector.fa

~/cram/bin/blastall:
	curl -O ftp://ftp.ncbi.nih.gov/blast/executables/release/2.2.25/$(BLAST)
	tar -zxvf $(BLAST) blast-2.2.25/bin/formatdb 
	tar -zxvf $(BLAST) blast-2.2.25/bin/blastall
	mv blast-2.2.25/bin/formatdb ~/cram/bin
	mv blast-2.2.25/bin/blastall ~/cram/bin
	rm -rf blast-2.2.25
	rm $(BLAST)

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

~/cram/bin/smalt:
	curl -O ftp://ftp.sanger.ac.uk/pub4/resources/software/smalt/smalt-0.5.7.tgz
	tar -zxvf smalt-0.5.7.tgz
	mv $(SMALT) ~/cram/bin/smalt
	rm -rf smalt-0.5.7*

~/cram/db/taxcollector.fa:
	curl http://microgator.org/taxcollector.fa.gz | gunzip > ~/cram/db/taxcollector.fa

~/cram/db/tc_seed.fasta:
	curl https://s3.amazonaws.com/genome-sequencing/babaco/tc_seed.fasta.gz | gunzip > ~/cram/db/seed.fasta