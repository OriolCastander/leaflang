"""
Words are part of sentences, can be simple mentions like a className or VariableName, or functionCalls
"""

from typing import Union

from src.tokenizer.token import Token, TokenKind

from src.utils import OperatorKind


class Mention: #?? (str):
    """
    A mention is a wrapper around the string, to represent variableNames, classNames...
    This distinction is to differentiate with the plain string, the one surrounded with quotes
    """
    
    def __init__(self, value: str) -> None:
        self.value: str = value


    def __repr__(self) -> str:
        return f"{self.value}"





class Chain:
    """Chain of stuff"""
    def __init__(self, elements: list[Union[str, int, float, bool, Mention, "LeafFunctionCallWord"]]):

        self.elements: list[str | int | float | bool | Mention | LeafFunctionCallWord] = elements

    def __repr__(self) -> str:
        return f"Chain: {self.elements}"



class Operator:



    @staticmethod
    def tokenToOperatorKind(token: Token) -> OperatorKind:
        if token.kind == TokenKind.PLUS:
            return OperatorKind.SUM
        elif token.kind == TokenKind.OPEN_ANG:
            return OperatorKind.LESS_THAN
        elif token.kind == TokenKind.CLOSE_ANG:
            return OperatorKind.GREATER_THAN
        else:
            raise Exception(f"Invalid operator token {token}")

    
    
    def __init__(self, operatorKind: OperatorKind, left: Union[Chain, "Operator"], right: Union[Chain, "Operator"]):
        
        self.operatorKind: OperatorKind = operatorKind
        self.left: Chain | Operator = left
        self.right: Chain | Operator = right

    def __repr__(self) -> str:
        return f"Operator: ({self.left}) {self.operatorKind} ({self.right})"





class LeafFunctionCallWord:
    """
    Function call
    TODO: leafFunction is a Mention, but it should be a Chain of stuff
    """
    def __init__(self, leafFunction: Mention, generics: list[Chain],arguments: list[Chain | Operator]) -> None:
        
        self.leafFunction: Mention = leafFunction
        self.generics: list[Chain] = generics
        self.arguments: list[Chain | Operator] = arguments


    def __repr__(self) -> str:
        return f"LeafFunctionCallWord: {self.leafFunction}({self.arguments})"



class Declaration:
    """
    A declaration is a mention with a class descriptor, e.g: x: List<int>
    """
    def __init__(self, mention: Mention, leafClassDescriptor: Chain, generics: list[Chain]) -> None:
        self.mention: Mention = mention
        self.leafClassDescriptor: Chain = leafClassDescriptor
        self.generics: list[Chain] = generics


    def __repr__(self) -> str:
        return f"{self.mention}: {self.leafClassDescriptor} <{self.generics}>"



