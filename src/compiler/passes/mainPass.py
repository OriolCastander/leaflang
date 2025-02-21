import src.compiler.compilerErrors as compilerErrors
import src.compiler.nodes as nodes
import src.compiler.structures as structures
import src.parser.sentences as sentences
import src.parser.words as words

from src.compiler.transformer import Transformer


MAIN_PASS_ALLOWED_SENTENCES = [sentences.NakedLeafFunctionCall, sentences.Assignment, sentences.LeafVariableDeclaration, sentences.ReturnSentence,
                               sentences.ScopeOpening, sentences.LeafIfStatement, sentences.LeafWhileStatement]

class MainPass:


    def __init__(self) -> None:
        
        self.transformer = Transformer(allowedSentences=MAIN_PASS_ALLOWED_SENTENCES)
        self.currentNode: nodes.ScopeNode


    def run(self, root: nodes.ScopeNode, alternateCurrentNode: nodes.TreeNode | None = None) -> compilerErrors.CompilerError | None:
        """Runs the main pass"""
        
        if alternateCurrentNode is None:
            self.currentNode = root
        else:
            self.currentNode = alternateCurrentNode

        return self._parseNode(root)
    


    def _parseNode(self, node: nodes.TreeNode | nodes.ScaffoldingNode) -> compilerErrors.CompilerError | None:
        """Parses a node"""


        if type(node) == nodes.ScaffoldingNode:
            treeNode = self.transformer.transform(node, replace=True)
            if isinstance(treeNode, compilerErrors.CompilerError):
                return treeNode
            
            ##maybe this can be done in the transformer?
            self.currentNode.children[self.currentNode.children.index(node)] = treeNode

            node = treeNode
        
            

        if isinstance(node, nodes.ScopeNode):

            self.currentNode = node

            for child in node.children:
                compilerError = self._parseNode(child)
                if compilerError is not None:
                    return compilerError
                
            self.currentNode = node.parent




