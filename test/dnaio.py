import unittest
from metacram import Dna, Record

class TestDna(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testParseFasta(self):
        with open('data/test.fasta') as handle:
            records = Dna(handle, type='fasta')
            self.assertEqual(len(list(records)), 5)
    
    def testParseFastq(self):
        with open('data/test.fastq') as handle:
            records = Dna(handle, type='fastq')
            self.assertEqual(len(list(records)), 5)
    
    def testParseQseq(self):
        with open('data/test.qseq') as handle:
            records = Dna(handle, type='qseq')
            self.assertEqual(len(list(records)), 5)

class TestRecord(unittest.TestCase):
    
    def testCreateFastaRecord(self):
        header, sequence = 'foo', 'GATC'
        record = Record(header, sequence)
        
        self.assertEqual(record.header, header)
        
        self.assertEqual(record.sequence, sequence)
    
    def testCreateFastqRecord(self):
        header, sequence, quality = 'foo', 'GATC', [10, 10, 10, 10]
        
        record = Record(header, sequence, quality)
        
        self.assertEqual(record.header, header)
        
        self.assertEqual(record.sequence, sequence)
        
        self.assertEqual(record.quality, quality)
    
    def testFormatPrinting(self):
        header, sequence, quality = 'foo', 'GATC', [10, 10, 10, 10]
        
        record = Record(header, sequence, quality)
        
        self.assertEqual(record.fasta, '>foo\nGATC')
        self.assertEqual(record.fastq, '@foo\nGATC\n+foo\n++++')
        
        # fails: self.assertRaises(Exception, record.qseq)

if __name__ == '__main__':
    unittest.main()