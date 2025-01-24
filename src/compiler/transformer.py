
from src.compiler.passes.scaffoldingPass import ScaffoldingNode
import src.compiler.compilerErrors as compilerErrors
import src.compiler.nodes as nodes
import src.compiler.structures as structures

import src.parser.sentences as sentences
import src.parser.words as words

import src.compiler.checks.orthographyChecks as orthographyChecks

from src.utils import ALLOCATION, PASSING

from src.base import KEYWORDS


class Transformer:
    """Transforms a scaffolding node into a proper node"""

    def __init__(self) -> None:
        pass


    def transform(self, scaffoldingNode: ScaffoldingNode, replace: bool = False) -> None | nodes.TreeNode | compilerErrors.CompilerError:
        """
        Transforms a scaffolding node into a proper node.
        If replace is true, changes the parent (aka, slots the new node in the place of the old one). Children always changed (does this make sense now?)
        """

        newNode = self._constructNode(scaffoldingNode)
        if isinstance(newNode, compilerErrors.CompilerError):
            return newNode

        if replace:
            if scaffoldingNode.parent is None: newNode.parent = None
            elif isinstance(scaffoldingNode.parent, ScaffoldingNode):
                raise Exception("scaffolding node cannot have a scaffolding node as parent")##error here: make leaf class scope node
            else: newNode.parent = scaffoldingNode.parent
            
        if isinstance(newNode, nodes.ScopeNode):
            newNode.children = scaffoldingNode.children
            for child in newNode.children:
                child.parent = newNode

        return newNode





    def _constructNode(self, scaffoldingNode: ScaffoldingNode) -> nodes.TreeNode | compilerErrors.CompilerError:
        """Constructs a new node"""


        if scaffoldingNode.element is None:
            scopeNode = nodes.ScopeNode(scaffoldingNode.line, scaffoldingNode.parent)
            return scopeNode
        
        elif type(scaffoldingNode.element) == sentences.LeafClassDeclaration:
            leafClass = self._constructLeafClass(scaffoldingNode.element, scaffoldingNode)
            if isinstance(leafClass, compilerErrors.CompilerError):
                return leafClass
            return nodes.LeafClassDeclarationNode(scaffoldingNode.line, scaffoldingNode.parent, leafClass)
        
        elif type(scaffoldingNode.element) == sentences.LeafFunctionDeclaration:
            leafFunction = self._constructLeafFunction(scaffoldingNode.element, scaffoldingNode)
            if isinstance(leafFunction, compilerErrors.CompilerError):
                return leafFunction
            return nodes.LeafFunctionDeclarationNode(scaffoldingNode.line, scaffoldingNode.parent, leafFunction)

        else:
            raise Exception(f"Unknown sentence type: {type(scaffoldingNode.element)}")
        


    def _constructLeafClass(self, leafClassSentence: sentences.LeafClassDeclaration, scaffoldingNode: ScaffoldingNode) -> structures.LeafClass | compilerErrors.CompilerError:
        """Constructs a leaf class"""

        ##FOR THE MOMENT, ALLOCATION IS HEAP AND PASSING IS BY REFERENCE BY DEFAULT
        allocation = ALLOCATION.HEAP
        passing = PASSING.REFERENCE

        takenClassNames = [structure.name for structure in scaffoldingNode.getAll(structures.LeafClass, recursive=True, includeBase=True)]
        takenClassNames.extend(KEYWORDS)
        
        ##leaf name
        if leafClassSentence.name.value in takenClassNames:
            return compilerErrors.InvalidNameError(leafClassSentence.line, scaffoldingNode, words.Chain([leafClassSentence.name.value]))


        ##generics: make sure it is a single mention, and that the mention is a valid word
        generics: list[str] = []
        for generic in leafClassSentence.generics:
            compilerError = orthographyChecks.checkGeneric(leafClassSentence.line, scaffoldingNode, generic)
            if compilerError is not None:
                return compilerError
            generics.append(generic.elements[0].value)
        

        leafClass = structures.LeafClass(leafClassSentence.name.value, leafClassSentence.generics, allocation, passing)
        leafClass.cName = f"struct {leafClass.name}"##to work on, probably fine for now as they are all top level declarations

        return leafClass



    def _constructLeafFunction(self, leafFunctionSentence: sentences.LeafFunctionDeclaration, scaffoldingNode: ScaffoldingNode) -> structures.LeafFunction | compilerErrors.CompilerError:
        """Constructs a leaf function"""

        takenNames: list[str] = [structure.name for structure in scaffoldingNode.getAll(structures.LeafClass, structures.LeafFunction, recursive=True, includeBase=True)]
        takenNames.extend(KEYWORDS)

        ##leaf name
        if leafFunctionSentence.name.value in takenNames:
            return compilerErrors.InvalidNameError(leafFunctionSentence.line, scaffoldingNode, words.Chain([leafFunctionSentence.name.value]))

        takenNames.append(leafFunctionSentence.name.value)

        ##generics: make sure it is a single mention, and that the mention is a valid word
        generics: list[str] = []
        for generic in leafFunctionSentence.generics:
            compilerError = orthographyChecks.checkGeneric(leafFunctionSentence.line, scaffoldingNode, generic)
            if compilerError is not None:
                return compilerError
            generics.append(generic.elements[0].value)

        ##parameters
        parameters: list[structures.LeafMention] = []
        for parameterWord in leafFunctionSentence.parameters:

            ##parameter name
            if parameterWord.mention.value in takenNames:
                return compilerErrors.InvalidParameterNameError(leafFunctionSentence.line, scaffoldingNode, parameterWord.mention.value)
            takenNames.append(parameterWord.mention.value)


            ##parameter type
            parameterLeafClass = scaffoldingNode.getClass(parameterWord.leafClassDescriptor)
            if parameterLeafClass is None:
                return compilerErrors.LeafClassNotFoundError(leafFunctionSentence.line, scaffoldingNode, parameterWord.leafClassDescriptor)
            
            if len(parameterWord.generics) > 0:
                ##TODO: should not be difficult, just getClass on the generic and voila
                raise NotImplementedError()
            
            parameter = structures.LeafMention(parameterWord.mention.value, parameterLeafClass, [])
            parameters.append(parameter)


        ##return type
        returnLeafClass = scaffoldingNode.getClass(leafFunctionSentence.returnLeafClass)
        if returnLeafClass is None:
            return compilerErrors.LeafClassNotFoundError(leafFunctionSentence.line, scaffoldingNode, leafFunctionSentence.returnLeafClass)
        
        ##TODO: generics in return type
        ret = structures.LeafMention(None, returnLeafClass, [])

        leafFunction = structures.LeafFunction(leafFunctionSentence.name.value, leafFunctionSentence.generics, parameters, ret)
        leafFunction.cName = f"{leafFunction.name}"##to work on when they are not top level
        return leafFunction
