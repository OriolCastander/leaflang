

import src.compiler.nodes as nodes


from src.utils import ALLOCATION, PASSING

class Writer:
    """
    The writer transforms the abstract syntax tree to the string that will become the c program
    """

    def __init__(self) -> None:
        ##MAYBE SOME CONFIG IN THE FUTURE?

        self.nIndentations: int = -1#start at -1 so that fist scope node gets us to 0
        self.entryNode: nodes.ScopeNode = None


    def write(self, entryNode: nodes.ScopeNode) -> str:
        """Outputs the c program"""

        self.entryNode = entryNode

        string = self._getStringDefaultStart()

        string += self._writeNode(entryNode)
        return string
    



    def _writeNode(self, node: nodes.TreeNode) -> str:

        if type(node) == nodes.ScaffoldingNode:
            raise Exception("Scaffolding node should not be written")

        if type(node) == nodes.LeafFunctionDeclarationNode:
            return self._writeFunctionDeclaration(node)
        
        elif type(node) == nodes.LeafClassDeclarationNode:
            return self._writeClassDeclaration(node)
        

        elif type(node) == nodes.ScopeNode:
            return self._writeScopeNode(node, writeEntryOpenCurly=node != self.entryNode)
        
        
        elif type(node) == nodes.NakedLeafFunctionCallNode:
            return self._writeNakedLeafFunctionCall(node)
        
        
        else:
            raise Exception(f"Canot write node of type {type(node)}")





    def _writeFunctionDeclaration(self, leafFunctionDeclarationNode: nodes.LeafFunctionDeclarationNode) -> str:
        """Writes the function declaration (+ all in scope)"""

        leafFunction = leafFunctionDeclarationNode.function

        #step 1: return value
        string = f"{leafFunction.ret.leafClass.cName}"
        if leafFunction.ret.passing == PASSING.REFERENCE:
            string += "*"

        string += f" {leafFunction.cName}("

        for i, parameter in enumerate(leafFunction.parameters):

            if i>0:
                string += ", "

            string += parameter.leafClass.cName
            if parameter.passing == PASSING.REFERENCE:
                string += "*"
            
            string += f" {parameter.name}"

        string += "){\n"
        string += self._writeScopeNode(leafFunctionDeclarationNode, writeEntryOpenCurly=False)

        return string
    



    def _writeClassDeclaration(self, leafClassDeclarationNode: nodes.LeafClassDeclarationNode) -> str:
        """Writes the class declaration. Important, all done top level, without indentation in the beggining (can have them in methods)"""

        leafClass = leafClassDeclarationNode.leafClass

        string = f"//Class {leafClass.name} struct and methods\n"
        string += leafClass.cName + "{\n"
        
        self.nIndentations += 1
        for property in leafClass.properties.values():
            propertyString = f"\t{property.leafClass.cName}"
            if property.passing == PASSING.REFERENCE:
                propertyString += "*"
            propertyString += f" {property.name};\n"
            string += propertyString

        string += "};\n"

        self.nIndentations -= 1

        ##TODO: write constructor + methods
        
        return string
    



    def _writeScopeNode(self, scopeNode: nodes.ScopeNode, writeEntryOpenCurly: bool) -> str:
        """Returns the string of the scope node. Writes the entry curly if requested to, indents in and out, and writes the closing curly"""
        
        string = ""
        if writeEntryOpenCurly:
            string += "\t" * self.nIndentations + "{\n"
        
        self.nIndentations += 1

        for child in scopeNode.children:
            string += self._writeNode(child)

        self.nIndentations -= 1

        if self.nIndentations >= 0:
            string += "\t" * self.nIndentations + "}\n"

        return string
    




    def _writeNakedLeafFunctionCall(self, nakedLeafFunctionCallNode: nodes.NakedLeafFunctionCallNode) -> str:
        """Writes the naked leaf function call"""

        return "\t" * self.nIndentations + nakedLeafFunctionCallNode.chain.write() + ";\n"



    def _getStringDefaultStart(self) -> str:
        
        string = """
//This is auto generated by the leaflang transpiler, all rights reserved or something?
//Oriol Castander

#include <stdio.h>
#include <stdlib.h>

#include "./../c_libraries/code/std.h"
#include "./../c_libraries/code/leaf.h"

"""
        return string