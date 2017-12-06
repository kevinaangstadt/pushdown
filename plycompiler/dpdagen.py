#!/usr/bin/env python

import argparse
import os
import parse


def write_lexer(terms, filename=None, lexermodule='lexer', lexername='lexer'):
    if filename is None:
        filename = "lex_wrapper.py"

    bn = os.path.basename(filename)

    try:
        with open(filename, "w") as f:
            f.write('''
# %s
# This file was automatically generated.  Do not edit.

from __future__ import print_function
import argparse
import %s

_terms = %r

l = %s.%s

            ''' % (bn, lexermodule, terms, lexermodule, lexername))

            # a function to convert a hex escape string to the hex characters
            f.write('''
def str2hex(s):
    s = '0' + s[1:]
    return chr(int(s, 16))

            ''')

            # let's write the main function
            f.write('''
def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="the input file to lex")

    args = p.parse_args()

    with open(args.input, "rb") as f:
        data = f.read()

    l.input(data)

    while True:
        tok = l.token()
        if not tok:
            break      # No more input
        print(str2hex(_terms[tok.type]), end='')

    print(str2hex(_terms['$end']), end='')

            ''')

            # finally, we'll call main
            f.write('''
if __name__ == '__main__':
    main()
            ''')
    except IOError:
        raise


def main():

    p = argparse.ArgumentParser()
    p.add_argument("parsetable", help="the path to the parser.out file")
    p.add_argument("mnrlfile", help="detination of the MNRL DPDA")
    p.add_argument(
        "--lexermodule", default="lexer", help="the name of the lexer module")
    p.add_argument(
        "--lexername",
        default="lexer",
        help="the name of the lexer variable inside the lexer module")
    p.add_argument(
        "--wrapper",
        default="lex_wrapper.py",
        help="the name of the wrapper generated for the lexer")

    args = p.parse_args()

    with open(args.parsetable, "rb") as f:
        thefile = f.read()

    machine = parse.parser.parse(thefile)
    machine.determine_reductions()
    mn = machine.generate_mnrl()
    mn.exportToFile(args.mnrlfile)
    
    print "Number of States: %d" % (len(mn.nodes))

    write_lexer(
        machine._terms,
        filename=args.wrapper,
        lexermodule=args.lexermodule,
        lexername=args.lexername)


if __name__ == '__main__':
    main()
