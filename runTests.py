
import subprocess
import pathlib







def runTest(filePath: str, expectedStdoutLines: list[str], expectedExitCode: int = 0) -> tuple[bool, str | None]:
    """Returns if test successful and reason for failure if not"""

    result = subprocess.run(["python3", "main.py", filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != expectedExitCode:
        return False, f"Expected exit code {expectedExitCode} but got {result.returncode}"
    
    resultStdoutLines = result.stdout.splitlines()
    
    if len(resultStdoutLines) != len(expectedStdoutLines):
        return False, f"Expected {len(expectedStdoutLines)} lines of stdout but got {len(resultStdoutLines)}"
    
    for resultLine, expectedLine in zip(resultStdoutLines, expectedStdoutLines):
        if resultLine != expectedLine:
            return False, f"Expected: {expectedLine}.\t Got: {resultLine}"
    
    return True, None



def main():

    testsRange = range(1, 3)

    testFiles = [f"./tests/test_{i}.lf" for i in testsRange]
    expectedStdoutLines = [[l.replace("\n", "") for l in open(f"./tests/expected_{i}.txt").readlines()] for i in testsRange]

    for testFile, expectedStdoutLines in zip(testFiles, expectedStdoutLines):
        success, reason = runTest(testFile, expectedStdoutLines)
        if not success:
            print(f"Test {testFile} failed: {reason}")
        else:
            print(f"Test {testFile} passed")


if __name__ == "__main__":
    main()
