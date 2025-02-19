

from enum import IntEnum

class TokenKind(IntEnum):
    STRING = 0
    NUMBER = 1
    EQUALS = 2
    COMMA = 3
    DOT = 4
    COLON = 5
    SEMICOLON = 6
    OPEN_PAR = 7 #(
    CLOSE_PAR = 8
    OPEN_BRA = 9 #[
    CLOSE_BRA = 10
    OPEN_CUR = 11 #{
    CLOSE_CUR = 12
    OPEN_ANG = 13 #<
    CLOSE_ANG = 14

    PLUS = 15
    QUOTES = 16 #"
    PIPE = 17 # | 
    AND = 18 # &
    PERCENT = 19 # %
    MINUS = 20 # -


class Token:
    """
    A token. Represents a "word", number or special character
    """

    def __init__(self, kind: TokenKind, value: None | str, line: int) -> None:
        self.kind: TokenKind = kind
        self.value: None | str = value
        self.line: int = line

    def __repr__(self) -> str:
        string =  f" {self.kind.name}"
        if self.value is not None:
            string += f" {self.value}"
        return string