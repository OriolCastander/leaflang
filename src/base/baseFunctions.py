

import src.compiler.structures as structures
from src.utils import ALLOCATION, PASSING

from src.base.baseClasses import BaseClasses

class BaseFunctions:

    def __init__(self, BASE_CLASSES: BaseClasses) -> None:

        self.PRINT_INT: structures.LeafFunction = self._initPrintInt(BASE_CLASSES)


    def getAll(self) -> list[structures.LeafFunction]:
        """Get all the base functions"""
        return list(self.__dict__.values())


    def _initPrintInt(self, BASE_CLASSES: BaseClasses) -> structures.LeafFunction:

        ###PRINT INT FUNCTION
        printInt = structures.LeafFunction("printInt", [], [structures.LeafMention(None, BASE_CLASSES.INT_CLASS, [])], structures.LeafMention(None, BASE_CLASSES.VOID_CLASS, []))
        printInt.cName = "printInt"

        def customSignature(argument: structures.LeafValue) -> str:

            string = f"printf(\"Your int is: %d\\n\", "

            argumentString = argument.write()
            ##TODO: PUT THIS SOMEWHERE ELSE BECAUSE WE'LL NEED TO REUSE IT
            if type(argument) == structures.LeafChain and len(argument.elements) == 1 and type(argument.elements[0]) in [int]:
                    string += f"{argumentString}"

            elif argument.getFinalPassing() == PASSING.VALUE:
                string += argumentString
            elif argument.getFinalPassing() == PASSING.REFERENCE:
                string += "*" + argumentString

            string += ")"
            return string


        printInt.customSignature = customSignature
        return printInt
    