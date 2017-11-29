import ply.lex as lex

tokens = ('LPAREN', 'RPAREN')

t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_error(t):
    print("Illegal character '%s'" % (t.value[0]))
    t.lexer.skip(1)


lexer = lex.lex()
