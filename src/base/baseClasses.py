


import src.compiler.structures as structures

from src.utils import ALLOCATION, PASSING

"""
Prebuilt classes and functions for the language
"""




class BaseClasses:

    def __init__(self) -> None:

        self.INT_CLASS: structures.LeafClass = self._initIntClass()
        self.VOID_CLASS: structures.LeafClass = self._initVoidClass()


    def getAll(self) -> list[structures.LeafClass]:
        """Returns all the classes"""

        return list(self.__dict__.values())
    
    
    def _initIntClass(self) -> structures.LeafClass:

        intClass = structures.LeafClass("int", [], ALLOCATION.STACK, PASSING.VALUE)
        intClass.cName = "int"
        intConstructor = structures.LeafFunction("int", [], None, structures.LeafMention(None, intClass, [])) ##TODO: PARAMETERS IS NONE, CAN WE GET AWAY WITH IT?
        intConstructor.customSignature = lambda x: f"{x}"
        intClass.constructor = intConstructor
        return intClass


    def _initVoidClass(self) -> structures.LeafClass:

        voidClass = structures.LeafClass("void", [], ALLOCATION.STACK, PASSING.VALUE)
        voidClass.cName = "void"
        return voidClass



