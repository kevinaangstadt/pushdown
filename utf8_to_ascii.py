#!/usr/bin/env python

import argparse
import codecs

parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("outfile")

args = parser.parse_args()


def writex(err):
    return (u'X', err.end)


codecs.register_error('x', writex)

with codecs.open(args.infile, "rb", encoding="utf-8", errors="x") as f:
    s = f.read()

with codecs.open(args.outfile, "wb", encoding="ascii", errors="x") as f:
    f.write(s)
