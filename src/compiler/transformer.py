
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

    def __init__(self, allowedSentences: list[type[sentences.Sentence]]) -> None:
        self.allowedSentences: list[type[sentences.Sentence]] = allowedSentences


    def transform(self, scaffoldingNode: ScaffoldingNode, replace: bool = False) ->  nodes.TreeNode | compilerErrors.CompilerError:
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
            else:
                newNode.parent = scaffoldingNode.parent
                #newNode.parent.children[newNode.parent.children.index(scaffoldingNode)] = newNode
            
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
        
        elif type(scaffoldingNode.element) not in self.allowedSentences:
            raise Exception(f"Sentence type {type(scaffoldingNode.element)} not allowed")
        
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


        elif type(scaffoldingNode.element) == sentences.NakedLeafFunctionCall:
            nakedLeafFunctionCall = self._constructNakedLeafFunctionCall(scaffoldingNode.element, scaffoldingNode)
    
            return nakedLeafFunctionCall
        

        elif type(scaffoldingNode.element) == sentences.LeafVariableDeclaration:
            leafVariableDeclaration = self._constructLeafVariableDeclaration(scaffoldingNode.element, scaffoldingNode)
            return leafVariableDeclaration

        elif type(scaffoldingNode.element) == sentences.Assignment:
            assignment = self._constructAssignment(scaffoldingNode.element, scaffoldingNode)
            return assignment

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
            parameter.cName = parameter.name
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



    def _constructLeafVariableDeclaration(self, leafVariableDeclarationSentence: sentences.LeafVariableDeclaration, scaffoldingNode: ScaffoldingNode) -> nodes.LeafVariableDeclarationNode | compilerErrors.CompilerError:
        """Constructs a leaf variable declaration"""

        parentNode: nodes.ScopeNode = scaffoldingNode.parent
        if not isinstance(parentNode, nodes.ScopeNode):
            raise Exception("Parent is not a scope node")
        
        leafClass = scaffoldingNode.getClass(leafVariableDeclarationSentence.declaration.leafClassDescriptor)
        
        if leafClass is None:
            return compilerErrors.LeafClassNotFoundError(leafVariableDeclarationSentence.line, scaffoldingNode, leafVariableDeclarationSentence.declaration.leafClassDescriptor)
        
        variableName = leafVariableDeclarationSentence.declaration.mention.value
        if variableName in KEYWORDS:
            return compilerErrors.InvalidNameError(leafVariableDeclarationSentence.line, scaffoldingNode, variableName)

        if scaffoldingNode.getStructureByName(variableName) is not None:
            return compilerErrors.InvalidNameError(leafVariableDeclarationSentence.line, scaffoldingNode, variableName)

        ##generics
        generics: list[structures.LeafClass] = []
        for genericWord in leafVariableDeclarationSentence.declaration.generics:
            generic = parentNode.getClass(genericWord, includeBase=True)
            if isinstance(generic, compilerErrors.CompilerError):
                return generic
            generics.append(generic)

        ##TODO: ALLOCATION AND PASSING

        leafMention = structures.LeafMention(variableName, leafClass, generics, allocation=leafVariableDeclarationSentence.allocation, passing=PASSING.REFERENCE)
        leafMention.cName = variableName
        return nodes.LeafVariableDeclarationNode(leafVariableDeclarationSentence.line, scaffoldingNode.parent, leafMention)






    def _constructNakedLeafFunctionCall(self, nakedLeafFunctionCall: sentences.NakedLeafFunctionCall, scaffoldingNode: ScaffoldingNode) -> nodes.NakedLeafFunctionCallNode | compilerErrors.CompilerError:
        """Constructs a naked leaf function call"""

        
        leafChain = constructLeafValue(nakedLeafFunctionCall.chain, scaffoldingNode)
        if isinstance(leafChain, compilerErrors.CompilerError):
            return leafChain
        
        return nodes.NakedLeafFunctionCallNode(nakedLeafFunctionCall.line, scaffoldingNode.parent, leafChain)





    def _constructAssignment(self, assignmentSentence: sentences.Assignment, scaffoldingNode: ScaffoldingNode) -> nodes.AssignmentNode | compilerErrors.CompilerError:
        """Constructs an assignment"""

        assigneeWord = assignmentSentence.assignee
        assignee = constructLeafValue(assigneeWord, scaffoldingNode)
        value = constructLeafValue(assignmentSentence.value, scaffoldingNode)

        if isinstance(assignee, compilerErrors.CompilerError):
            return assignee
        if type(assignee) != structures.LeafChain:
            return compilerErrors.InvalidStructureError(assignmentSentence.line, scaffoldingNode, assigneeWord, structures.LeafChain, type(assignee))
        
        if isinstance(value, compilerErrors.CompilerError):
            return value
        
        
        return nodes.AssignmentNode(assignmentSentence.line, scaffoldingNode.parent, assignee, value)
        








def constructLeafValue(word: words.Chain | words.Operator, originNode: nodes.TreeNode | nodes.ScaffoldingNode) -> structures.LeafValue | compilerErrors.CompilerError:
    """
    Constructs a leaf value from a word chain or operator
    TODO: separate if word is chain or operator?
    """

    parentNode = originNode.parent
    if not isinstance(parentNode, nodes.ScopeNode):
        raise Exception("Parent is not a scope node")


    if type(word) == words.Chain:

        newElements: list[structures.LeafMention | structures.LeafFunctionCall | int | float | str | bool] = []
        insideClass = None

        for wordElement in word.elements:

            if insideClass is None:

                if type(wordElement) == words.Mention:
                    mention = originNode.getStructureByName(wordElement.value)

                    ##fail if not found
                    if mention is None:
                        return compilerErrors.InvalidNameError(originNode.line, originNode, wordElement.value)
                    
                    ##fail if not variable
                    if type(mention) != structures.LeafMention:
                        return compilerErrors.InvalidStructureError(originNode.line, originNode, wordElement.value, structures.LeafMention, type(mention))
                    
                    newElements.append(mention)
                    insideClass = mention.leafClass


                elif type(wordElement) == words.LeafFunctionCallWord:

                    leafFunctionStructure = originNode.getStructureByName(wordElement.leafFunction.value)

                    ##fail if not found
                    if leafFunctionStructure is None:
                        return compilerErrors.InvalidNameError(originNode.line, originNode, wordElement.leafFunction.value)
                    
                    ##if a class, grab the constructor yo
                    if type(leafFunctionStructure) == structures.LeafClass:
                        if leafFunctionStructure.constructor is None: raise Exception("Class has no constructor")
                        leafFunctionStructure = leafFunctionStructure.constructor

                    ##not a function yo
                    if type(leafFunctionStructure) != structures.LeafFunction:
                        return compilerErrors.InvalidStructureError(originNode.line, originNode, wordElement.leafFunction.value, structures.LeafFunction, type(functionCallStructure))
                    
                    ###VALID STUFFS, PROCEED W/ EVERYTHING

                    ##get the generics
                    generics: list[structures.LeafClass] = []
                    for wordGeneric in wordElement.generics:
                        generic = parentNode.getClass(wordGeneric, includeBase=True)
                        if isinstance(generic, compilerErrors.CompilerError):
                            return generic
                        generics.append(generic)

                    ###get the parameters
                    arguments: list[structures.LeafValue] = []

                    for wordArgument in wordElement.arguments:
                        argument = constructLeafValue(wordArgument, originNode)
                        
                        if isinstance(argument, compilerErrors.CompilerError):
                            return argument
                        arguments.append(argument)

                    ##construct the function call
                    functionCallStructure = structures.LeafFunctionCall(leafFunctionStructure, generics, arguments)
                    newElements.append(functionCallStructure)
                    insideClass = functionCallStructure.leafFunction.ret.leafClass



                elif type(wordElement) in [int, float, str, bool]:
                    newElements.append(wordElement)

                else:
                    raise Exception(f"Unknown word element type: {type(wordElement)}")
                




            elif insideClass is not None:

                if type(wordElement) == words.Mention:
                    mention = insideClass.properties.get(wordElement.value)
                    
                    if mention is None:
                        return compilerErrors.InvalidNameError(originNode.line, originNode, wordElement.value)
                    newElements.append(mention)

                elif type(wordElement) == words.LeafFunctionCallWord:
                    raise NotImplementedError()
                
                else:##TODO: compiler error here 99% sure
                    raise Exception(f"Unknown word element type: {type(wordElement)}")


        
        return structures.LeafChain(newElements)






    elif type(word) == words.Operator:

        leftValue = constructLeafValue(word.left, originNode)

        if isinstance(leftValue, compilerErrors.CompilerError):
            return leftValue
        
        leftValueClass = leftValue.getFinalLeafClass()

        rightValue = constructLeafValue(word.right, originNode)
        if isinstance(rightValue, compilerErrors.CompilerError):
            return rightValue
        
        rightValueClass = rightValue.getFinalLeafClass()
        
        operatorFunction = leftValueClass.getOperator(word.operatorKind)

        if operatorFunction is None:
            return compilerErrors.InvalidOperatorError(originNode.line, originNode, leftValueClass, word.operatorKind)

        if leftValueClass != operatorFunction.ret.leafClass:
            return compilerErrors.LeafClassMismatchError(originNode.line, originNode, operatorFunction.ret.leafClass, rightValueClass)


        
        return structures.LeafOperator(word.operatorKind, operatorFunction, leftValue, rightValue)