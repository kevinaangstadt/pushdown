#!/usr/bin/env python

import argparse

def get_cycles(line):
    ''' return the next number of cycles from string representing line '''
    parts = line.split(',')
    assert len(parts) == 2
    return int(parts[1].strip())
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lexfile")
    parser.add_argument("parsefile")
    
    args = parser.parse_args()
    
    with open(args.lexfile, "r") as lexfile:
        with open(args.parsefile, "r") as parsefile:
            token = 1
            cycles = 0
            
            lex_line = lexfile.readline()
            assert len(lex_line) != 0
            
            # we incur the cost of finding the first token
            cycles += get_cycles(lex_line)
            
            # we will use these to keep track of the balance
            imbalance = 0
            
            while True:
                lex_line = lexfile.readline()
                
                if len(lex_line) == 0:
                    break
                    
                p_c = get_cycles(parsefile.readline())
                l_c = get_cycles(lex_line)
                
                imbalance += (l_c - p_c)
                
                cycles += p_c
                
                if imbalance > 0:
                    cycles += imbalance
                    imbalance = 0
                
            
            # just the cycles to process the last token
            cycles += get_cycles(parsefile.readline())
            
            # just the cycles to process the EOF token
            cycles += get_cycles(parsefile.readline())
            
            junk = parsefile.readline()
            assert len(junk) == 0
            
            print cycles

if __name__ == '__main__':
    main()