

from src.compiler.transformer import Transformer

import src.compiler.structures as structures
import src.compiler.nodes as nodes
import src.parser.sentences as sentences

import src.compiler.compilerErrors as compilerErrors

from src.compiler.passes.mainPass import MainPass

from src.utils import ALLOCATION, PASSING




class ClassPass:
    """Resolves the variable declarations and functions in a class"""


    def __init__(self) -> None:
        
        self.transformer = Transformer(allowedSentences=[sentences.LeafVariableDeclaration])
        self.mainPasser = MainPass()
        self.currentNode: nodes.ScopeNode


    def run(self, root: nodes.ScopeNode) -> compilerErrors.CompilerError | None:
        """Runs the main pass"""
        
        for child in root.children:
            if type(child) == nodes.LeafClassDeclarationNode:
                self._parseClass(child)
    

    def _parseClass(self, node: nodes.LeafClassDeclarationNode) -> compilerErrors.CompilerError | None:
        """Parses a class"""

        leafClass = node.leafClass

        self.currentNode = node
        isInPropertiesDeclaration = True
        
        for child in node.children:
            if isInPropertiesDeclaration:
                ###WE PARSE THE PROPERTIES

                if type(child.element) == sentences.LeafVariableDeclaration:
                    variableDeclarationNode: nodes.LeafVariableDeclarationNode | compilerErrors.CompilerError = self.transformer.transform(child, replace=True)
                    if isinstance(variableDeclarationNode, compilerErrors.CompilerError):
                        return variableDeclarationNode
                    
                    leafVariable = variableDeclarationNode.variable

                    ##cheat, but gotta look into this: all variables are referenced pass rn, but not as a parameter
                    if leafVariable.passing == PASSING.REFERENCE and leafVariable.leafClass.passing == PASSING.VALUE:
                        leafVariable.passing = PASSING.VALUE
                    leafClass.properties[variableDeclarationNode.variable.name] = leafVariable

                elif type(child.element) == sentences.LeafFunctionDeclaration:
                    isInPropertiesDeclaration = False

                else:
                    return compilerErrors.InvalidSentenceError(child.line, child, child.element)


            if not isInPropertiesDeclaration:
                ###WE PARSE THE METHODS

                if type(child.element) == sentences.LeafFunctionDeclaration:
                    self.mainPasser.run(child) ##main passer constrcuts the method recursively

                else:
                    return compilerErrors.InvalidSentenceError(child.line, child, child.element)
                

        constructorNode = self._constructConstructor(leafClass, node)
        node.constructor = constructorNode
        leafClass.constructor = constructorNode.function





    def _constructConstructor(self, leafClass: structures.LeafClass, leafClassDeclarationNode: nodes.LeafClassDeclarationNode) -> nodes.LeafFunctionDeclarationNode:
        """Constructs the constructor"""

        ###constructor
        selfMention = structures.LeafMention("self", leafClass, [], allocation=None, passing=PASSING.REFERENCE)
        selfMention.cName = "self"

        constructorParams = [selfMention] + list(leafClass.properties.values())
        constructor = structures.LeafFunction(f"{leafClass.name}__constructor", leafClass.generics, constructorParams, structures.LeafMention(None, leafClass, [], allocation=ALLOCATION.HEAP, passing=PASSING.REFERENCE))
        constructor.cName = f"{leafClass.name}__constructor"
        constructor.constructorOf = leafClass
        constructorNode = nodes.LeafFunctionDeclarationNode(leafClassDeclarationNode.line, leafClassDeclarationNode, constructor)




        for property in leafClass.properties.values():
            assignee = structures.LeafChain([selfMention, property])
            value = structures.LeafChain([property])
            assignmentNode = nodes.AssignmentNode(leafClassDeclarationNode.line, constructorNode, assignee, value)
            constructorNode.children.append(assignmentNode)

        ###RETURN NODE
        returnStructure = structures.LeafChain([selfMention])
        returnNode = nodes.ReturnNode(leafClassDeclarationNode.line, constructorNode, returnStructure)
        constructorNode.children.append(returnNode)

        

        return constructorNode










