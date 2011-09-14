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
        self.handle.close()
        
    def close(self):
        ''' close the handle '''
        self.handle.close()
        
    def __iter__(self):
        ''' iterate through file based on type '''
        
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
    ''' a nucleotide record '''
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
        ''' return qseq formatted string '''
        raise Exception, 'not implemented!'
    
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