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
    def parse(self, handle, **args):
        
        # options
        sep = args.get('separator', ',') # record separator character
        key = args.get('key_column', 0)  # key column
        
        # create something to store data in
        data = {}
        
        # deal with header
        header   = handle.next().strip().split(sep)
        print header
        main_key = header.pop(key)

        for line in handle:
            
            line    = line.strip().split(sep)
            datum   = {}
            primary = line.pop(key)
            
            for k, d in zip(header, line):
                # sanity check
                if key in datum:
                    raise Exception("Duplicate secondary key: %s!" % k)
                # add a column
                datum[k] = d
                # sanity check
            if primary in data:
                    raise Exception("Duplicate primary key: %s" % primary)
            # add a row    
            data[primary] = datum
            
        return data
    
    @classmethod
    def careful_merge(self, *datas):
        ''' merge csv files (from hashes) without accidentally
        overwriting anything'''
        
        # make sure there are no duplicates
        #assert len(set(i.values() for i in datas)) == len(i.values() for i in datas)

        return dict(i.items() for i in datas)
        
    @classmethod    
    def pretty_print(self, d, **args):
        sep = args.get('sep', ',')
        ''' print the table pretty-like'''
        pass
        

def main():
    
    # MUST LOAD ALL THE TABLES!!!
    datas = dict( (i, Csv.parse(open(i), separator=",")) for i in sys.argv[1:] )

    #print datas.values()[0]
    
    # le merge
    Csv.careful_merge(datas)
    
    # Csv.pretty_print(datas)
    # PRINT 'EM!
    
if __name__ == '__main__':
    main()
