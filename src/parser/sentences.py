
import abc
import src.parser.words as words

from src.utils import ALLOCATION, PASSING

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
        self.allocation: ALLOCATION = allocation
        ##self.passing: PASSING = passing IN the future, currently decided by the class


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

        self.assignee: words.Chain = assignee
        self.value: words.Chain | words.Operator = value

    def __repr__(self) -> str:
        return f"Assignment: {self.assignee} = {self.value}"




class ReturnSentence(Sentence):
    """
    A return statement
    """
    def __init__(self, line: int, value: words.Chain | words.Operator) -> None:
        super().__init__(line)

        self.value: words.Chain | words.Operator = value

    def __repr__(self) -> str:
        return f"ReturnSentence: {self.value}"



class ScopeClosure(Sentence):
    """
    A scope closure
    """
    def __init__(self, line: int) -> None:
        super().__init__(line)


    def __repr__(self) -> str:
        return f"ScopeClosure"
    


class ScopeOpening(Sentence):
    """
    A simple scope opening without an if or function or while or anything
    """

    def __init__(self, line: int) -> None:
        super().__init__(line)

    def __repr__(self) -> str:
        return f"ScopeOpening"
        




class LeafIfStatement(Sentence):
    """
    A simple if statement
    """
    def __init__(self, line: int, condition: words.Operator) -> None:
        super().__init__(line)

        self.condition: words.Operator = condition


    def __repr__(self) -> str:
        return f"LeafIfStatement: {self.condition}"
    



class LeafWhileStatement(Sentence):
    """
    A simple while statement
    """
    def __init__(self, line: int, condition: words.Operator) -> None:
        super().__init__(line)

        self.condition: words.Operator = condition


    def __repr__(self) -> str:
        return f"LeafWhileStatement: {self.condition}"
