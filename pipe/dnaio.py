class Dna:
    ''' memory-efficient fasta/q/ file iterator '''
    def __init__(self, handle, type='fasta'):
        self.handle = handle
        self.type = type
        
    def __enter__(self, *args):
        pass
        
    def __exit__(self, *args):
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
                    quality = line
                    yield Record(header, sequence, quality)
                    
        # QSEQ FILES (Illumina)
        elif self.type == 'qseq':
            for line in self.handle:
                line = line.strip().split()
                header = ':'.join(line[:7])
                sequence = line[8]
                quality = line[9]
                
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
            self.quality = [ ord(i) for i in args[2] ]
        else:
            self.type = 'fasta'
    
    @property
    def fasta(self):
        ''' return fasta formatted string '''
        return '>%s\n%s' % (self.header, self.sequence.replace('.', 'N'))
    
    @property
    def fastq(self):
        ''' return fastq formatted string '''
        try:
            self.quality
        except AttributeError:
            raise IOError, 'cant make fastq out of fasta file!'
        
        return '@%s\n%s\n+%s\n%s' % (self.header,
            self.sequence.replace('.', 'N'),
            self.header,
            ''.join(chr(i) for i in self.quality))
            
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
        

def test():
    # TEST FASTA IO
    fasta_file = \
'''

>header
sequencesequence
sequence
sequencesequencesequencesequence


>header2
sequencesequencesequencesequence
sequence
sequence'''.split('\n')

    assert len(list(Dna(fasta_file))) == 2

    # fasta -> fastq, CANT HAPPEN!
    try:
        list(Dna(fasta_file))[0].fastq
    except IOError:
        pass
    else:
        raise AssertionError
    
    # fastq iterator!
    fastq_file = \
'''@header1
sequencesequencesequence
+header1
+qualitescanstartwithaplussign
@header2
sequencesequencesequencesequence
+header2
moresequenceeyaaayayyyy
'''.split('\n')

    assert len(list(i.fasta for i in Dna(fastq_file, type='fastq')))
    

test()