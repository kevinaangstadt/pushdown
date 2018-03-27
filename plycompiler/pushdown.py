import os
import sys

sys.path.append(
    os.path.dirname(os.path.abspath(__file__)) + "/../MNRL/python/")

import mnrl
import mnrlerror


def char(n):
    x = []
    if n == 0:
        x.append(0)
    while n:
        x.append(n % 256)
        n //= 256
    s = ''.join(r'\x{:02x}'.format(b) for b in reversed(x))
    return s


class State(object):
    def __init__(self, id, rules, ttransitions, nttransitions):
        self._id = id
        # rules is a list of ParseSate
        self._rules = rules
        # t is a dict of TERMINAL -> Shift/Reduce
        self._t = ttransitions
        # t is dict of NONTERMINAL -> Shift/Reduce
        self._nt = nttransitions
        self._mark = False

    def contains_final(self):
        for r in self._rules:
            if r._id == 0:
                return True
        return False

    def mark(self):
        self._mark = True

    def unmark(self):
        self._mark = False

    def is_marked(self):
        return self._mark


class Rule(object):
    def __init__(self, id, lhs, rhs):
        self._id = id
        self._lhs = lhs
        self._rhs = rhs

    def __str__(self):
        rhs = " ".join(self._rhs)
        return "Rule {}    {} -> {}".format(self._id, self._lhs, rhs)


class ParseState(object):
    def __init__(self, rule_id, position=-1):
        self._id = rule_id
        self._pos = position
        self._orig = list()


class Production(object):
    def __init__(self, lhs, rhs):
        self._lhs = lhs
        self._rhs = rhs


class Pushdown(object):
    def __init__(self, type, terms, nonterms):
        self._type = type
        self._states = dict()
        self._rules = dict()
        self._t = dict()
        self._nt = dict()

        self._terms = dict.fromkeys(terms)
        # we will give eatch term a unique character
        i = 1
        for t in self._terms:
            self._terms[t] = char(i)
            i += 1
        # the end character will always be 255
        self._terms['$end'] = char(255)

        self._nonterms = nonterms

        # set multipop to be defaulted off
        self._multipop = False

    def add_state(self, st):
        self._states[st._id] = st

    def add_rule(self, r):
        self._rules[r._id] = r

    def add_t(self, t, nums):
        self._t[t] = nums

    def add_nt(self, nt, nums):
        self._nt[nt] = nums

    def set_multipop(self, new_val):
        self._multipop = new_val

    def fix_rules(self):
        '''Depending on the PA format, we might not know how many symbols to pop
        on a reduction.  This code walks through and updates the value based
        on the current rule being reduced.'''
        for i, state in self._states.iteritems():
            for j, action in state._t.iteritems():
                if isinstance(action, Reduce) and action._rule._pos < 0:
                    # the position hasn't been set yet
                    action._rule._pos = len(self._rules[action._rule._id]._rhs)
            for j, action in state._nt.iteritems():
                if isinstance(action, Reduce) and action._rule._pos < 0:
                    # the position hasn't been set yet
                    action._rule._pos = len(self._rules[action._rule._id]._rhs)

    def generate_mnrl(self):
        """Here, we will convert the parser into a homogeneous DPDA and return
        it as a MNRL file"""

        # first fix up the postions
        self.fix_rules()

        # make a MNRL network that we'll use eventually
        mn = mnrl.MNRLNetwork("parser")

        # let's build up the information we need now...abs
        # STEP 1: For each state, make a dict and populate with all of the
        # terminals and non-terminals
        mnrl_nodes = dict.fromkeys(self._states.keys())

        for k in mnrl_nodes:
            # we keep terminals and nonterminals separate
            state = mnrl_nodes[k] = dict()

            # terms represent different lookahead values
            state["terms"] = dict.fromkeys(self._terms.keys())

            # we get to a non-terminal after a reduction
            state["nonterms"] = dict.fromkeys(self._nonterms)

            # for each of the nonterms, we need to have different lookaheads
            for j in state["nonterms"]:
                state["nonterms"][j] = dict.fromkeys(self._terms.keys())

        # STEP 2: Add all of the states
        for k, state in self._states.iteritems():
            # we need to create a different state for each combination
            # of input/stack/push/pop

            # log if we found the final accept
            accept_found = False

            # check if we are the starting state
            if k == 0:
                enable = mnrl.MNRLDefs.ENABLE_ON_START_AND_ACTIVATE_IN
            else:
                enable = mnrl.MNRLDefs.ENABLE_ON_ACTIVATE_IN

            # for each of these transitions, we'll add a PDState
            # we need to add it for each reduction target, so this might
            # cause a decent increase in size

            # First, we'll handle the terminals
            for trans, rule in state._t.iteritems():
                # okay, now we need to figure out the parameters for the
                # PDState.  This is going to depend on if we have a
                # Shift or a Reduce

                # First, we make the lookahead memory
                la_state = mn.addHPDState(
                    '*',  # don't care about the stack
                    0,  # don't pop the stack
                    symbolSet=self._terms[trans],
                    enable=enable,
                    pushStack=char(0) if k == 0 else None,
                    attributes={
                        'ply': k,
                        'lookahead': None
                    })
                if isinstance(rule, Shift):
                    # we have a shift
                    m_state = mn.addHPDState(
                        '*',  # don't care about stack
                        0,  # don't pop the stack
                        pushStack=char(rule._goto),
                        attributes={
                            'goto': rule._goto,
                            'ply': k,
                            'lookahead': trans
                        })
                elif isinstance(rule, Reduce):
                    # we have a reduction
                    m_state = mn.addHPDState(
                        '*',  # don't care about the stack
                        rule._rule._pos if self._multipop else 1
                        if rule._rule._pos > 0 else 0,  # pop the stack
                        report=True,
                        reportId=rule._rule._id,
                        attributes={
                            # we've already popped one
                            'toPop': 0
                            if self._multipop else rule._rule._pos - 1,
                            'ply': k,
                            'lookahead': trans,
                            'lhs': self._rules[rule._rule._id]._lhs
                        })
                else:
                    # we have an accept rule from bison
                    if trans == '$end':
                        m_state = mn.addHPDState(
                            '*',  # don't care about the stack
                            0,  # don't pop
                            report=True,
                            reportId=0,
                            attributes={
                                'ply': k,
                                'lookahead': "$end"
                            })
                        accept_found = True

                # we make a connection between the lookahead and the action
                mn.addConnection(
                    (la_state.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                    (m_state.id, mnrl.MNRLDefs.H_PD_STATE_INPUT))
                mnrl_nodes[k]["terms"][trans] = {
                    'lookahead': la_state,
                    'action': m_state
                }

            # Now, we will do the same thing for the non-terminals
            for trans, rule in state._nt.iteritems():
                for term in mnrl_nodes[k]["nonterms"][trans]:
                    if isinstance(rule, Shift):
                        # we have a shift
                        # It's already on the stack, just go
                        m_state = mn.addHPDState(
                            char(k),  # peek at stack
                            0,  # don't pop the stack
                            pushStack=char(rule._goto),
                            attributes={
                                'goto_a': rule._goto,
                                'ply': k,
                                'lookahead': term
                            })
                    elif isinstance(rule, Reduce):
                        # we have a reduction
                        m_state = mn.addHPDState(
                            char(k),  # peek at the stack
                            rule._rule._pos if self._multipop else 1
                            if rule._rule._pos > 0 else 0,  # pop the stack
                            report=True,
                            reportId=rule._rule._id,
                            attributes={
                                # we've already popped one
                                'toPop':
                                0 if self._multipop else rule._rule._pos - 1,
                                'ply':
                                k,
                                'lookahead':
                                term,
                                'lhs':
                                self._rules[rule._rule._id]._lhs
                            })

                    mnrl_nodes[k]["nonterms"][trans][term] = m_state

            # Finally, we'll check to see if this state has the final reduction
            # we only get here by a reduction

            if not accept_found and k != 0 and state.contains_final():
                final = mn.addHPDState(
                    '*',  # don't care about the stack
                    0,  # don't pop
                    report=True,
                    reportId=0,
                    attributes={
                        'ply': k,
                        'lookahead': "$end"
                    })
                mnrl_nodes[k]["terms"]["$end"] = {
                    "lookahead": None,
                    "action": final
                }

        # STEP 3: We now need to add additional popping nodes
        reductions = list()
        for node in mn.nodes.values():
            # we first check if this is a reduction node that needs some
            # additional pops
            tmp = node
            if 'toPop' in node.attributes:
                if node.attributes['toPop'] > 0:
                    for i in range(node.attributes['toPop']):
                        # we're just making a chain of pops and connecting them
                        pop = mn.addHPDState(
                            '*',  # ignore the stackSet
                            1,  # perform a pop
                            attributes={
                                'lookahead': tmp.attributes['lookahead'],
                                'lhs': tmp.attributes['lhs']
                            })

                        mn.addConnection(
                            (tmp.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (pop.id, mnrl.MNRLDefs.H_PD_STATE_INPUT))

                        tmp = pop
                # add this to our list that we need to wire up for reductions
                reductions.append(tmp)

        # STEP 4: Now, it's time to wire everything up

        # STEP 4.1: We'll do the reduction wiring
        for node in reductions:
            la = node.attributes['lookahead']
            lhs = node.attributes['lhs']

            # we will go through all of the states, and make a connection
            # where there is a nonterminal with the particular lookahead
            for id, state in mnrl_nodes.iteritems():
                for lookahead, target_node in state['nonterms'].get(
                        lhs, dict()).iteritems():
                    if target_node is not None and lookahead == la:
                        # This reduction state exists, we should connect it
                        mn.addConnection(
                            (node.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (target_node.id, mnrl.MNRLDefs.H_PD_STATE_INPUT))

        # STEP 4.2: We'll connect all of the shift operations
        for id, node in mn.nodes.iteritems():
            la = node.attributes['lookahead']
            if 'goto' in node.attributes:
                # this was a shift of a term, so we need a new lookahead
                for _, st in mnrl_nodes[node.attributes['goto']][
                        'terms'].iteritems():
                    if st is not None:
                        mn.addConnection(
                            (node.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (st["lookahead"].id,
                             mnrl.MNRLDefs.H_PD_STATE_INPUT))
            if 'goto_a' in node.attributes:
                # this was a shift of a nonterm, so we don't need lookahead
                for lookahead, st in mnrl_nodes[node.attributes['goto_a']][
                        'terms'].iteritems():
                    if st is not None and lookahead == la:
                        mn.addConnection(
                            (node.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (st["action"].id, mnrl.MNRLDefs.H_PD_STATE_INPUT))

        # STEP 5: remove extra nodes
        changed = True
        while changed:
            changed = False
            for node in mn.nodes.values():
                if len(
                        node.getInputConnections()
                    [mnrl.MNRLDefs.H_PD_STATE_INPUT][1]
                ) == 0 and node.enable == mnrl.MNRLDefs.ENABLE_ON_ACTIVATE_IN:
                    mn.removeNode(node.id)
                    changed = True
        
                if len(node.getOutputConnections()
                       [mnrl.MNRLDefs.H_PD_STATE_OUTPUT]
                       [1]) == 0 and not node.report:
                    mn.removeNode(node.id)
                    changed = True

        # STEP 6: Clean up the nodes
        for id, node in mn.nodes.iteritems():
            #node.attributes.pop('goto', None)
            node.attributes.pop('toPush', None)
            node.attributes.pop('toPop', None)

        # STEP 5: Return the MNRL network
        return mn


class Shift(object):
    def __init__(self, goto):
        self._goto = goto

    def __str__(self):
        return "Shift, and go to state {}".format(self._goto)


class Reduce(object):
    def __init__(self, rule):
        self._rule = rule

    def __str__(self):
        return "Reduce using rule {}".format(self._rule._id)


class Accept(object):
    def __str__(self):
        return "Accept"
