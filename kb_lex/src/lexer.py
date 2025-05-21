from .state import State
from .token_1 import Token
from .token_type import TokenType


OPERATORS = {
    '+': TokenType.PLUS,      # 30
    '-': TokenType.MINUS,     # 31
    '*': TokenType.MULTIPLY,  # 32
    '/': TokenType.DIVIDE,    # 33
    '=': TokenType.ASSIGN,    # 34
    '<': TokenType.LT,        # 35
    '>': TokenType.GT,        # 36
    '!': TokenType.NEQ,       # 37
    '?': TokenType.EQ,        # 38
    '&': TokenType.AND,       # 39
    '|': TokenType.OR,        # 40
    '~': TokenType.UNARY_MINUS, # 41
    '(': TokenType.LPAREN,    # 20
    ')': TokenType.RPAREN,    # 21
    '[': TokenType.LSQUARE,   # 22
    ']': TokenType.RSQUARE,   # 23
    '{': TokenType.LCURLY,    # 24
    '}': TokenType.RCURLY,    # 25
    ';': TokenType.SEMICOLON, # 26
    ',': TokenType.COMMA,     # 27

}


KEYWORDS = {
    'int': TokenType.INT,     # 1
    'float': TokenType.FLOAT, # 2
    'if': TokenType.IF,       # 3
    'else': TokenType.ELSE,   # 4
    'while': TokenType.WHILE, # 5
    'output': TokenType.OUTPUT, # 6
    'input': TokenType.INPUT   # 7
}


def analyze(input_string):
    tokens = []         
    line = 1   
    state = State.S
    buffer = ""  
    position = 0        
    start_position = 0  
    input_string += '\0'  
    i = 0

    def add_token(token_type, start_position, value=""):
        tokens.append(Token(token_type, value, line, start_position))

    while i < len(input_string):
        c = input_string[i]
        
        if state == State.S:
            start_position = position
            if c.isalpha():
                state = State.A
                buffer = c
            elif c.isdigit(): 
                state = State.B
                buffer = c
            elif c in OPERATORS: 
                add_token(OPERATORS[c],start_position, c)
                state = State.S
            elif c in [' ', '\t']:  
                state = State.S
            elif c == '\n': 
                line += 1
                position = 0
                state = State.S
            elif c == '\0': 
                add_token(TokenType.EOF,start_position)
                break
            else:  
                raise RuntimeError(f"Неизвестный символ '{c}' в строке {line}, позиция {position+1}")

        elif state == State.A:
            if c.isalnum():  
                buffer += c
            elif c == '.' or c == '~':
                raise RuntimeError(f"Недопустимый символ '{c}' после идентификатора/ключевого слова в строке {line}, позиция {position+1}")
            else:  
                token_type = KEYWORDS.get(buffer, TokenType.IDENTIFIER)
                add_token(token_type,start_position, buffer)
                buffer = ""
                state = State.S
                continue  

        elif state == State.B: 
            if c.isdigit():  
                buffer += c
            elif c == '.': 
                buffer += c
                state = State.C
            elif c.isalpha() or c == '{' or c == '~':
                raise RuntimeError(f"Недопустимый символ '{c}' после целого числа в строке {line}, позиция {position+1}")
            else:  
                add_token(TokenType.INTEGER_CONST,start_position, buffer)
                buffer = ""
                state = State.S
                continue 

        elif state == State.C:
            if c.isdigit():  
                buffer += c
                state = State.D
            else:
                raise RuntimeError(f"Ожидалась цифра после точки в строке {line}, позиция {position+1}")

        elif state == State.D: 
            if c.isdigit():
                buffer += c
            elif c == '.' or c == '{' or c == '~' or c.isalpha():
                raise RuntimeError(f"Недопустимый символ '{c}' после дробной части числа в строке {line}, позиция {position+1}")
            else:
                add_token(TokenType.FLOAT_CONST,start_position, buffer)
                buffer = ""
                state = State.S
                continue  

        elif state == State.Z: 
            raise RuntimeError(f"Лексическая ошибка в строке {line}, позиция {position+1}")

        i += 1
        position += 1

    return tokens