
import src.compiler.nodes as nodes
import src.parser.sentences as sentences

from src.compiler.passes.scaffoldingPass import ScaffoldingPass, ScaffoldingNode
from src.compiler.passes.topDeclarationsPass import TopDeclarationsPass
from src.compiler.transformer import Transformer
import src.compiler.compilerErrors as compilerErrors

class Compiler:
    
    def __init__(self) -> None:

        pass


    def reset(self) -> None:
        """Resets the compiler"""
        pass
        

    def compile(self, sentences: list[sentences.Sentence]) -> nodes.ScopeNode:
        """Compiles a list of sentences into a tree of nodes. Returns the root"""

        scaffoldingPass: ScaffoldingPass = ScaffoldingPass()
        scaffoldingRoot: ScaffoldingNode = scaffoldingPass.run(sentences)

        transformer = Transformer()
        root = transformer.transform(scaffoldingRoot)

        print("root children before", root.children)

        topDeclarationsPass = TopDeclarationsPass(transformer)
        compilerError = topDeclarationsPass.run(root)
        if isinstance(compilerError, compilerErrors.CompilerError):
            print(compilerError)
            exit(1)

        print("root children after ", root.children)

        root: nodes.ScopeNode = root
        return root
        

