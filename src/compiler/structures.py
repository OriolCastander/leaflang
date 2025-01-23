"""
Structures that live inside nodes
"""
from typing import Callable, Any
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