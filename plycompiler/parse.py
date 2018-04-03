import ply.yacc as yacc

# get the token map from the lexer
from lex import tokens

import sys

import pushdown
Pushdown = pushdown.Pushdown
State = pushdown.State
Rule = pushdown.Rule
ParseState = pushdown.ParseState
Production = pushdown.Production
Shift = pushdown.Shift
Reduce = pushdown.Reduce

# Grammar
#
# file       := GRAMMAR NEWLINE rulelist NEWLINE TLIST NEWLINE tlist NEWLINE
#                    NTLIST NEWLINE ntlist NEWLINE PMETHOD NEWLINE statelist
# rulelist   := rule rulelist
#             | empty
# tlist      := tterm tlist
#             | empty
# ntlist     := ntterm ntlist
#             | empty
# statelist  := state statelist
#             | empty
# rule       := RULE production
# tterm      := TERMINAL COLON numbers
# ntterm     := NONTERMINAL COLON numbers
# state      := STATE NEWLINE srulelist NEWLINE trules NEWLINE ntrules NEWLINE
# production := NONTERMINAL RARROW rhs
# numbers    := INT numbers
#             | empty
# srulelist  := srule
#             | empty
# trules     := trule trules
#             | empty
# ntrules    := ntrule ntrules
#             | empty
# rhs        := exp erhs
# erhs       := exp erhs
#             | empty
# srule      := LPAREN INT RPAREN production
# trule      := TERMINAL operation
# ntrule     := NONTERMINAL operation
# exp        := DOT | TERMINAL | NONTERMINAL
# operation  := SHIFT | REDUCE LPAREN production RPAREN

terminals = ["<empty>"]
non_terminals = []


def p_file(p):
    '''file : anythinglist GRAMMAR DNEWLINE rulelist TLIST DNEWLINE tlist NTLIST DNEWLINE ntlist  PMETHOD DNEWLINE statelist'''
    terms = [x for (x, _) in p[7]]
    nterms = [x for (x, _) in p[10]]

    print "non_terminals:", non_terminals
    print "terminals:", terminals

    p[0] = Pushdown(p[13], terms, nterms)

    for r in p[4]:
        p[0].add_rule(r)
    for s in p[13]:
        p[0].add_state(s)
    for k, v in p[7]:
        p[0].add_t(k, v)
    for k, v in p[10]:
        p[0].add_nt(k, v)


# ignore everything before we see the start of the GRAMMAR
def p_anything(p):
    ''' anything : RULE
                 | STATE
                 | TLIST
                 | NTLIST
                 | PMETHOD
                 | SHIFT
                 | REDUCE
                 | RARROW
                 | IDENT
                 | INT
                 | COLON
                 | LPAREN
                 | RPAREN
                 | DOT
                 | NEWLINE
                 | DNEWLINE'''
    pass


# We'll simplify things by having a single rule for all our list productions
def p_list(p):
    '''statelist : state statelist
                 | state NEWLINE statelist
                 | empty
       numbers   : INT numbers
                 | empty
       trules   : trule NEWLINE trules
                 | DNEWLINE
       ntrules  : ntrule NEWLINE ntrules
                 | empty
       erhs      : exp erhs
                 | empty
       anythinglist : anything anythinglist
                    | empty'''
    if len(p) == 2:
        p[0] = list()
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]] + p[2]


def p_non_empty_list(p):
    '''tlist     : tterm NEWLINE tlist
                 | tterm DNEWLINE
       ntlist    : ntterm NEWLINE ntlist
                 | ntterm DNEWLINE
       srulelist : srule NEWLINE srulelist
                 | srule DNEWLINE
       sactions : action NEWLINE sactions
                | action DNEWLINE'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


# def p_rulelist(p):
#     '''rulelist : ruleset DNEWLINE rulelist
#                 | empty'''
#     if len(p) == 2:
#         p[0] = list()
#     else:
#         p[0] = p[1] + p[3]

# def p_forced_list(p):
#     '''trules  : trule etrules
#        ntrules : ntrule entrules'''
#     p[0] = [p[1]] + p[2]


def p_ruleset(p):
    '''rulelist   : rule NEWLINE rulelist
                 | rule DNEWLINE'''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_rule(p):
    '''rule : RULE production'''
    p[0] = Rule(p[1], p[2]._lhs, p[2]._rhs)


def p_tterm(p):
    '''tterm : IDENT COLON numbers'''
    global terminals
    terminals.append(p[1])
    p[0] = (p[1], p[3])


def p_ntterm(p):
    '''ntterm : IDENT COLON numbers'''
    global non_terminals
    non_terminals.append(p[1])
    p[0] = (p[1], p[3])


def p_state(p):
    '''state : STATE DNEWLINE srulelist sactions sactions
             | STATE DNEWLINE srulelist sactions
             | STATE DNEWLINE srulelist DNEWLINE'''

    actions = []

    if isinstance(p[4], list):
        actions.extend([(x, y) for (x, y) in p[4] if y is not None])

    if len(p) >= 6:
        actions.extend([(x, y) for (x, y) in p[5] if y is not None])

    # make a dict of t- and nt-transitions
    t = dict()
    nt = dict()

    for k, v in actions:
        if k in non_terminals:
            nt[k] = v
        else:
            t[k] = v
    p[0] = State(p[1], p[3], t, nt)


# def p_state_no_t(p):
#     '''state : STATE dnewline srulelist dnewline ntrules NEWLINE'''
#     # make a dict of t- and nt-transitions
#     t = dict()
#     nt = dict()
#     for k, v in p[6]:
#         nt[k] = v
#     p[0] = State(p[1], p[2], t, nt)
#
#
# def p_state_no_nt(p):
#     '''state : STATE dnewline srulelist NEWLINE trules NEWLINE'''
#     # make a dict of t- and nt-transitions
#     t = dict()
#     nt = dict()
#     for k, v in p[5]:
#         t[k] = v
#     p[0] = State(p[1], p[2], t, nt)


def p_production(p):
    '''production : IDENT RARROW rhs'''
    p[0] = Production(p[1], p[3])


def p_rhs(p):
    '''rhs : exp erhs'''
    p[0] = [p[1]] + p[2]


def p_srule(p):
    '''srule : LPAREN INT RPAREN production'''
    p[0] = ParseState(p[2], p[4]._rhs.index('.'))


def p_action(p):
    '''trule : IDENT operation
       ntrule : IDENT operation
       action : IDENT operation
              | BANG IDENT LBRACKET operation RBRACKET'''
    if len(p) == 6:
        p[0] = (p[2], None)
    else:
        p[0] = (p[1], p[2])


def p_exp(p):
    '''exp : DOT
           | IDENT'''
    p[0] = p[1]


def p_operation(p):
    '''operation : SHIFT
                 | REDUCE LPAREN production RPAREN'''
    if len(p) == 2:
        p[0] = Shift(p[1])
    else:
        p[0] = Reduce(ParseState(p[1], position=p[3]._rhs.index('.')))


# Error rule for syntax errors
def p_error(p):
    if not p:
        print "End of File!"
        return
    print "Syntax error at token", p.type, "on line", p.lineno
    sys.exit(1)


def p_empty(p):
    '''empty : '''
    pass


parser = yacc.yacc()
