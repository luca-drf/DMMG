import ply.lex as lex

reserved = {
    'ann'        : 'ANN',
    'annotation' : 'ANNOTATION',
    'any'        : 'ANY',
    'array'      : 'ARRAY',
    'assert'     : 'ASSERT',
    'bool'       : 'BOOL',
    'case'       : 'CASE',
    'constraint' : 'CONSTRAINT',
    'diff'       : 'DIFF',
    'div'        : 'DIV',
    'else'       : 'ELSE',
    'elseif'     : 'ELSEIF',
    'endif'      : 'ENDIF',
    'enum'       : 'ENUM',
    'false'      : 'FALSE',
    'float'      : 'FLOAT',
    'function'   : 'FUNCTION',
    'in'         : 'IN',
    'include'    : 'INCLUDE',
    'int'        : 'INT',
    'if'         : 'IF',
    'intersect'  : 'INTERSECT',
    'let'        : 'LET',
    'list'       : 'LIST',
    'of'         : 'OF',
    'op'         : 'OP',
    'output'     : 'OUTPUT',
    'minimize'   : 'MINIMIZE',
    'maximize'   : 'MAXIMIZE',
    'mod'        : 'MOD',
    'not'        : 'NOT',
    'par'        : 'PAR',
    'predicate'  : 'PREDICATE',
    'record'     : 'RECORD',
    'satisfy'    : 'SATISFY',
    'set'        : 'SET',
    'solve'      : 'SOLVE',
    'string'     : 'STRING',
    'subset'     : 'SUBSET',
    'superset'   : 'SUPERSET',
    'symdiff'    : 'SYMDIFF',
    'test'       : 'TEST',
    'then'       : 'THEN',
    'true'       : 'TRUE',
    'tuple'      : 'TUPLE',
    'type'       : 'TYPE',
    'union'      : 'UNION',
    'var'        : 'VAR',
    'where'      : 'WHERE',
    'xor'        : 'XOR'
    }

# List of token names.
tokens = [
          # Operators
          'IFF',
          'INTLIT',
          'FLOATLIT',
          'STRLIT',
          'SUF',
          'NEC',
          'DIS',
          'DOUBLECOL',
          'QUOT',
          'CON',
          'LEQ',
          'GEQ',
          'EQ',
          'DIF',
          'DOTS',
          'PP',
          'RARROW',
          'IDENT'
         ] + list(reserved.values())


literals = [ '-','<','>','=','+','*','/',';',':',',','.','_',
             '(',')','[',']','{','}','|' ]

# Operators
t_QUOT      = r'\''
t_DOUBLECOL = r'::'
t_EQ        = r'=='
t_LEQ       = r'<='
t_GEQ       = r'>='
t_DIF       = r'!='
t_SUF       = r'->'
t_NEC       = r'<-'
t_IFF       = r'<->'
t_CON       = r'/\\'
t_RARROW    = r'-->'
t_DOTS      = r'\.\.'
t_PP        = r'\+\+'
t_DIS       = r'\\/'
t_INTLIT    = r'0x[0-9A-Fa-f]+|0o[0-7]+|[0-9]+'
t_FLOATLIT  = r'[0-9]+\.[0-9]+[Ee][-+]?[0-9]+|[0-9]+[Ee][-+]?[0-9]+|[0-9]+\.[0-9]+'
t_STRLIT    = r'"[^"\n]*"'
t_ignore    = ' \t'


# No return value. Token discarded
def t_COMMENT(t):
    r'\%.*'
    pass


# Check for reserved words
def t_IDENT(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value,'IDENT')
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
