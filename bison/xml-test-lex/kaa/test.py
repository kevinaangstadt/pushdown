#!/usr/bin/env python

# We're going to test this parser with VASim

import argparse
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree

ElementTree = xml.etree.ElementTree


@contextlib.contextmanager
def mktmpdir():
    dir = tempfile.mkdtemp()
    cur_dir = os.getcwd()
    os.chdir(dir)
    yield dir
    os.chdir(cur_dir)
    shutil.rmtree(dir)


def main():
    root = os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument("xmlfile", help="the xml file to test")

    args = parser.parse_args()

    try:
        e = ElementTree.parse(args.xmlfile)
    except ElementTree.ParseError:
        sys.exit(1)

    with mktmpdir() as d:
        with open(os.path.join(d, "xml.input"), "wb") as f:
            convert_cmd = [os.path.join(root, 'main2'), args.xmlfile]
            print convert_cmd
            subprocess.call(convert_cmd, stdout=f)

        vasim_cmd = [
            "/home/kaa2nx/AP/vasim-dpda/vasim", "-r",
            "/home/kaa2nx/AP/pushdown/bison/xml-test-lex/parser/xml.multi.epsreduced.mnrl",
            os.path.join(d, "xml.input")
        ]

        subprocess.call(vasim_cmd)

        # now we read in the report file
        with open("reports_0tid_0packet.txt", "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                last_line = lines[len(lines) - 1]
                rule = int(last_line.split(":")[2].strip())

                print "the rule is", rule

                if rule != 0:
                    sys.exit(0)

    sys.exit(1)


if __name__ == '__main__':
    main()
