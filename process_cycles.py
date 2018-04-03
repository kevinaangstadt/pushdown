#!/usr/bin/env python

import argparse
import math

def get_cycles(line):
    ''' return the next number of cycles from string representing line '''
    parts = line.split(',')
    assert len(parts) == 2
    return int(parts[1].strip())
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lexfile")
    parser.add_argument("parsefile")
    parser.add_argument("--lex-freq", type=float, default=1.0, help="frequency of lexer core in GHz")
    parser.add_argument("--parse-freq", type=float, default=1.0, help="frequency of the parser core in GHz")
    parser.add_argument("--cpu-cycles", type=int, default=0, help="number of cycles needed to convert lex report to parse token")
    parser.add_argument("--cpu-freq", type=float, default=1.0, help="frequency of the cpu core in GHz")
    
    args = parser.parse_args()
    
    # what is the multiplicative factor for the lexer portion?
    # if the lexer is faster, then we can count each cycle as a fraction of the parser
    lex_mult = args.parse_freq / args.lex_freq
    
    cpu_mult = args.parse_freq / args.cpu_freq
    
    with open(args.lexfile, "r") as lexfile:
        with open(args.parsefile, "r") as parsefile:
            cycles = 0
            
            lex_line = lexfile.readline()
            assert len(lex_line) != 0
            
            # we incur the cost of finding the first token
            cycles += int(math.ceil(get_cycles(lex_line) * lex_mult)) + int(math.ceil(args.cpu_cycles*cpu_mult))
            
            # we will use these to keep track of the balance
            imbalance = 0
            
            while True:
                lex_line = lexfile.readline()
                
                if len(lex_line) == 0:
                    break
                    
                p_c = get_cycles(parsefile.readline())
                l_c = int(math.ceil(get_cycles(lex_line) * lex_mult)) + int(math.ceil(args.cpu_cycles*cpu_mult))
                
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