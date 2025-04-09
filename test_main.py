import unittest
from tqdm import tqdm

from printing_chessboard import *

# module that needs to be tested

from chess_module import *
from chess_bitmap_module import *
from bit_board_chess import Chess


# main

if __name__ == '__main__':
    
    # import module by relative path
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
    
        from senier_project.test.test_Perft import *
        from senier_project.test.test_bitBoard_module import *
    else:
        from .test.test_Perft import *
        from .test.test_bitBoard_module import *
    
    # test Perft
    f = open("test_result.txt", "a")
    chess = Chess()
    
    # process perft test
    for testcaseIndex in range(6):
        f.write(f'testcase{testcaseIndex + 1} :\n')
        
        for depth in tqdm(range(5), desc=f'Perft Test {testcaseIndex} : '):
            # skip some tests that are too deep
            if depth == 4 and testcaseIndex:
                continue

            # set initial position
            chess.reset()
            chess._set(perftTestInitPositions[testcaseIndex])

            # process
            perftResult = chess.perftDivide(depth + 1)
            f.write(f'Perft({depth + 1}) : {perftResult}\n')
            
            if perftResult == perftTestcasesResults[testcaseIndex][depth]:
                continue
            else:
                f.write(f'Test fail in testcase{testcaseIndex + 1} - Perft({depth + 1})\n')
                f.write(f'correct answer : {perftTestcasesResults[testcaseIndex][depth]}\n')
                f.close()
                raise Exception

    f.close()
    print('Perft Test Done\n')


    # run unitmodule test
    unittest.main()
    
