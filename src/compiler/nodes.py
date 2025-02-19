"""
Nodes are the parts of the abstract syntax tree
"""
from typing import Union
import abc

import src.compiler.structures as structures
import src.parser.sentences as sentences


import src.parser.words as words


from src.base import BASE_CLASSES, BASE_FUNCTIONS

##TODO: maybe join scaffolding node and scope node into something like, they got the same funcs...


class ScaffoldingNode:

    def __init__(self, line: int, parent: Union["ScaffoldingNode", None], element: sentences.Sentence | None) -> None:
        self.line: int = line
        self.parent: ScaffoldingNode | ScopeNode | None = parent
        self.element: sentences.Sentence | None = element

        self.children: list[ScaffoldingNode | ScopeNode] = []

        self.location: list[int] = [] if parent is None else parent.location + [len(parent.children)]

    
    def getAll(self, *leafStructures: type, recursive: bool = False, includeBase: bool = False) -> list[structures.LeafMention | structures.LeafFunction | structures.LeafClass]:
        """Returns all the leaf structures of the given type"""
        return _getAll(self, *leafStructures, recursive=recursive, includeBase=includeBase)


    def getClass(self, chain: words.Chain, includeBase: bool = True) -> structures.LeafClass | None:
        """Returns the class of the given name"""
        return _getClass(self, chain, includeBase)

    def getStructureByName(self, name: str) -> structures.LeafMention | structures.LeafClass | structures.LeafFunction | None:
        """Gets the element in scope with the given name (or None if not found)"""

        ##TODO: do it more efficient for the love of god
        ##I'm lazy and I did it like this.
        ##Wow, get All yields each level? (nah Im like high rn)

        allStructures = self.getAll(structures.LeafMention, structures.LeafClass, structures.LeafFunction, recursive=True, includeBase=True)
        for structure in allStructures:
            if structure.name == name:
                return structure
        return None


class TreeNode(abc.ABC):
    """Abstract base class for all nodes"""

    def __init__(self, line: int, parent: Union["ScopeNode", None]) -> None:
        
        self.line: int = line
        self.parent: ScaffoldingNode | ScopeNode | None = parent
        

    def getStructure(self) -> structures.LeafMention | structures.LeafFunction | structures.LeafClass | None:
        """Returns the structure of the node (overriden in certain nodes)"""
        return None


    def getAll(self, *leafStructures: type, recursive: bool = False, includeBase: bool = False) -> list[structures.LeafMention | structures.LeafFunction | structures.LeafClass]:
        """Returns all the leaf structures of the given type"""
        return _getAll(self, *leafStructures, recursive=recursive, includeBase=includeBase)


    def getClass(self, chain: words.Chain, includeBase: bool = True) -> structures.LeafClass | None:
        """Returns the class of the given name"""
        return _getClass(self, chain, includeBase)




    def getStructureByName(self, name: str) -> structures.LeafMention | structures.LeafClass | structures.LeafFunction | None:
        """Gets the element in scope with the given name (or None if not found)"""

        ##TODO: do it more efficient for the love of god
        ##I'm lazy and I did it like this.
        ##Wow, get All yields each level? (nah Im like high rn)

        allStructures = self.getAll(structures.LeafMention, structures.LeafClass, structures.LeafFunction, recursive=True, includeBase=True)
        for structure in allStructures:
            if structure.name == name:
                return structure
        return None




class ScopeNode(TreeNode):
    """
    Node that opens a new scope, such as the body of a function declaration, if statement...
    Has children
    """

    def __init__(self, line: int, parent: Union["ScopeNode", None]) -> None:
        super().__init__(line, parent)

        self.children: list[TreeNode | ScaffoldingNode] = []






class LeafVariableDeclarationNode(TreeNode):
    """
    Node that declares a variable
    """

    def __init__(self, line: int, parent: ScopeNode, variable: structures.LeafMention) -> None:
        super().__init__(line, parent)

        self.variable: structures.LeafMention = variable


    def getStructure(self) -> structures.LeafMention:
        return self.variable





class LeafClassDeclarationNode(ScopeNode):


    def __init__(self, line: int, parent: ScopeNode, leafClass: structures.LeafClass) -> None:
        super().__init__(line, parent)

        self.leafClass: structures.LeafClass = leafClass
        self.constructor: LeafFunctionDeclarationNode | None = None

    def getStructure(self) -> structures.LeafClass:
        return self.leafClass
    


class LeafFunctionDeclarationNode(ScopeNode):

    def __init__(self, line: int, parent: ScopeNode, function: structures.LeafFunction) -> None:
        super().__init__(line, parent)

        self.function: structures.LeafFunction = function


    def getStructure(self) -> structures.LeafFunction:
        return self.function
    





class NakedLeafFunctionCallNode(TreeNode):

    def __init__(self, line: int, parent: ScopeNode, chain: structures.LeafChain) -> None:
        super().__init__(line, parent)

        self.chain: structures.LeafChain = chain


    def getStructure(self) -> structures.LeafChain:
        return self.chain



class AssignmentNode(TreeNode):

    def __init__(self, line: int, parent: ScopeNode, assignee: structures.LeafChain, value: structures.LeafValue) -> None:
        super().__init__(line, parent)

        self.assignee: structures.LeafChain = assignee
        self.value: structures.LeafValue = value



class ReturnNode(TreeNode):

    def __init__(self, line: int, parent: ScopeNode, value: structures.LeafValue) -> None:
        super().__init__(line, parent)

        self.value: structures.LeafValue = value




class LeafIfStatementNode(ScopeNode):

    def __init__(self, line: int, parent: ScopeNode, condition: structures.LeafOperator) -> None:
        super().__init__(line, parent)

        self.condition: structures.LeafOperator = condition



class LeafWhileStatementNode(ScopeNode):

    def __init__(self, line: int, parent: ScopeNode, condition: structures.LeafOperator) -> None:
        super().__init__(line, parent)

        self.condition: structures.LeafOperator = condition



#functions that apply to both scope nodes and scaffolding nodes

def _getAll(node: TreeNode | ScaffoldingNode, *leafStructures: type, recursive: bool = False, includeBase: bool = False) -> list[structures.LeafMention | structures.LeafFunction | structures.LeafClass]:
    """Returns all the leaf structures of the given type"""

    validStructures: list[structures.LeafMention | structures.LeafFunction | structures.LeafClass] = []

    if includeBase:
        validStructures.extend(BASE_CLASSES.getAll())
        validStructures.extend(BASE_FUNCTIONS.getAll())


    if type(node) == LeafFunctionDeclarationNode:
        ##include ourselves
        validStructures.append(node.function)
        
        ##include the params
        for parameter in node.function.parameters:
            validStructures.append(parameter)
    
    if node.parent is not None:
        for child in node.parent.children[:node.parent.children.index(node)]:
            if type(child) == ScaffoldingNode:
                continue

            potentialStructure = child.getStructure()
            if potentialStructure is not None and type(potentialStructure) in leafStructures:
                validStructures.append(potentialStructure)

        if recursive:
            validStructures.extend(_getAll(node.parent, *leafStructures, recursive=True, includeBase=False))

    
    return validStructures




def _getClass(node: TreeNode | ScaffoldingNode, chain: words.Chain, includeBase: bool = True) -> structures.LeafClass | None:
    """Returns the class of the given name"""

    if len(chain.elements) > 1 or type(chain.elements[0]) != words.Mention:
        ##TODO: allow that
        raise NotImplementedError()

    ###GO TO TOP LEVEL YO
    if node.parent is not None:
        return _getClass(node.parent, chain, includeBase)
    
    
    if includeBase:
        for baseClass in BASE_CLASSES.getAll():
            if baseClass.name == chain.elements[0].value:
                return baseClass
    
    
    for child in node.children:

        if type(child) == LeafClassDeclarationNode:
            if child.leafClass.name == chain.elements[0].value:
                return child.leafClass
            
    return None
