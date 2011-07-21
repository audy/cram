from dnaio import *

class Trim():
    ''' The Famous Trim algorithm '''
    def __init__(self, **kwargs):
        self.input = kwargs['input']
        self.output = kwargs['out']
    
    @classmethod
    def _get_coords(self, quality, **kwargs):
        ''' the trim2 algorithm '''
        quality_cutoff = 20
        _sum, _max, first, last, start, end = 0, 0, 0, 0, 0, 0
        for a, q in enumerate(quality):
            _sum += (q - 64 - quality_cutoff)
            if _sum > _max:
                _max = _sum
                end = a
                start = first
            if _sum < 0:
                _sum = 0
                first = a
        
        return (start, end - start)
    
    @classmethod
    def trim(self, record):
        ''' an atomic method for sequence trimming '''
        
        # trimming algorithm
        coords = self._get_coords(record.quality)
        
        # truncate sequence and quality accordingly
        sequence = record.sequence[coords[0]:coords[1]]
        quality = record.quality[coords[0]:coords[1]]
        
        # create quality string
        quality = [ chr(i) for i in quality ]
        
        # quick test
        assert len(sequence) == len(quality)
        
        # make and return a new record
        new_record = Record(record.header, sequence, quality)
        
        return new_record
    
    @classmethod
    def _check_seq(self, record, **kwargs):
        ''' make sure sequence survives trimming '''
        
        ops = { # defaults
            'min_length': 0,
            'skip_if_quality_has': [],
            'skip_if_read_has': [],
        }
        
        ops.update(kwargs)
        
        for n in ops['skip_if_quality_has']:
            if n in record.quality:
                return False
        for n in ops['skip_if_read_has']:
            if n in record.sequence:
                return False
        
        if len(record.sequence) < ops['min_length']:
            return False
        return True



def test():
    raw = \
'''HWUSI-EAS163FR:13:2:1:4515:5372:0:1:A
GCCGCGGTAACACGTAGGGCGCGAGCGTTGTCCGGAATTATTGGGCGTAAAGAGCTCGTAGGCGGCCTGTTGCGTGCGCTGTGAAAGCCG
HWUSI-EAS163FR:13:2:1:4515:5372:0:1:A
ffffffffffaffffcfffafffafcfffffddfdPRdd]^bbbf_febaacafY^Wa^]b`XbcZJ_c\^XM^BBBBBBBBBBBBBBBB
'''.split('\n')
    
    trimmed = \
'''HWUSI-EAS163FR:13:2:1:4515:5372:0:1:A
GCCGCGGTAACACGTAGGGCGCGAGCGTTGTCCGGAATTATTGGGCGTAAAGAGCTCGTAGGCGGCCTGTTGC
HWUSI-EAS163FR:13:2:1:4515:5372:0:1:A
ffffffffffaffffcfffafffafcfffffddfdPRdd]^bbbf_febaacafY^Wa^]b`XbcZJ_c\^XM
'''.split('\n')
    
    record = Record(raw[0], raw[1], raw[3])
    trimmed = Record(trimmed[0], trimmed[1], trimmed[3])
    record = Trim.trim(record)
    
    assert record.sequence == trimmed.sequence
    assert record.quality == trimmed.quality


test()