# Classes for dealing with different sequence file formats
# FASTQ, FASTA, QSEQ

class Dna:
    ''' A memory-efficient fasta/q/ file iterator
    
    # parse a fasta file
    >>> with open('../test/test.fasta') as handle:
    ...     records = Dna(handle, type='fasta')
    ...     len([record for record in records])
    5
    
    # parse a fastq file
    >>> with open('../test/test.fastq') as handle:
    ...     records = Dna(handle, type='fastq')
    ...     len([record for record in records])
    5
    
    # parse a qseq file
    >>> with open('../test/test.qseq') as handle:
    ...     records = Dna(handle, type='qseq')
    ...     len([record for record in records])
    5
    
    '''
    
    def __init__(self, handle, type='fasta'):
        self.handle = handle
        self.type = type
        if self.type == 'fastq':
            self.offset = 33
        elif self.type == 'qseq':
            self.offset = 64
        else:
            self.offset = None
        
    def __enter__(self, *args):
        ''' So with statements may be used '''
        pass
        
    def __exit__(self, *args):
        ''' This is here so that Dnai() can be used in a with statement
        
        Example
        
        with Dna(open('kitten_metagenome.fastq'), type='fastq') as records:
            for record in records:
                print record
                
        This closes the file when the with statement exits.
        
        '''
        self.handle.close()
        
    def close(self):
        ''' Explicitly close the file handle '''
        self.handle.close()
        
    def __iter__(self):
        ''' The deliverator of Record() objects.
        
        uses yield so that the entire file isn't loaded into memory
        (hence the memory-efficiency)
        
         '''
        
        # FASTA FILES
        if self.type == 'fasta':
            header, sequence = False, False
            for line in self.handle:
                line = line.strip()
                if line == '':
                    continue
                elif line.startswith('>'):
                    if sequence and header:
                        yield Record(header, ''.join(sequence))
                    header = line[1:].strip()
                    sequence = []
                else:
                    sequence.append(line)
            yield Record(header, ''.join(sequence))
            
        # FASTQ FILES
        elif self.type == 'fastq':
            from itertools import cycle
            
            c = cycle([0, 1, 2, 3])
            
            for line in self.handle:
                line = line.strip()
                i = c.next()
                if i == 0:
                    header = line[1:]
                elif i == 1:
                    sequence = line
                elif i == 3:
                    quality = [ (ord(i) - self.offset) for i in line ]
                    yield Record(header, sequence, quality)
                    
        # QSEQ FILES (Illumina)
        elif self.type == 'qseq':
            for line in self.handle:
                line = line.strip().split()
                header = ':'.join(line[:7])
                sequence = line[8]
                quality = line[9]
                quality = [ (ord(i) - self.offset) for i in quality ]
                
                yield Record(header, sequence, quality)
                    
        else:
            raise IOError, 'unknown filetype %s' % self.type


class Record:
    ''' A nucleotide record.
    
    # Create a record
    >>> record = Record('a sequence', 'GATC')
    
    # Print record in fasta format
    >>> print record.fasta
    >a sequence
    GATC
    
    # Cannot convert fasta -> fastq (no quality information)
    >>> print record.fastq
    Traceback (most recent call last):
    ...
    IOError: record does not contain quality information
    
    # Create a record with quality information
    >>> record = Record('a sequence with quality', 'GATC', [10, 10, 10, 10])
    
    # Print record in fasta format
    >>> print record.fasta
    >a sequence with quality
    GATC
    
    # Print record in fastq format
    >>> print record.fastq
    @a sequence with quality
    GATC
    +a sequence with quality
    ++++
    
    # Printing qseq is not implemented yet
    >>> print record.qseq
    Traceback (most recent call last):
    ...
    Exception: qseq not implemented!
    
    '''
    def __init__(self, *args):
        self.header = args[0]
        self.sequence = args[1]
        if len(args) == 3:
            self.type = 'fastq'
            self.quality = [ int(i) for i in args[2] ]
        else:
            self.type = 'fasta'
            self.quality = None
    
    @property
    def fasta(self):
        ''' return fasta formatted string '''
        return '>%s\n%s' % (self.header, self.sequence.replace('.', 'N'))
    
    @property
    def fastq(self):
        ''' return fastq formatted string '''
        if self.quality == None:
            raise IOError, 'record does not contain quality information'
        
        return '@%s\n%s\n+%s\n%s' % (self.header,
            self.sequence.replace('.', 'N'),
            self.header,
            ''.join(chr(i+33) for i in self.quality))
            
    @property
    def qseq(self):
        ''' Return a qseq formatted string
        
        NOT IMPLEMENTED
        do not use.
        
        '''
        raise Exception, 'qseq not implemented!'
    
    def __str__(self):
        if self.type == 'fasta':
            return self.fasta
        elif self.type == 'fastq':
            return self.fastq
            
    def __len__(self):
        return len(self.sequence)
            
    def __repr__(self):
        return '<Record: %s>' % self.header     
        

if __name__ == '__main__':
    import doctest
    doctest.testmod()