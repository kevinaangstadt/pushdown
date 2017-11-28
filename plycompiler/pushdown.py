import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../MNRL/python/")

import mnrl
import mnrlerror


def char(n):
    x = []
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

    def assign_reductions(self, rule=None, pos=None, reductions=None):
        doit = True

        if reductions is None:
            # we should just assign origins for the closure
            doit = False

        # figure out which rules for this state we're trying to update
        therule = self._rules
        if rule is not None and pos is not None:
            therule = [
                x for x in self._rules if x._id == rule and x._pos == pos
            ]

        if doit:
            # we have reduction origin information
            for t in therule:
                for r in reductions:
                    if r not in t._orig:
                        # only add the origin if it's not there already
                        self._changed = True
                        t._orig.append(r)
        else:
            for t in therule:
                if len(t._orig) == 0 and t._pos == 0:
                    # this is a closure rule; add the origin as ourself
                    self._changed = True
                    t._orig.append(self._id)

    def get_reductions(self):
        target_set = set()
        for r in self._rules:
            for o in r._orig:
                target_set.add(o)

        return list(target_set)

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
    def __init__(self, rule_id, position):
        self._id = rule_id
        self._pos = position
        self._orig = list()


class Production(object):
    def __init__(self, lhs, rhs):
        self._lhs = lhs
        self._rhs = rhs


class Pushdown(object):
    def __init__(self, type, terms):
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

    def add_state(self, st):
        self._states[st._id] = st

    def add_rule(self, r):
        self._rules[r._id] = r

    def add_t(self, t, nums):
        self._t[t] = nums

    def add_nt(self, nt, nums):
        self._nt[nt] = nums

    def determine_reductions(self):
        '''For the reduction rules to work, we need to figure out where to
        return to for each rule.  So this method performs a pass over the
        states to determine the origin of each rule.'''

        def loop(id):
            ''' A helper function that goes though the rules for a state and
            adds the origins'''

            def match(f, k):
                '''Determine if a particular rule matches a shift'''
                if len(self._rules[f._id]._rhs) > f._pos:
                    el = self._rules[f._id]._rhs[f._pos]
                    if el == k:
                        return True
                else:
                    return False

            def help(l, s):
                '''For each shift rule, propagate the origins from the current
                state's rules, then recurse'''
                for k, v in l.iteritems():
                    if type(v) is Shift:
                        # we need to propagate the reduction origin
                        rules = [f for f in s._rules if match(f, k)]
                        for r in rules:
                            self._states[v._goto].assign_reductions(
                                rule=r._id, pos=r._pos + 1, reductions=r._orig)

                        if not s.is_marked():
                            loop(v._goto)

            s = self._states[id]
            help(s._t, s)
            help(s._nt, s)
            s.mark()

        # to get things started, we will do all of state 0
        self._states[0].assign_reductions(rule=0, pos=0, reductions=[0])
        for k, v in self._states.iteritems():
            v.assign_reductions()

        fixpoint = False
        while fixpoint is not True:
            # Because we're using DFS, there might be a need to run the loop
            # several times.  So we track changes to reach a fixpoint
            for k, v in self._states.iteritems():
                v.unmark()
                v._changed = False

            loop(0)

            fixpoint = all(not v._changed for k, v in self._states.iteritems())

    def generate_mnrl(self):
        """Here, we will convert the parser into a homogeneous DPDA and return
        it as a MNRL file"""

        # make a MNRL network that we'll use eventually
        mn = mnrl.MNRLNetwork("parser")

        # let's build up the information we need now...abs
        # STEP 1: For each state, make a dict and populate with the reduction
        # targets
        mnrl_nodes = dict.fromkeys(self._states.keys())

        for k in mnrl_nodes:
            # we need to look at each state and figure out what the reduction
            # targets are
            mnrl_nodes[k] = dict.fromkeys(self._states[k].get_reductions())
            for t in mnrl_nodes[k]:
                # we'll just keep a list of all the states
                mnrl_nodes[k][t] = list()

        # STEP 2: Add all of the states
        for k, state in self._states.iteritems():
            # we need to create a different state for each combination
            # of input/stack/push/pop

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
                for targ in mnrl_nodes[k]:
                    # okay, now we need to figure out the parameters for the
                    # PDState.  This is going to depend on if we have a
                    # Shift or a Reduce
                    if type(rule) is Shift:
                        # we have a shift
                        m_state = mn.addHPDState(
                            '*',  # don't care about stack
                            False,  # don't pop the stack
                            symbolSet=self._terms[trans],
                            pushStack=self._terms[trans],
                            enable=enable,
                            attributes={
                                'goto': rule._goto
                            })
                    else:
                        # we have a reduction
                        m_state = mn.addHPDState(
                            '*',  # don't care about the stack
                            True,  # pop the stack
                            symbolSet=self._terms[trans],
                            enable=enable,
                            report=True,
                            reportId=rule._rule._id,
                            attributes={
                                'goto':
                                targ,
                                # we've already popped one
                                'toPop':
                                rule._rule._pos - 1,
                                # we're going to need to push the reduction
                                'toPush':
                                self._terms[self._rules[rule._rule._id]._lhs]
                            })

                    mnrl_nodes[k][targ].append(m_state)

            # Now, we will do the same thing for the non-terminals
            for trans, rule in state._nt.iteritems():
                for targ in mnrl_nodes[k]:
                    if type(rule) is Shift:
                        # we have a shift
                        # It's already on the stack, just go
                        m_state = mn.addHPDState(
                            self._terms[trans],  # peek at stack
                            False,  # don't pop the stack
                            enable=enable,
                            attributes={
                                'goto': rule._goto
                            })
                    else:
                        # we have a reduction
                        m_state = mn.addHPDState(
                            self._terms[trans],  # peek at the stack
                            True,  # pop the stack
                            enable=enable,
                            report=True,
                            reportId=rule._rule._id,
                            attributes={
                                'goto': targ,
                                # we've already popped one
                                'toPop': rule._rule._pos - 1,
                                # we're going to need to push the reduction
                                'toPush':
                                self._terms[self._rules[rule._rule._id]]
                            })
                    mnrl_nodes[k][targ].append(m_state)

            # Finally, we'll check to see if this state has the final reduction
            if k != 0 and state.contains_final():
                mn.addHPDState(
                    char(255),  # the stack should have the end character
                    False,  # don't pop
                    report=True,
                    reportId=0)

        # STEP 5: We now need to add additional popping nodes
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
                            True  # perform a pop
                        )

                        mn.addConnection(
                            (tmp.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (pop.id, mnrl.MNRLDefs.H_PD_STATE_INPUT))

                        tmp = pop

                    # we will move the goto to the end of the pop chain
                    tmp.attributes['goto'] = node.attributes['goto']
                    node.attributes.pop('goto', None)

                # clean up the toPop
                node.attributes.pop('toPop', None)

            # check if we have something to push
            if 'toPush' in node.attributes:
                tmp.pushStack = node.attributes['toPush']

                # clean up the toPush
                node.attributes.pop('toPush', None)

        # STEP 4: Now, it's time to wire everything up
        for id, node in mn.nodes.iteritems():
            if 'goto' in node.attributes:
                for _, l in mnrl_nodes[node.attributes['goto']].iteritems():
                    for st in l:
                        mn.addConnection(
                            (node.id, mnrl.MNRLDefs.H_PD_STATE_OUTPUT),
                            (st.id, mnrl.MNRLDefs.H_PD_STATE_INPUT))

                # we can clean up the goto
                node.attributes.pop('goto', None)

        # STEP 5: Return the MNRL network
        return mn


class Shift(object):
    def __init__(self, goto):
        self._goto = goto


class Reduce(object):
    def __init__(self, rule):
        self._rule = rule
