
"""
The tokenizer transforms the chars in the file to a list of tokens
"""

from enum import IntEnum

from src.tokenizer.token import Token, TokenKind


    

class _TokenizerState(IntEnum):
    NEUTRAL = 0
    CONSUMING_STRING = 1
    CONSUMING_NUMBER = 2




class Tokenizer:
    """
    tokenize function transforms the chars in the file to a list of tokens
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.tokens: list[Token] = []
        self.state: _TokenizerState = _TokenizerState.NEUTRAL
        self.currentString: str = ""
        self.currentNumber: str = ""

    def tokenize(self, string: str) -> list[Token]:
        """Returns the list of tokens from a string (the .lf file)"""
        self.reset()

        line: int = 1

        for char in string:
            if char == "\n": line += 1
            elif char == "\t": pass
            else: self._consumeChar(char, line)

        return self.tokens
    
    def _consumeChar(self, char: str, line: int) -> None:

        if self.state == _TokenizerState.NEUTRAL:
            potentialToken = self._consumeNeutral(char, line)
            if potentialToken is not None: self.tokens.append(potentialToken)

        elif self.state == _TokenizerState.CONSUMING_STRING:
            potentialTokens: None | tuple[Token, None | Token] = self._consumeString(char, line)
            if potentialTokens is not None:
                self.tokens.append(potentialTokens[0])
                if potentialTokens[1] is not None: self.tokens.append(potentialTokens[1])

        elif self.state == _TokenizerState.CONSUMING_NUMBER:
            potentialTokens: None | tuple[Token, None | Token] = self._consumeNumber(char, line)
            if potentialTokens is not None:
                self.tokens.append(potentialTokens[0])
                if potentialTokens[1] is not None: self.tokens.append(potentialTokens[1])

        else:
            raise Exception(f"Tokenizer error: Unknown state {self.state.name}")

    
    def _consumeNeutral(self, char: str, line: int) -> Token | None:
        if char.isnumeric():
            self.state = _TokenizerState.CONSUMING_NUMBER
            self.currentNumber += char
            return None
        
        if char.isalpha() or char == "_":
            self.state = _TokenizerState.CONSUMING_STRING
            self.currentString += char
            return None

        if char == " ": return None
        if char == "=": return Token(TokenKind.EQUALS, None, line)
        if char == ":": return Token(TokenKind.COLON, None, line)
        if char == ";": return Token(TokenKind.SEMICOLON, None, line)
        if char == ",": return Token(TokenKind.COMMA, None, line)
        if char == "(": return Token(TokenKind.OPEN_PAR, None, line)
        if char == ")": return Token(TokenKind.CLOSE_PAR, None, line)
        if char == "[": return Token(TokenKind.OPEN_BRA, None, line)
        if char == "]": return Token(TokenKind.CLOSE_BRA, None, line)
        if char == "{": return Token(TokenKind.OPEN_CUR, None, line)
        if char == "}": return Token(TokenKind.CLOSE_CUR, None, line)
        if char == "<": return Token(TokenKind.OPEN_ANG, None, line)
        if char == ">": return Token(TokenKind.CLOSE_ANG, None, line)
        if char == ".": return Token(TokenKind.DOT, None, line)
        if char == "+": return Token(TokenKind.PLUS, None, line)
        if char == "\"": return Token(TokenKind.QUOTES, None, line)
        if char == "|": return Token(TokenKind.PIPE, None, line)
        if char == "&": return Token(TokenKind.AND, None, line)
        if char == "%": return Token(TokenKind.PERCENT, None, line)

        raise Exception(f"Character {char} in line {line} is not allowed")


    def _consumeString(self, char: str, line: int) -> None | tuple[Token, None | Token]:
        
        if char.isalnum() or char == "_":
            self.currentString += char
            return None
                
        else:
            string = self.currentString
            self.currentString: str = ""
            self.state = _TokenizerState.NEUTRAL
            return (Token(TokenKind.STRING, string, line), self._consumeNeutral(char, line))
        
    
    def _consumeNumber(self, char: str, line: int) -> None | tuple[Token, None | Token]:
        if char.isnumeric():
            self.currentNumber += char

        elif char == ".":
            if "." in self.currentNumber:
                raise Exception(f"Tokenizer error in line {line}. Numeric value {self.currentNumber} already has a decimal point.")
            else:
                self.currentNumber += "."

        elif char.isalpha():
            raise Exception(f"Tokenizer error in line {line}. Cannot continue number declaration {self.currentNumber} with alphabetic character {char}")
        
        else:
            string = self.currentNumber
            self.currentNumber: str = ""
            self.state = _TokenizerState.NEUTRAL
            return (Token(TokenKind.NUMBER, string, line), self._consumeNeutral(char,line))