#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/MNRL/python/")

import pydotplus
import mnrl


def mnrl2dot(mn):
    '''Converts a MNRL network to a DOT SUBGRAPH

    Args:
        mn (mnrl.MNRLNetwork): the MNRLNetwork

    Returns:
        (pydotplus.Graph): the same machine in DOT format
    '''

    def tuple2int((x, _)):
        return int(x[1:])

    g = pydotplus.Graph(name=mn.id)

    # STEP 1: add in all of the nodes
    for _, node in sorted(mn.nodes.iteritems(), key=tuple2int):
        if isinstance(node, mnrl.HPDState):
            # we need to come up with the label for this node
            label = "{id: %s | { stack: %s | pop: %s } | input: %s | push: %s }" % (
                node.id, node.stackSet, node.popStack, node.symbolSet,
                node.pushStack)

            n = pydotplus.Node(name=node.id)
            n.set_label(label)
            n.set_shape("record")

            if node.report:
                n.set_style("filled")
                n.set_fillcolor("chartreuse")

            if node.enable == mnrl.MNRLDefs.ENABLE_ON_START_AND_ACTIVATE_IN:
                n.set_style("filled")
                n.set_fillcolor("cadetblue1")

            # add it to the graph
            g.add_node(n)
        else:
            raise SystemExit('Unsupported Node Type: ' + str(type(node)))

    # STEP 2: add in all the edges
    for _, node in sorted(mn.nodes.iteritems(), key=tuple2int):
        if isinstance(node, mnrl.HPDState):
            _, conn_l = node.getOutputConnections()[
                mnrl.MNRLDefs.H_PD_STATE_OUTPUT]
            for conn in conn_l:
                g.add_edge(pydotplus.Edge(src=node.id, dst=conn["id"]))
        else:
            raise SystemExit('Unsupported Node Type: ' + str(type(node)))

    return g


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="the MNRL file to process")
    parser.add_argument("outfile", help="the DOT file to write")

    args = parser.parse_args()

    mn = mnrl.loadMNRL(args.infile)

    g = mnrl2dot(mn)

    with open(args.outfile, "wb") as f:
        f.write(g.to_string())


if __name__ == '__main__':
    main()
