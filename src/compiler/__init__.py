
import src.compiler.nodes as nodes
import src.compiler.structures as structures
import src.parser.sentences as sentences

from src.compiler.passes.scaffoldingPass import ScaffoldingPass, ScaffoldingNode
from src.compiler.passes.topDeclarationsPass import TopDeclarationsPass
from src.compiler.passes.mainPass import MainPass
from src.compiler.passes.classPass import ClassPass

from src.compiler.transformer import Transformer
import src.compiler.compilerErrors as compilerErrors

from src.base import BASE_CLASSES

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

        transformer = Transformer(allowedSentences=[])
        root = transformer.transform(scaffoldingRoot)

        topDeclarationsPass = TopDeclarationsPass()
        compilerError = topDeclarationsPass.run(root)
        if isinstance(compilerError, compilerErrors.CompilerError):
            print(compilerError)
            exit(1)

        mainFunction = self._setMainFunction(root)

        classPass = ClassPass()
        compilerError = classPass.run(root)
        if isinstance(compilerError, compilerErrors.CompilerError):
            print(compilerError)
            exit(1)

        mainPass = MainPass()
        compilerError = mainPass.run(root)
        if isinstance(compilerError, compilerErrors.CompilerError):
            print(compilerError)
            exit(1)


        mainFunction.children.append(nodes.ReturnNode(1, mainFunction, structures.LeafChain([0])))

        

        return root
        



    def _setMainFunction(self, root: nodes.ScopeNode) -> nodes.LeafFunctionDeclarationNode:
        """Sets the main function to the first function in the root, returns it"""
        

        mainLeafFunction = structures.LeafFunction("main", [], [], structures.LeafMention(None, BASE_CLASSES.INT_CLASS, []))
        mainLeafFunction.cName = "main"
        mainLeafFunction.isMain = True

        mainLeafFunctionNode = nodes.LeafFunctionDeclarationNode(1, root, mainLeafFunction)

        for child in [child for child in root.children if type(child) == nodes.ScaffoldingNode]:
            root.children.remove(child)
            mainLeafFunctionNode.children.append(child)
            child.parent = mainLeafFunctionNode

        root.children.append(mainLeafFunctionNode)

        return mainLeafFunctionNode


