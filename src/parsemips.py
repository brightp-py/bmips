import ply.lex as lex
import ply.yacc as yacc

import contextlib, sys, re
from io import StringIO

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

from src import container as con
from src.mips_const import REGISTERS, INSTRUCTIONS, SUPPLEMENT

DEBUGPRINT = False

def printd(*s):
    if DEBUGPRINT:
        print(' '.join(map(str, s)))

tokens = [
    'START',
    'COMMENT',
    'GLOBL',
    'PREGEN',
    'STRING',
    'REGISTER',
    'INSTR',
    'CONSTANT',
    'LABEL',
    # 'VLABEL',
    'LABELREF',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'COLON'
]

t_ignore = ' \t\n\r'

t_START =       '[#]\sstandard\sDecaf\spreamble\s'
t_COMMENT =     '[#].*'
t_GLOBL =       '\.globl\s[_a-zA-Z][_a-zA-Z0-9]+'
t_PREGEN =      '\.[a-z]+'
# t_STRING =      '\"[^"]*\"'
t_REGISTER =    '\$(([a-z][a-z0-9])|0)'
# t_INSTR =       '[a-z]+'
t_CONSTANT =    '-?[0-9]+'
# t_LABEL =       '[_a-zA-Z][_a-zA-Z0-9]+'
# t_VLABEL =      '[_a-zA-Z][_a-zA-Z0-9]+\.[_a-zA-Z0-9]+'
t_LABELREF =    '[_a-zA-Z][_a-zA-Z0-9]+(\.[_a-zA-Z0-9]+)?'
t_LPAREN =      '\('
t_RPAREN =      '\)'
t_COMMA =       ','
t_COLON =       ':'

def t_STRING(t):
    '\"[^"]*\"'
    with stdoutIO() as s:
        exec(f"print({t.value})")
    t.value = s.getvalue()[:-1]
    for i in INSTRUCTIONS:
        inst = i.lower()
        t.value = re.sub(f" ~{inst} ", f" {inst} ", t.value)
        t.value = re.sub(f" ~{inst}\n", f" {inst}\n", t.value)
    return t

def t_LABEL(t):
    '[_a-zA-Z][_a-zA-Z0-9]+(\.[_a-zA-Z0-9]+)?:'
    # print(t.value)
    return t

def t_INSTR(t):
    '~[a-z]+'
    t.value = t.value[1:]
    return t

# def t_PREAMBLE(t):
#     '\.globl [_a-zA-Z][_a-zA-Z0-9]+'
#     printd('p:', t)
#     return t

def t_error(t):
    print(f"Illegal character '{str(t.value[0])}'")
    t.lexer.skip(1)

lexer = lex.lex()

precedence = ()

# def p_comment(p):
#     'comment : COMMENT'
#     print(p[1])

def p_startprogram(p):
    'program : START'
    printd("Program start!", p[1])
    p[0] = con.Program()

def p_addcomment(p):
    'program : program COMMENT'
    p[0] = p[1]

def p_pre(p):
    '''pre : PREGEN
           | PREGEN STRING
           | PREGEN CONSTANT
           | PREGEN LABELREF
           | GLOBL'''
    p[0] = p[1:]
    printd('P:', p[0])

def p_constarg(p):
    'arg : CONSTANT'
    p[0] = (int(p[1]), REGISTERS[0])
    printd('C:', p[0])

def p_regarg(p):
    'arg : REGISTER'
    p[0] = (0, p[1])
    printd('R:', p[0])

def p_parentregarg(p):
    'arg : LPAREN REGISTER RPAREN'
    p[0] = (0, p[2])
    printd('R:', p[0])

def p_labelarg(p):
    'arg : LABELREF'
    p[0] = p[1]
    printd('A:', p[0])

def p_offsetarg(p):
    'arg : CONSTANT LPAREN arg RPAREN'
    p[0] = (int(p[1]), p[3][1])
    printd('O:', p[0])

def p_line(p):
    '''line : INSTR arg COMMA arg COMMA arg
            | INSTR arg COMMA arg
            | INSTR arg
            | INSTR'''
    
    p[0] = [p[1]]
    if len(p) > 1:
        p[0].append(p[2::2])
    printd('L:', p[0])

def p_addline(p):
    'program : program line'
    p[0] = p[1]
    p[0].addLine(p[2])
    printd('+L', p[2])

def p_addlabel(p):
    'program : program LABEL'
    p[0] = p[1]
    p[0].addLabel(p[2][:-1])
    printd('+A', p[2])

def p_addpre(p):
    'program : program pre'
    p[0] = p[1]
    p[0].addPregen(p[2])
    printd('+P', p[2])

def p_error(p):
    print("Syntax error in input!")
    print(p)

parser = yacc.yacc()

def parseCode(code):
    code += SUPPLEMENT
    
    for i in INSTRUCTIONS:
        inst = i.lower()
        code = re.sub(f" {inst} ", f" ~{inst} ", code)
        code = re.sub(f" {inst}\n", f" ~{inst}\n", code)

    # return parser.parse(code, debug = True)
    program = parser.parse(code)
    program.resolvePregen()
    return program

if __name__ == "__main__":
    with open("t5.s", 'r') as f:
        text = f.read()
    
    result = parseCode(text)

    if result:
        for l in result.lines:
            print(l)
        
        for a in result.labels:
            print(a, result.labels[a], '\t(', result.lines[result.labels[a]], ')')