import ply.yacc as yacc
from lexer import tokens


def p_bracket(p):
    '''s : LPAREN s RPAREN
         | '''
    pass


parser = yacc.yacc()
