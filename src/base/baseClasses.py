
from typing import Callable

import src.compiler.structures as structures

from src.utils import ALLOCATION, PASSING, OperatorKind

"""
Prebuilt classes and functions for the language
"""



def _simpleOperatorCustomSignatureConstructor(operatorString: str) -> Callable[[structures.LeafValue, structures.LeafValue], str]:
    """Returns the custom signature for a simple operator (a + b)"""

    def simpleOperatorCustomSignature(argument1: structures.LeafValue, argument2: structures.LeafValue) -> str:
        string = ""

        for argument in [argument1, argument2]:

            if argument.getFinalPassing() == PASSING.VALUE:
                string += argument.write()
            elif argument.getFinalPassing() == PASSING.REFERENCE:
                string += "*" + argument.write()

            if argument == argument1:
                string += f" {operatorString} "

        return string
    return simpleOperatorCustomSignature



class BaseClasses:

    def __init__(self) -> None:

        self.INT_CLASS: structures.LeafClass = structures.LeafClass("int", [], ALLOCATION.STACK, PASSING.VALUE)
        self.VOID_CLASS: structures.LeafClass = structures.LeafClass("void", [], ALLOCATION.STACK, PASSING.VALUE)
        self.BOOL_CLASS: structures.LeafClass = structures.LeafClass("bool", [], ALLOCATION.STACK, PASSING.VALUE)

        self._initIntClass()
        self._initVoidClass()
        self._initBoolClass()


    def getAll(self) -> list[structures.LeafClass]:
        """Returns all the classes"""

        return list(self.__dict__.values())
    
    
    def _initIntClass(self) -> None:

        
        self.INT_CLASS.cName = "int"
        intConstructor = structures.LeafFunction("int", [], None, structures.LeafMention(None, self.INT_CLASS, [])) ##TODO: PARAMETERS IS NONE, CAN WE GET AWAY WITH IT?
        intConstructor.customSignature = lambda x: f"{x}"
        self.INT_CLASS.constructor = intConstructor

        sumOperator = structures.LeafFunction("int__operator__SUM", [], None, structures.LeafMention(None, self.INT_CLASS, []))            
        sumOperator.customSignature = _simpleOperatorCustomSignatureConstructor("+")
        sumOperator.cName = sumOperator.name
        self.INT_CLASS.operators[OperatorKind.SUM] = sumOperator


        lessThanOperator = structures.LeafFunction("int__operator__LESS_THAN", [], None, structures.LeafMention(None, self.BOOL_CLASS, []))
        lessThanOperator.customSignature = _simpleOperatorCustomSignatureConstructor("<")
        lessThanOperator.cName = lessThanOperator.name
        self.INT_CLASS.operators[OperatorKind.LESS_THAN] = lessThanOperator


        greaterThanOperator = structures.LeafFunction("int__operator__GREATER_THAN", [], None, structures.LeafMention(None, self.BOOL_CLASS, []))
        greaterThanOperator.customSignature = _simpleOperatorCustomSignatureConstructor(">")
        greaterThanOperator.cName = greaterThanOperator.name
        self.INT_CLASS.operators[OperatorKind.GREATER_THAN] = greaterThanOperator





    def _initVoidClass(self) -> None:
        
        self.VOID_CLASS.cName = "void"


    def _initBoolClass(self) -> None:

        self.BOOL_CLASS.cName = "bool"




