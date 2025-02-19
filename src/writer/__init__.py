

import src.compiler.nodes as nodes


from src.utils import ALLOCATION, PASSING

class Writer:
    """
    The writer transforms the abstract syntax tree to the string that will become the c program
    """

    def __init__(self, cDebugLevel: int = 0) -> None:
        ##MAYBE SOME CONFIG IN THE FUTURE?

        self.nIndentations: int = -1#start at -1 so that fist scope node gets us to 0
        self.entryNode: nodes.ScopeNode = None
        self.cDebugLevel: int = cDebugLevel

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
            return self._writeScopeNode(node, writeEntryOpenCurly=node != self.entryNode, writeScopeCalls=node != self.entryNode)
        
        
        elif type(node) == nodes.NakedLeafFunctionCallNode:
            return self._writeNakedLeafFunctionCall(node)
        


        elif type(node) == nodes.LeafVariableDeclarationNode:
            return self._writeLeafVariableDeclaration(node)


        elif type(node) == nodes.AssignmentNode:
            return self._writeAssignment(node)
        
        elif type(node) == nodes.ReturnNode:
            return self._writeReturnNode(node)
        
        elif type(node) == nodes.LeafIfStatementNode:
            return self._writeLeafIfStatement(node)
        
        elif type(node) == nodes.LeafWhileStatementNode:
            return self._writeLeafWhileStatement(node)
        
        
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

        if not leafFunction.isMain:
            string += "struct __STD_List* __LEAF_SCOPES, struct __STD_List* __LEAF_HEAP_ALLOCATIONS\n"
            if len(leafFunction.parameters) > 0:
                string += ", "

        
        for i, parameter in enumerate(leafFunction.parameters):

            if i>0:
                string += ", "

            string += parameter.leafClass.cName
            if parameter.passing == PASSING.REFERENCE:
                string += "*"
            
            string += f" {parameter.name}"

        string += "\t" * self.nIndentations + "){\n"

        if leafFunction.isMain:
            string += self._writeMainFunctionAddons()
        

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
        string += self._writeFunctionDeclaration(leafClassDeclarationNode.constructor)

        for method in leafClass.methods.values():
            for childNode in leafClassDeclarationNode.children:
                if type(childNode) == nodes.LeafFunctionDeclarationNode and childNode.function.cName == method.cName:
                    string += self._writeFunctionDeclaration(childNode)

        
        return string
    



    def _writeScopeNode(self, scopeNode: nodes.ScopeNode, writeEntryOpenCurly: bool, writeScopeCalls: bool = True) -> str:
        """Returns the string of the scope node. Writes the entry curly if requested to, indents in and out, and writes the closing curly"""
        
        string = ""
        if writeEntryOpenCurly:
            string += "\t" * self.nIndentations + "{\n"
        
        self.nIndentations += 1

        if writeScopeCalls:
            string += "\t" * self.nIndentations + f"__LEAF_openScope(__LEAF_SCOPES, {self.cDebugLevel});\n"

        for child in scopeNode.children:
            string += self._writeNode(child)


        if writeScopeCalls:
            string += "\t" * self.nIndentations + f"__LEAF_closeScope(__LEAF_SCOPES, __LEAF_HEAP_ALLOCATIONS, {self.cDebugLevel});\n"
        
        self.nIndentations -= 1

        if self.nIndentations >= 0:
            string += "\t" * self.nIndentations + "}\n"

        return string
    



    def _writeLeafVariableDeclaration(self, leafVariableDeclarationNode: nodes.LeafVariableDeclarationNode) -> str:
        """Writes the leaf variable declaration"""

        leafClass = leafVariableDeclarationNode.variable.leafClass
        
        if leafVariableDeclarationNode.variable.allocation == ALLOCATION.STACK:
            cStackDeclarationString = leafClass.cName + " " + leafVariableDeclarationNode.variable.name + "__STACK;"
            cDeclarationString = f"{leafClass.cName}* {leafVariableDeclarationNode.variable.cName} = &{leafVariableDeclarationNode.variable.cName}__STACK;"
            return "\t" * self.nIndentations + cStackDeclarationString + "\n" + "\t" * self.nIndentations + cDeclarationString + "\n"
        
        elif leafVariableDeclarationNode.variable.allocation == ALLOCATION.HEAP:
            declarationString = leafClass.cName + "* " + leafVariableDeclarationNode.variable.name + " = malloc(sizeof(" + leafClass.cName + "));"
            
            initSource: int = 0
            initObject: str = leafVariableDeclarationNode.variable.name
            initSize: int = f"sizeof({leafClass.cName})"
            initDestructor = f"__LEAF_voidDestructor" ##TEMP

            initVariableString = f"__LEAF_initHeapVariable(__LEAF_SCOPES, __LEAF_HEAP_ALLOCATIONS, {initSource}, {initObject}, {initSize}, &{initDestructor});"
            return "\t" * self.nIndentations + declarationString + "\n" + "\t" * self.nIndentations + initVariableString + "\n"
        else:
            raise Exception("Invalid allocation type")



    def _writeAssignment(self, assignmentNode: nodes.AssignmentNode) -> str:
        """Writes the assignment"""

        string = "\t" * self.nIndentations
        if assignmentNode.assignee.getFinalPassing() == PASSING.REFERENCE:
            string += "*"

        assigneeString = assignmentNode.assignee.write()
        assignedString = assignmentNode.value.write(assigneeString)
        assignedFinalPassing = assignmentNode.value.getFinalPassing()
        if assignedFinalPassing == PASSING.REFERENCE:
            assignedString = f"*({assignedString})"

        string += assigneeString + " = " + assignedString + ";\n"
        ##need to do something with the assignment value and reference passing? probably bro

        return string
    




    def _writeNakedLeafFunctionCall(self, nakedLeafFunctionCallNode: nodes.NakedLeafFunctionCallNode) -> str:
        """Writes the naked leaf function call"""

        return "\t" * self.nIndentations + nakedLeafFunctionCallNode.chain.write() + ";\n"


    def _writeReturnNode(self, returnNode: nodes.ReturnNode) -> str:
        """Writes the return node"""

        string = "\t" * self.nIndentations + "/** Return clause */   "

        
        string += f"for (int i=0; i<{returnNode.getNLevelsToFunction()}; i++) __LEAF_closeScope(__LEAF_SCOPES, __LEAF_HEAP_ALLOCATIONS, {self.cDebugLevel});\n"
        string += "\t" * self.nIndentations + "return " + returnNode.value.write() + ";//Finish return clause\n"
        return string
    



    def _writeLeafIfStatement(self, leafIfStatementNode: nodes.LeafIfStatementNode) -> str:
        """Writes the leaf if statement"""

        string = "\t" * self.nIndentations + "if (" + leafIfStatementNode.condition.write() + ") {\n"        
        string += self._writeScopeNode(leafIfStatementNode, writeEntryOpenCurly=False)

        return string
    

    def _writeLeafWhileStatement(self, leafWhileStatementNode: nodes.LeafWhileStatementNode) -> str:
        """Writes the leaf while statement"""

        string = "\t" * self.nIndentations + "while (" + leafWhileStatementNode.condition.write() + ") {\n"
        string += self._writeScopeNode(leafWhileStatementNode, writeEntryOpenCurly=False)

        return string



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
    


    def _writeMainFunctionAddons(self) -> str:
        """Stuff that should be appended at the beggining of the main function"""
        
        string = "\t//Stuff to carry through the program\n\n"
        string += "\tstruct __STD_List* __LEAF_SCOPES = malloc(sizeof(struct __STD_List));\n"
        string += "\tstruct __STD_List* __LEAF_HEAP_ALLOCATIONS = malloc(sizeof(struct __STD_List));\n\n"

        string += "\t__STD_List_constructor(__LEAF_SCOPES, (void(*)(void*))&__LEAF_Scope_destructor);\n"
        string += "\t__STD_List_constructor(__LEAF_HEAP_ALLOCATIONS, (void(*)(void*))&__LEAF_HeapAllocation_destructor);\n\n"

        

        return string