#!/usr/bin/env python

import argparse
import os
import parse
import bisonparse


def write_tokens(terms, enum_name="token", filename=None):
    """ Helper file to generate C header with term enum """

    def end_ff(k):
        if k == "$end":
            return "$end = 0xff"
        else:
            return k

    if filename is None:
        filename = "tokens.h"

    bn = os.path.basename(filename)

    try:
        with open(filename, "w") as f:
            f.write('''
// {}
// This file was automatically generated.  Do not edit.
            '''.format(bn))

            f.write('''
typedef enum {{
    MY_EOF,
    {}
}} {};'''.format(",\n    ".join([end_ff(k) for k in terms.keys()]), enum_name))
    except IOError:
        raise


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
    p.add_argument(
        "-b",
        "--bison",
        action="store_true",
        default=False,
        help="use the parser for bison output")
    p.add_argument(
        "-m",
        "--multipop",
        action="store_true",
        default=False,
        help="enable multipop DPDA states")
    p.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="turn on debugging for parsing")

    args = p.parse_args()

    with open(args.parsetable, "rb") as f:
        thefile = f.read()

    if args.bison:
        machine = bisonparse.parser.parse(thefile, debug=args.debug)
    else:
        machine = parse.parser.parse(thefile, debug=args.debug)

    # set up multipop
    machine.set_multipop(args.multipop)

    mn = machine.generate_mnrl()
    mn.exportToFile(args.mnrlfile)

    print "Number of States: %d" % (len(mn.nodes))

    if args.bison:
        write_tokens(machine._terms)
    else:
        write_lexer(
            machine._terms,
            filename=args.wrapper,
            lexermodule=args.lexermodule,
            lexername=args.lexername)


if __name__ == '__main__':
    main()
