from pipe import *
from dnaio import *
from trim import *
from helps import *

from clc import *
from phmmer import *
from prodigal import *
from smalt import *
from velvet import *

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_pipeline_path(path):
    ''' get path to a pipeline file 
    >>> get_pipeline_path('illumina.py')
    ... 'something'
    
    '''
    return os.path.join(_ROOT, 'pipelines', path)



import cram