import unittest
from metacram import velvet

class TestVelvet(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def testVelvet(self):
        ''' test running a velvet assembly '''
    
        # TODO get test data that actually assembles!
        velvet(
            reads    = [('fasta', 'long', 'data/test.fasta')],
            outdir   = 'data/test_velvet',
            k        = 31
        )

if __name__ == '__main__':
    unittest.main()