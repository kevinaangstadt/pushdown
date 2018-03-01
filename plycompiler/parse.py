import ply.yacc as yacc

# get the token map from the lexer
from lex import tokens

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


def p_file(p):
    '''file : anythinglist GRAMMAR dnewline rulelist NEWLINE TLIST dnewline tlist NEWLINE NTLIST dnewline ntlist NEWLINE PMETHOD dnewline statelist'''
    terms = [x for (x, _) in p[8]]
    nterms = [x for (x, _) in p[12]]

    p[0] = Pushdown(p[14], terms, nterms)

    for r in p[4]:
        p[0].add_rule(r)
    for s in p[16]:
        p[0].add_state(s)
    for k, v in p[8]:
        p[0].add_t(k, v)
    for k, v in p[12]:
        p[0].add_nt(k, v)


def p_dnewline(p):
    '''dnewline : NEWLINE NEWLINE'''
    pass


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
                 | TERMINAL
                 | NONTERMINAL
                 | INT
                 | COLON
                 | LPAREN
                 | RPAREN
                 | DOT
                 | NEWLINE'''
    pass


# We'll simplify things by having a single rule for all our list productions
def p_list(p):
    '''rulelist  : rule NEWLINE rulelist
                 | empty
       tlist     : tterm NEWLINE tlist
                 | empty
       ntlist    : ntterm NEWLINE ntlist
                 | empty
       statelist : state NEWLINE statelist
                 | empty
       numbers   : INT numbers
                 | empty
       srulelist : srule NEWLINE srulelist
                 | empty
       trules   : trule NEWLINE trules
                 | empty
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


# def p_forced_list(p):
#     '''trules  : trule etrules
#        ntrules : ntrule entrules'''
#     p[0] = [p[1]] + p[2]


def p_rule(p):
    '''rule : RULE production'''
    p[0] = Rule(p[1], p[2]._lhs, p[2]._rhs)


def p_tterm(p):
    '''tterm : TERMINAL COLON numbers'''
    p[0] = (p[1], p[3])


def p_ntterm(p):
    '''ntterm : NONTERMINAL COLON numbers'''
    p[0] = (p[1], p[3])


def p_state(p):
    '''state : STATE dnewline srulelist NEWLINE trules NEWLINE ntrules'''
    # make a dict of t- and nt-transitions
    t = dict()
    nt = dict()
    for k, v in p[5]:
        t[k] = v
    for k, v in p[7]:
        nt[k] = v
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
    '''production : NONTERMINAL RARROW rhs'''
    p[0] = Production(p[1], p[3])


def p_rhs(p):
    '''rhs : exp erhs'''
    p[0] = [p[1]] + p[2]


def p_srule(p):
    '''srule : LPAREN INT RPAREN production'''
    p[0] = ParseState(p[2], p[4]._rhs.index('.'))


def p_trule(p):
    '''trule : TERMINAL operation'''
    p[0] = (p[1], p[2])


def p_ntrule(p):
    '''ntrule : NONTERMINAL operation'''
    p[0] = (p[1], p[2])


def p_exp(p):
    '''exp : DOT
           | TERMINAL
           | NONTERMINAL'''
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
        print "Endo of File!"
        parser.errok()
    print "Syntax error at token", p.type, "on line", p.lineno
    parser.errorok()


def p_empty(p):
    '''empty : '''
    pass


parser = yacc.yacc()
