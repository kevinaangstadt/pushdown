# ----------------------------------------------------------------------------
# lex.py
#
# tokenizer for the PLY parser.out compiler
# ----------------------------------------------------------------------------

import ply.lex as lex

# List of token names
tokens = ('RULE', 'STATE', 'GRAMMAR', 'TLIST', 'NTLIST', 'PMETHOD', 'SHIFT',
          'REDUCE', 'RARROW', 'TERMINAL', 'NONTERMINAL', 'INT', 'COLON',
          'LPAREN', 'RPAREN', 'DOT', 'NEWLINE')

# keep track if we've not seen the EOF yet
_lex_first_time = True


def t_RULE(t):
    r'Rule[ ](?P<rule>\d+)'
    t.value = int(t.lexer.lexmatch.group('rule'))
    return t


def t_HEADER(t):
    r"Created[ ]by[ ]PLY[ ]version[ ]\d+\.\d+[ ]\([a-zA-z0-9_:/.%]+\)"
    pass


def t_STATE(t):
    r'state[ ](?P<state>\d+)'
    t.value = int(t.lexer.lexmatch.group('state'))
    return t


def t_GRAMMAR(t):
    r'Grammar\b'
    return t


def t_TLIST(t):
    r'Terminals,[ ]with[ ]rules[ ]where[ ]they[ ]appear'
    return t


def t_NTLIST(t):
    r'Nonterminals,[ ]with[ ]rules[ ]where[ ]they[ ]appear'
    return t


def t_PMETHOD(t):
    r'Parsing[ ]method:[ ](?P<method>LALR|SLR)'
    t.value = t.lexer.lexmatch.group('method')
    return t


def t_SHIFT(t):
    r'shift[ ]and[ ]go[ ]to[ ]state[ ](?P<shift>\d+)'
    t.value = int(t.lexer.lexmatch.group('shift'))
    return t


def t_REDUCE(t):
    r'reduce[ ]using[ ]rule[ ](?P<reduce>\d+)'
    t.value = int(t.lexer.lexmatch.group('reduce'))
    return t


def t_UNUSED(t):
    r'Unused[ ]terminals:|Unused[ ]nonterminals:'
    pass


def t_RARROW(t):
    r'->'
    return t


def t_NONTERMINAL(t):
    r"S'|([a-z]\w*)"
    if t.value == "error":
        t.type = 'TERMINAL'
    return t


def t_TERMINAL(t):
    r'(\$end)|<empty>|([A-Z]\w*)'
    return t


def t_INT(t):
    r'\d'
    t.value = int(t.value)
    return t


def t_COLON(t):
    r':'
    return t


def t_LPAREN(t):
    r'\('
    return t


def t_RPAREN(t):
    r'\)'
    return t


def t_DOT(t):
    r'\.'
    return t


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    return t


def t_WHITESPACE(t):
    r'[ \t]+'
    pass


def t_eof(t):
    # if this is the first time we've seen the end of the file,
    # we'll return a newline instead
    global _lex_first_time
    if _lex_first_time:
        t.type = 'NEWLINE'
        t.value = '\n'
        _lex_first_time = False
        return t
    else:
        return None


# Error handling rule
def t_error(t):
    print("Illegal character '%s' on line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)


# build the lexer
lexer = lex.lex()
