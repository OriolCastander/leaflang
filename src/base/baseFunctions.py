

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
        printInt.customSignature = lambda x: f"printf(\"Your int is: %d\\n\", *{x.write()})"#TODO: improve
        return printInt
    