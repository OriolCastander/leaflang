from typing import Union

import src.compiler.nodes as nodes
import src.parser.sentences as sentences


from src.compiler.nodes import ScaffoldingNode






class ScaffoldingPass:

    def __init__(self) -> None:
        
        self.root: ScaffoldingNode
        self.currentNode: ScaffoldingNode


    def reset(self) -> None:
        """Resets the scafolding pass"""
        self.root = ScaffoldingNode(0, None, None)
        self.currentNode = self.root



    def run(self, sentences: list[sentences.Sentence]) -> ScaffoldingNode:
        """Runs the primitive abstract syntax tree of the program"""

        self.reset()

        for sentence in sentences:
            self._parseSentence(sentence)

        return self.root


    def _parseSentence(self, sentence: sentences.Sentence) -> None:
        """Parses a sentence into the scafolding tree"""
        
        if type(sentence) in [sentences.LeafClassDeclaration, sentences.LeafFunctionDeclaration, sentences.ScopeOpening, sentences.LeafIfStatement, sentences.LeafWhileStatement]:
            self._parseNewScopeDeclaration(sentence)


        elif type(sentence) in [sentences.LeafVariableDeclaration, sentences.NakedLeafFunctionCall, sentences.Assignment, sentences.ReturnSentence]:
            self._parseStandard(sentence)

        
        elif type(sentence) == sentences.ScopeClosure:
            self._parseEndScopeDeclaration(sentence)

        else:
            raise Exception(f"Unknown sentence type: {type(sentence)}")



    def _parseNewScopeDeclaration(self, sentence: sentences.Sentence) -> None:
        """Parses a declaration that requires a change of scope"""
        
        scaffoldingNode: ScaffoldingNode = ScaffoldingNode(sentence.line, self.currentNode, sentence)
        self.currentNode.children.append(scaffoldingNode)
        self.currentNode = scaffoldingNode


    def _parseStandard(self, sentence: sentences.Sentence) -> None:
        """Parses a standard sentence"""
        
        scaffoldingNode: ScaffoldingNode = ScaffoldingNode(sentence.line, self.currentNode, sentence)
        self.currentNode.children.append(scaffoldingNode)





    def _parseEndScopeDeclaration(self, sentence: sentences.Sentence) -> None:
        """Parses a declaration that ends a scope"""
        
        self.currentNode = self.currentNode.parent

