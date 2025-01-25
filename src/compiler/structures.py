"""
Structures that live inside nodes
"""
from typing import Callable, Any, Union
import abc


from src.utils import ALLOCATION, PASSING





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
        self.customSignature: Callable | None = None

        self.cName: str | None = None






class LeafValue(abc.ABC):
    """Either a leaf chain or a leaf operator"""

    @abc.abstractmethod
    def write(self) -> str:
        pass


    @abc.abstractmethod
    def getFinalLeafClass(self) -> LeafClass:
        pass





class LeafChain(LeafValue):
    """
    A chain of variables and function calls
    TODO: might also be native stuff, like ints and stuff
    """

    def __init__(self, elements: list[Union[LeafMention, "LeafFunctionCall", int, float, str, bool]]) -> None:
        
        self.elements: list[LeafMention | LeafFunctionCall | int | float | str, bool] = elements

    
    def write(self) -> str:
        """Returns the C code for the chain"""
        ##ugly as hell but I dont give a fuck
        import src.writer.valueWriter as valueWriter
        return valueWriter.writeLeafChain(self)
        


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
        



class LeafFunctionCall(LeafValue):
    """
    A function call
    """

    def __init__(self, leafFunction: LeafFunction, generics: list[LeafChain], arguments: list[LeafValue]) -> None:
        
        self.leafFunction: LeafFunction = leafFunction
        self.generics: list[LeafChain] = generics
        self.arguments: list[LeafValue] = arguments


    def write(self) -> str:
        """Returns the C code for the function call"""

        raise NotImplementedError("LeafFunctionCall.write() not implemented")
    

    def getFinalLeafClass(self) -> LeafClass:
        """Returns the leaf class of the function call"""
        return self.leafFunction.ret.leafClass
