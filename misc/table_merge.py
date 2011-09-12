#!/usr/bin/env python

# table merge - merge two tab or comma-separated value files
# usage: table_merge.py table1.csv ... tablen.csv

import sys

class Csv(object):
    ''' Parse a CSV file and return it as a hash.
    data = Csv.parse(handle, # file handle
           sep='\t',         # record sepatator
           key=0)            # key column '''
    
    @classmethod
    def parse(handle, **args):
        
        # options
        sep = args.get('separator', ',') # record separator character
        key = args.get('key_column', 0)  # key column
        
        # create something to store data in
        data = {}
        
        # deal with header
        header   = handle.next().strip().split(sep)
        main_key = header.pop(key)
        
        for line in handle:
            
            line    = line.strip.split(sep)
            datum   = {}
            primary = line.pop(key)
            
            for k, d in zip(header, line):
                # sanity check
                if key in datum:
                    raise Exception("Duplicate secondary key: %s!" % k)
                # add a column
                datum[k] = d
            # sanity check
            elif primary in data:
                    raise Exception("Duplicate primary key: %s" % primary)
            # add a row    
            data[primary] = datum
            
        return data
    
    @classmethod
    def careful_merge(*datas):
        ''' merge csv files (from hashes) without accidentally
        overwriting anything'''
        
        # make sure there are no duplicates
        assert len(set(*i.values() for i in datas)) == len(i.values() for i in datas)
        return dict(i.items() for i in datas)
        
    @classmethod    
    def pretty_print(d, **args):
        sep = args.get('sep', '\t')
        ''' print the table pretty-like'''
        pass
        
def main():
    
    # MUST LOAD ALL THE TABLES!!!
    datas = dict( (i, Csv.parse(open(i))) for i in sys.argv )
    
    # le merge
    Csv.careful_merge(datas)
    
    Csv.pretty_print(datas)
    # PRINT 'EM!