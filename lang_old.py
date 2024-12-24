# This is old code from before I discovered that CodePulse has its own GitHub repository,
# where I can just download the code and modify it to suit my visual preferences and add new things.


##########
# IMPORS #
##########

import string

##########
#  CONS  # 
##########

DIGI = '0123456789'
LETTERS = string.ascii_letters
LETTERSDIGITS = LETTERS + DIGI

#######
# POS #
#######

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

            return self
        
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

##########
# ERRORS #
##########

class Error:
    def __init__(self, posstart, posend, errorname, details):
        self.posstart = posstart
        self.posend = posend
        self.errorname = errorname
        self.details = details
    
    def as_string(self):
        result = f'{self.errorname}: {self.details}'
        result += f'\nFile {self.posstart.fn}, line {str(self.posstart.ln + 1)}'
        return result

class IllegalCharError(Error):
    def __init__(self, posstart, posend, details):
        super().__init__(posstart, posend, 'Illegal Character', details)

class ExpectedCharError(Error):
    def __init__(self, posstart, posend, details): 
        super().__init__(posstart, posend, 'Expected Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, posstart, posend, details): 
        super().__init__(posstart, posend, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, posstart, posend, details, context): 
        super().__init__(posstart, posend, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generatetraceback()
        result += f'{self.errorname}: {self.details}'
        return result

    def generatetraceback(self):
        result = ''
        pos = self.posstart
        ctx = self.context

        while ctx:
            result = f'   File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.displayname}\n' + result
            pos = ctx.parententrypos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result

############
#  TOKENS  #
############

LU_INT = 'INT'
LU_FLOAT = 'FLOAT'
LU_IDENTIFIER = 'IDENTIFIER'
LU_KEYWORD = 'KEYWORD'
LU_MINUS = 'MINUS'
LU_PLUS = 'PLUS'
LU_MUL = 'MUL'
LU_DIV = 'DIV'
LU_POW = 'POW'
LU_EQ = 'EQ'
LU_LPAREN = 'LPAREN'
LU_RPAREN = 'RPAREN'
LU_EE = 'EE'
LU_NE = 'NE'
LU_LT = 'LT'
LU_GT = 'GT'
LU_LTE = 'LTE'
LU_GTE = 'GTE'
LU_EOF = 'EOF'

KEYWORDS = [
    'SET',
    'AND',
    'OR',
    'NOT',
    'IF',
    'THEN',
    'OTHER',
    'ELSE'

]

class Token:
    def __init__(self, type, value=None, posstart=None, posend=None):
        self.type = type
        self.value = value

        if posstart:
            self.posstart = posstart.copy()
            self.posend = posstart.copy()
            self.posend.advance()

        if posend:
            self.posend = posend.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        return f'{self.type}:{self.value}' if self.value else f'{self.type}'
    
#############
#   LEXER   #
#############

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def maketokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGI:
                tokens.append(self.make_int())
            elif self.current_char in LETTERS:
                tokens.append(self.makeidenty())
            elif self.current_char == '+':
                tokens.append(Token(LU_PLUS, posstart=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(LU_MINUS, posstart=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(LU_MUL, posstart=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(LU_DIV, posstart=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(LU_POW, posstart=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(LU_LPAREN, posstart=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(LU_RPAREN, posstart=self.pos))
                self.advance()
            elif self.current_char == '!':
                tok, error = self.makenoteq()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == '=':
                tokens.append(self.makeeq())
                self.advance()
            elif self.current_char == '<':
                tokens.append(self.makelesst())
                self.advance()
            elif self.current_char == '>':
                tokens.append(self.makegreatert())
                self.advance()

            else:
                posstart = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(posstart, self.pos, "'" + char + "'")
        
        tokens.append(Token(LU_EOF, posstart=self.pos))
        return tokens, None
    
    def make_int(self):
        int_str = ''
        dot_count = 0
        postart = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGI + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                int_str += '.'
            else:
                int_str += self.current_char
            self.advance()
        
        if dot_count == 0:
            return Token(LU_INT, int(int_str), postart, self.pos)
        else:
            return Token(LU_FLOAT, float(int_str), postart, self.pos)
        
    def makeidenty(self):
        id_str = ''
        posstart = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERSDIGITS + '_':
            id_str += self.current_char
            self.advance()
        
        toktype = LU_KEYWORD if id_str in KEYWORDS else LU_IDENTIFIER
        return Token(toktype, id_str, posstart, self.pos)
    
    def makenoteq(self):
        posstart = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(LU_NE, posstart, self.pos), None
        
        self.advance()
        return None, ExpectedCharError(posstart, self.pos, "'=' (after '!')" )
    
    def makeeq(self):
        posstart = self.pos.copy()
        toktype = LU_EQ
        self.advance()

        if self.current_char == '=':
            self.advance()
            toktype = LU_EE

        return Token(toktype, posstart, self.pos)
    
    def makelesst(self):
        posstart = self.pos.copy()
        toktype = LU_LT
        self.advance()

        if self.current_char == '=':
            self.advance()
            toktype = LU_LTE

        return Token(toktype, posstart, self.pos)
    
    def makegreatert(self):
        posstart = self.pos.copy()
        toktype = LU_GT
        self.advance()

        if self.current_char == '=':
            self.advance()
            toktype = LU_GTE

        return Token(toktype, posstart, self.pos)



#########
# NODES #
#########

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.posstart = self.tok.posstart
        self.posend = self.tok.posend
    
    def __repr__(self):
        return f'{self.tok}'

class VarAccessNode:
    def __init__(self, varnametok):
        self.varnametok = varnametok

        self.posstart = self.varnametok.posstart
        self.posend = self.varnametok.posend

class VarAssignNode:
    def __init__(self, varnametok, valuenode):
        self.varnametok = varnametok
        self.valuenode = valuenode

        self.posstart = self.varnametok.posstart
        self.posend = self.valuenode.posend



class BinOpNode:
    def __init__(self, lnode, optok, rnode):
        self.lnode = lnode
        self.optok = optok
        self.rnode = rnode

        self.posstart = self.lnode.posstart
        self.posend = self.rnode.posend

    def __repr__(self):
        return f'({self.lnode} {self.optok}, {self.rnode})'

class UnaryOpNode:
    def __init__(self, optok, node):
        self.optok = optok
        self.node = node

        self.posstart = self.optok.posstart
        self.posend = node.posend

    def __repr__(self):
        return f'({self.optok}, {self.node})'


class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.posstart = self.cases[0][0].posstart
		self.posend = (self.else_case or self.cases[len(self.cases) - 1][0]).posend


##############
# PAR RESULT #
##############

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advancecount = 0

    def register_advance(self):
        self.advancecount += 1

    def register(self, res):
        self.advancecount += res.advancecount
        if res.error: self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advancecount == 0:
            self.error = error
        return self




#######
# PAR #
#######

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenidx = -1
        self.advance()

    def advance(self):
        self.tokenidx += 1
        if self.tokenidx < len(self.tokens):
            self.currenttoken = self.tokens[self.tokenidx]
        
        return self.currenttoken
    

    def parse(self):
        res = self.Expr()
        if not res.error and self.currenttoken.type != LU_EOF:
            return res.failure(InvalidSyntaxError(
                self.currenttoken.posstart, self.currenttoken.posend, 
                "Expected '+', '-', '*', '/' or '^'"
            ))
        return res
    
    ######################################


    def IfExpr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.currenttoken.matches(LU_KEYWORD, 'IF'):
            return res.failure(InvalidSyntaxError(
                self.currenttoken.posstart, self.currenttoken.posend,
                f"Expected 'IF'"
            ))

        res.register_advance()
        self.advance()

        condition = res.register(self.Expr())
        if res.error: return res

        if not self.currenttoken.matches(LU_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.currenttoken.posstart, self.currenttoken.posend,
                f"Expected 'THEN'"
            ))

        res.register_advance()
        self.advance()

        expr = res.register(self.Expr())
        if res.error: return res
        cases.append((condition, expr))

        while self.currenttoken.matches(LU_KEYWORD, 'ELIF'):
            res.register_advance()
            self.advance()

            condition = res.register(self.Expr())
            if res.error: return res

            if not self.currenttoken.matches(LU_KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.currenttoken.posstart, self.currenttoken.posend,
                    f"Expected 'THEN'"
                ))

            res.register_advance()
            self.advance()

            Expr = res.register(self.Expr())
            if res.error: return res
            cases.append((condition, Expr))

        if self.currenttoken.matches(LU_KEYWORD, 'ELSE'):
            res.register_advance()
            self.advance()

            else_case = res.register(self.Expr())
            if res.error: return res

        return res.success(IfNode(cases, else_case))
    

    def Atom(self):
        res = ParseResult()
        tok = self.currenttoken

        if tok.type in (LU_INT, LU_FLOAT):
                res.register_advance()
                self.advance()
                return res.success(NumberNode(tok))
        
        if tok.type == LU_IDENTIFIER:
            res.register_advance()
            self.advance()
            return res.success(VarAccessNode(tok))
            
        elif tok.type == LU_LPAREN:
            res.register_advance()
            self.advance()
            expr = res.register(self.Expr())
            if res.error: return res
            if self.currenttoken.type == LU_RPAREN:
                res.register_advance()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
            self.currenttoken.posstart, self.currenttoken.posend, 
            "Expected ')'"
        ))
            
        elif tok.matches(LU_KEYWORD, 'IF'):
            ifExpr = res.register(self.IfExpr())
            if res.error: return res
            return res.success(ifExpr)
            
        return res.failure(InvalidSyntaxError(
            self.currenttoken.posstart, self.currenttoken.posend, 
            "Expected int, float, identyfier, '+', '-', or '("
        ))
    
    def power(self):
        return self.BinOp(self.Atom, (LU_POW, ), self.Factor)


    def Factor(self):
        res = ParseResult()
        tok = self.currenttoken

        if tok.type in (LU_PLUS, LU_MINUS):
            res.register_advance()
            self.advance()
            factor = res.register(self.Factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def Term(self):
        return self.BinOp(self.Factor, (LU_MUL, LU_DIV))
    
    def CompExpr(self):
        res = ParseResult()

        if self.currenttoken.matches(LU_KEYWORD, 'NOT'):
            optok = self.currenttoken
            res.register_advance()
            self.advance()

            node = res.register(self.CompExpr())
            if res.error: return res
            return res.success(UnaryOpNode(optok, node))
        
        node = res.register(self.BinOp(self.ArithExpr, (LU_EE, LU_NE, LU_LT, LU_GT, LU_LTE, LU_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
            self.currenttoken.posstart, self.currenttoken.posend, 
            "Expected int, float, identyfier, '+', '-', '(', 'NOT'"
        ))

        return res.success(node)


    def ArithExpr(self):
        return self.BinOp(self.Term, (LU_PLUS, LU_MINUS))
        

    def Expr(self):
        res = ParseResult()

        if self.currenttoken.matches(LU_KEYWORD, 'SET'):
            res.register_advance()
            self.advance()

            if self.currenttoken.type != LU_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.currenttoken.posstart, 
                    self.currenttoken.posend, 
                    'Expected identifier'
                ))
            
            varname = self.currenttoken
            res.register_advance()
            self.advance()

            if self.currenttoken.type != LU_EQ:
                return res.failure(InvalidSyntaxError(
                    self.currenttoken.posstart, 
                    self.currenttoken.posend, 
                    "Expected '='"
                ))

            res.register_advance()
            self.advance()
            expr = res.register(self.Expr())
            if res.error: return res
            return res.success(VarAssignNode(varname, expr))

        node = res.register(self.BinOp(self.CompExpr, ((LU_KEYWORD, "AND"), (LU_KEYWORD, "OR"))))

        if res.error:
            return res.failure(InvalidSyntaxError(
            self.currenttoken.posstart, self.currenttoken.posend, 
            "Expected int, float, identyfier, 'SET', '+', '-', or '("
        ))

        return res.success(node)

    def BinOp(self, funcA, ops, funcB=None):
        if funcB == None:
            funcB = funcA
        res = ParseResult()
        left = res.register(funcA())
        if res.error: return res

        while self.currenttoken.type in ops or (self.currenttoken.type, self.currenttoken.value) in ops:
            op_tok = self.currenttoken
            res.register_advance()
            self.advance()
            right = res.register(funcB())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

##########
# RT RES #
##########

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self

#######
# VAL #
#######

class Number:
    def __init__(self, value):
        self.value = value
        self.posstart = None
        self.posend = None
        self.setcontext()

    def setpos(self, posstart=None, posend=None):
        self.posstart = posstart
        self.posend = posend
        return self
    
    def setcontext(self, context=None):
        self.context = context
        return self
    
    def addedto(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setcontext(self.context), None
        
    def subbedby(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setcontext(self.context), None
        
    def multedby(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setcontext(self.context), None
        
    def devedby(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.posstart, other.posend, 'Division by zero', self.context)
            return Number(self.value / other.value).setcontext(self.context), None
        
    def powedby(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).setcontext(self.context), None
    
    def getcomp_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).setcontext(self.context), None

    def getcomp_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).setcontext(self.context), None

    def getcomp_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).setcontext(self.context), None

    def getcomp_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).setcontext(self.context), None

    def getcomp_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).setcontext(self.context), None

    def getcomp_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).setcontext(self.context), None

    def andedby(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).setcontext(self.context), None

    def oredby(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).setcontext(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.setpos(self.posstart, self.posend)
        copy.setcontext(self.context)
        return copy
    
    def notted(self):
        return Number(1 if self.value == 0 else 0).setcontext(self.context), None
    
    def IsTrue(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

##########
# CONTEX #
##########

class Context:
    def __init__(self, displayname, parent=None, parententrypos=None):
        self.displayname = displayname
        self.parent = parent
        self.parententrypos = parententrypos
        self.symboltable = None


#############
# SYM TABLE #
#############

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        self.symbols[name] = value
    
    def remove(self, name):
        del self.symbols[name]


#########
# INTER #
#########

class Interpreter:
    def visit(self, node, context):
        methodname = f'visit_{type(node).__name__}'
        method = getattr(self, methodname, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    ######################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
        Number(node.tok.value).setcontext(context).setpos(node.posstart, node.posend))
    
    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        varname = node.varnametok.value
        value = context.symboltable.get(varname)

        if not value:
            return res.failure(RTError(
                node.posstart, node.posend, 
                f"'{varname}' is not defined",
                context
            ))

        value = value.copy().setpos(node.posstart, node.posend)
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        varname = node.varnametok.value
        value = res.register(self.visit(node.valuenode, context))
        if res.error: return res

        context.symboltable.set(varname, value)
        return res.success(value)
        

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.lnode, context))
        if res.error: return res
        right = res.register(self.visit(node.rnode, context))
        if res.error: return res

        if node.optok.type == LU_PLUS:
            result, error = left.addedto(right)
        elif node.optok.type == LU_MINUS:
            result, error = left.subbedby(right)
        elif node.optok.type == LU_MUL:
            result, error = left.multedby(right)
        elif node.optok.type == LU_DIV:
            result, error = left.devedby(right)
        elif node.optok.type == LU_POW:
            result, error = left.powedby(right)
        elif node.optok.type == LU_EE:
            result, error = left.getcomp_eq(right)
        elif node.optok.type == LU_NE:
            result, error = left.getcomp_ne(right)
        elif node.optok.type == LU_LT:
            result, error = left.getcomp_lt(right)
        elif node.optok.type == LU_GT:
            result, error = left.getcomp_gt(right)
        elif node.optok.type == LU_LTE:
            result, error = left.getcomp_lte(right)
        elif node.optok.type == LU_GTE:
            result, error = left.getcomp_gte(right)
        elif node.optok.matches(LU_KEYWORD, 'AND'):
            result, error = left.andedby(right)
        elif node.optok.matches(LU_KEYWORD, 'OR'):
            result, error = left.oredby(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.setpos(node.posstart, node.posend))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.optok.type == LU_MINUS:
            number, error = number.multedby(Number(-1))
        elif node.optok.matches(LU_KEYWORD, 'NOT'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.setpos(node.posstart, node.posend))
        
    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.IsTrue():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)
        
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)
        
        return res.success(None)



##########
#  RUN   #
##########

globalsymboltable = SymbolTable()
globalsymboltable.set("NULL", Number(0))
globalsymboltable.set("TRUE", Number(1))
globalsymboltable.set("FALSE", Number(0))

def run(fn, text):
    # Generate Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.maketokens()
    if error: 
        return None, error

    # Generate AST
    parsr = Parser(tokens)
    ast = parsr.parse()

    if ast.error: return None, ast.error

    # Run Program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symboltable = globalsymboltable
    result = interpreter.visit(ast.node, context)


    # return ast.node, ast.error
    return result.value, result.error
