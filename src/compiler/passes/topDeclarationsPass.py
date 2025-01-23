
import src.compiler.compilerErrors as compilerErrors

import src.compiler.nodes as nodes
import src.parser.sentences as sentences

from src.compiler.transformer import Transformer




class TopDeclarationsPass:
    """Gets the definitions of classes and functions that must be top level"""

    def __init__(self, transformer: Transformer | None = None) -> None:
        
        self.transformer = Transformer() if transformer is None else transformer


    def run(self, treeRoot: nodes.ScopeNode) -> compilerErrors.CompilerError | list[nodes.LeafClassDeclarationNode, nodes.LeafFunctionDeclarationNode]:
        """
        Runs the top declarations pass
        TODO: currently classes and functions can only be declared at the top level.
        Top declarations pass should check recursively once this is changed
        """

        passTargets = [sentences.LeafClassDeclaration, sentences.LeafFunctionDeclaration]

        for passTarget in passTargets:
            for child in treeRoot.children:
                
                if isinstance(child, nodes.TreeNode):
                    continue##TODO: check if this is correct or should fail

                if child.element is None:
                    continue

                if type(child.element) == passTarget:
                    declarationNode = self.transformer.transform(child, replace=False)
                    
                    if isinstance(declarationNode, compilerErrors.CompilerError):
                        return declarationNode
                    
                    treeRoot.children.append(declarationNode)
                    treeRoot.children.remove(child)

                
                
