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
    def __init__(self, type):
        self._type = type
        self._states = dict()
        self._rules = dict()
        self._t = dict()
        self._nt = dict()

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


class Shift(object):
    def __init__(self, goto):
        self._goto = goto


class Reduce(object):
    def __init__(self, rule):
        self._rule = rule
