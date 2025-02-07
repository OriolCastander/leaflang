


import src.compiler.structures as structures

from src.utils import ALLOCATION, PASSING, OperatorKind

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

        sumOperator = structures.LeafFunction("int__operator__SUM", [], None, structures.LeafMention(None, intClass, []))
        def sumOperatorcustomSignature(argument1: structures.LeafValue, argument2: structures.LeafValue) -> str:

            string = ""

            for argument in [argument1, argument2]:

                if argument.getFinalPassing() == PASSING.VALUE:
                    string += argument.write()
                elif argument.getFinalPassing() == PASSING.REFERENCE:
                    string += "*" + argument.write()

                if argument == argument1:
                    string += " + "

            return string
        
        sumOperator.customSignature = sumOperatorcustomSignature
        sumOperator.cName = sumOperator.name
        intClass.operators[OperatorKind.SUM] = sumOperator
        return intClass


    def _initVoidClass(self) -> structures.LeafClass:

        voidClass = structures.LeafClass("void", [], ALLOCATION.STACK, PASSING.VALUE)
        voidClass.cName = "void"
        return voidClass



