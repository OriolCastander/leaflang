
import abc
import src.parser.words as words

from src.utils import ALLOCATION

class Sentence(abc.ABC):
    
    def __init__(self, line: int) -> None:

        self.line: int = line



    @abc.abstractmethod
    def __repr__(self) -> str:
        pass





class LeafVariableDeclaration(Sentence):
    """
    A variable declaration
    """
    def __init__(self, line: int, declaration: words.Declaration, allocation: ALLOCATION) -> None:
        super().__init__(line)

        self.declaration: words.Declaration = declaration



    def __repr__(self) -> str:
        return f"LeafVariableDeclaration: {self.declaration}"
    




class LeafClassDeclaration(Sentence):
    """
    A class declaration
    """

    def __init__(self, line: int, name: words.Mention, generics: list[words.Chain]) -> None:
        super().__init__(line)

        self.name: words.Mention = name
        self.generics: list[words.Chain] = generics


    def __repr__(self) -> str:
        return f"LeafClassDeclaration: {self.name} <{self.generics}>"





class LeafFunctionDeclaration(Sentence):
    """
    A function declaration
    """

    def __init__(self, line: int, name: words.Mention, generics: list[words.Chain], parameters: list[words.Declaration], returnLeafClass: words.Chain) -> None:
        super().__init__(line)

        self.name: words.Mention = name
        self.generics: list[words.Chain] = generics
        self.parameters: list[words.Declaration] = parameters
        self.returnLeafClass: words.Chain = returnLeafClass


    def __repr__(self) -> str:
        return f"LeafFunctionDeclaration: {self.name} <{self.generics}>({self.parameters}) -> {self.returnLeafClass}"




class NakedLeafFunctionCall(Sentence):
    """A simple function call with no return value (or not set to anyting), like print("Hello"). Last element of chain should be a function call"""
    def __init__(self, line: int, chain: words.Chain) -> None:
        super().__init__(line)

        self.chain: words.Chain = chain


    def __repr__(self) -> str:
        return f"NakedLeafFunctionCall: {self.chain}"




class Assignment(Sentence):
    """
    Stuff like x = 3.
    """

    def __init__(self, line: int, assignee: words.Chain, value: words.Chain | words.Operator) -> None:
        super().__init__(line)

        self.assignee: words.Mention = assignee
        self.value: words.Chain | words.Operator = value

    def __repr__(self) -> str:
        return f"Assignment: {self.assignee} = {self.value}"




class ScopeClosure(Sentence):
    """
    A scope closure
    """
    def __init__(self, line: int) -> None:
        super().__init__(line)


    def __repr__(self) -> str:
        return f"ScopeClosure"
