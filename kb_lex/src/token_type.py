from enum import IntEnum

class TokenType(IntEnum):
    # Служебные операторы (1-7)
    INT = 1
    FLOAT = 2
    IF = 3
    ELSE = 4
    WHILE = 5
    OUTPUT = 6
    INPUT = 7

    # Идентификаторы (10)
    IDENTIFIER = 10

    # Константы (11-12)
    INTEGER_CONST = 11
    FLOAT_CONST = 12

    # Скобки, разделители (20-28)
    LPAREN = 20      # (
    RPAREN = 21      # )
    LSQUARE = 22     # [
    RSQUARE = 23     # ]
    LCURLY = 24      # {
    RCURLY = 25      # }
    SEMICOLON = 26   # ;
    COMMA = 27       # ,
    DOT = 28         # .

    # Операторы (30-41)
    PLUS = 30        # +
    MINUS = 31       # -
    MULTIPLY = 32    # *
    DIVIDE = 33      # /
    ASSIGN = 34      # =
    LT = 35         # <
    GT = 36         # >
    NEQ = 37        # !
    EQ = 38         # ?
    AND = 39        # &
    OR = 40         # |
    UNARY_MINUS = 41 # ~

    # Специальные символы (90-100)
    WHITESPACE = 90
    NEWLINE = 91
    EOF = 99
    ERROR = 100