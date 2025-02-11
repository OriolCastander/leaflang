"""
Structures that live inside nodes
"""
from typing import Callable, Any, Union
import abc


from src.utils import ALLOCATION, PASSING, OperatorKind





class LeafClass:
    """Representation of a leaf class"""

    def __init__(self, name: str, generics: list[str], allocation: ALLOCATION, passing: PASSING) -> None:
        
        self.name: str = name
        self.generics: list[str] = generics
        self.allocation: ALLOCATION = allocation
        self.passing: PASSING = passing

        self.cName: str = None
        self.constructor: LeafFunction = None

        self.properties: dict[str, LeafMention] = {}
        self.methods: dict[str, LeafFunction] = {}

        self.operators: dict[OperatorKind, LeafFunction] = {}



    def getOperator(self, operatorKind: OperatorKind) -> Union["LeafFunction", None]:
        return self.operators.get(operatorKind, None)





class LeafMention:
    """Representation of a leaf mention, aka, a variable declaration, parameter, etc."""

    def __init__(self, name: str | None, leafClass: LeafClass, generics: list[LeafClass], allocation: ALLOCATION | None = None, passing: PASSING | None = None) -> None:
        
        self.name: str | None = name
        self.leafClass: LeafClass = leafClass
        self.generics: list[LeafClass] = generics
        self.allocation: ALLOCATION = allocation if allocation is not None else leafClass.allocation
        self.passing: PASSING = passing if passing is not None else leafClass.passing

        self.cName: str | None = None




class LeafFunction:
    """Representation of a leaf function"""

    def __init__(self, name: str, generics: list[str], parameters: list[LeafMention], ret: LeafMention) -> None:
        
        self.name: str = name
        self.generics: list[str] = generics
        self.parameters: list[LeafMention] = parameters
        self.ret: LeafMention = ret

        self.methodOf: LeafClass | None = None
        self.constructorOf: LeafClass | None = None
        self.customSignature: Callable | None = None

        self.cName: str | None = None

        self.isMain: bool = False






class LeafValue(abc.ABC):
    """Either a leaf chain or a leaf operator"""

    @abc.abstractmethod
    def write(self, selfString: str | None = None) -> str:
        pass


    @abc.abstractmethod
    def getFinalLeafClass(self) -> LeafClass:
        pass


    @abc.abstractmethod
    def getFinalAllocation(self) -> ALLOCATION:
        pass

    @abc.abstractmethod
    def getFinalPassing(self) -> PASSING:
        pass






class LeafChain(LeafValue):
    """
    A chain of variables and function calls
    TODO: might also be native stuff, like ints and stuff
    """

    def __init__(self, elements: list[Union[LeafMention, "LeafFunctionCall", int, float, str, bool]]) -> None:
        
        self.elements: list[LeafMention | LeafFunctionCall | int | float | str, bool] = elements

    
    def write(self, selfString: str | None = None) -> str:
        """Returns the C code for the chain"""
        ##ugly as hell but I dont give a fuck
        import src.writer.valueWriter as valueWriter
        return valueWriter.writeLeafChain(self, selfString)
        


    def getFinalLeafClass(self) -> LeafClass:
        """Returns the leaf class of the final element of the chain"""


        if type(self.elements[-1]) == LeafFunctionCall:
            return self.elements[-1].leafFunction.ret.leafClass
        
        elif type(self.elements[-1]) == LeafMention:
            return self.elements[-1].leafClass
        
        elif type(self.elements[-1]) == int:
            ##ugly as hell but I dont give a fuck
            from src.base import BASE_CLASSES
            return BASE_CLASSES.INT_CLASS
        
        else:
            raise NotImplementedError(f"Invalid type {type(self.elements[-1])}")
        

    def getFinalAllocation(self) -> ALLOCATION:
        """Returns the allocation of the final element of the chain"""

        if type(self.elements[-1]) == LeafFunctionCall:
            return self.elements[-1].leafFunction.ret.allocation
        
        elif type(self.elements[-1]) == LeafMention:
            return self.elements[-1].allocation
        
        elif type(self.elements[-1]) == int:
            return ALLOCATION.STACK
        
        else:
            raise NotImplementedError(f"Invalid type {type(self.elements[-1])}")
        

    def getFinalPassing(self) -> PASSING:
        """Returns the passing of the final element of the chain"""

        if type(self.elements[-1]) == LeafFunctionCall:
            return self.elements[-1].leafFunction.ret.passing
        
        elif type(self.elements[-1]) == LeafMention:
            return self.elements[-1].passing
        
        elif type(self.elements[-1]) == int:
            return PASSING.VALUE
        
        else:
            raise NotImplementedError(f"Invalid type {type(self.elements[-1])}")
        


class LeafOperator(LeafValue):
    """A leaf operator"""

    def __init__(self, operatorKind: OperatorKind, leafFunction: LeafFunction, left: LeafValue, right: LeafValue) -> None:
        self.operatorKind: OperatorKind = operatorKind
        self.leafFunction: LeafFunction = leafFunction
        self.left: LeafValue = left
        self.right: LeafValue = right

        self.leafFunctionCall: LeafFunctionCall = LeafFunctionCall(self.leafFunction, [], [self.left, self.right])


    def write(self, selfString: str | None = None) -> str:
        """Returns the C code for the operator"""
        return LeafChain([self.leafFunctionCall]).write(selfString)
    
    

    def getFinalLeafClass(self) -> LeafClass:
        return self.leafFunctionCall.leafFunction.ret.leafClass
    

    def getFinalAllocation(self) -> ALLOCATION:
        return self.leafFunctionCall.leafFunction.ret.allocation
    

    def getFinalPassing(self) -> PASSING:
        return self.leafFunctionCall.leafFunction.ret.passing
    


class LeafFunctionCall:
    """
    A function call
    """

    def __init__(self, leafFunction: LeafFunction, generics: list[LeafChain], arguments: list[LeafValue]) -> None:
        
        self.leafFunction: LeafFunction = leafFunction
        self.generics: list[LeafChain] = generics
        self.arguments: list[LeafValue] = arguments

