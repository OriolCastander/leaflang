import src.compiler.compilerErrors as compilerErrors
import src.compiler.nodes as nodes
import src.compiler.structures as structures
import src.parser.sentences as sentences
import src.parser.words as words

from src.compiler.transformer import Transformer


class MainPass:


    def __init__(self) -> None:
        
        self.transformer = Transformer(allowedSentences=[sentences.NakedLeafFunctionCall, sentences.Assignment, sentences.LeafVariableDeclaration])
        self.currentNode: nodes.ScopeNode


    def run(self, root: nodes.ScopeNode) -> compilerErrors.CompilerError | None:
        """Runs the main pass"""
        
        self.currentNode = root
        return self._parseNode(root)
    


    def _parseNode(self, node: nodes.TreeNode | nodes.ScaffoldingNode) -> compilerErrors.CompilerError | None:
        """Parses a node"""


        if type(node) == nodes.ScaffoldingNode:
            treeNode = self.transformer.transform(node, replace=True)
            if isinstance(treeNode, compilerErrors.CompilerError):
                return treeNode
            
            ##maybe this can be done in the transformer?
            self.currentNode.children[self.currentNode.children.index(node)] = treeNode


            

        if isinstance(node, nodes.ScopeNode):

            self.currentNode = node

            for child in node.children:
                compilerError = self._parseNode(child)
                if compilerError is not None:
                    return compilerError
                




