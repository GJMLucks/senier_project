import unittest
import random
from printing_chessboard import *

# module that needs to be tested

from chess_module import *

from chess_bitmap_module import *
from bit_board_chess import Chess

# module test

class BitBoardTest(unittest.TestCase):
    def test_rotateLeft64int(self):
        random_bitboard = random.randint(0, 0x1 << 64)

        for offset in range(-64, 65):
            if offset > 0:
                self.assertEqual(rotateLeft64int(random_bitboard, offset),
                                 (random_bitboard << offset) | (random_bitboard >> (64 - offset)))
                continue
            self.assertEqual(rotateLeft64int(random_bitboard, offset),
                             (random_bitboard >> -offset) | (random_bitboard << (64 + offset)))


    def test_occludedFill(self):
        for testcase in range(8):
            # N, E, S, W possible squares
            possibleSquares1 = 0xffffffffffffffff >> (testcase * 8)
            possibleSquares2 = (0xff >> testcase) \
                * 0x0101010101010101
            possibleSquares3 = 0xffffffffffffffff << (testcase * 8)
            possibleSquares4 = ((0xff << testcase) & 0xff) \
                * 0x0101010101010101

            soloBlocker1 = 0xffffffffffffffff - \
                (0x1 << 72 - testcase * move_shift[NoEa])
            soloBlocker2 = 0xffffffffffffffff - \
                ((0x1 << 49) >> 49 - testcase * -move_shift[SoEa])
            soloBlocker3 = 0xffffffffffffffff - \
                ((0x1 << 54) >> 63 - testcase * -move_shift[SoWe])
            soloBlocker4 = 0xffffffffffffffff - \
                (0x1 << 63 - testcase * move_shift[NoWe])

            self.assertEqual(occludedFill(0x1, possibleSquares1, NoEa),
                             0x8040201008040201 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x1, possibleSquares2, NoEa),
                             0x8040201008040201 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x1, soloBlocker1, NoEa),
                             0x8040201008040201 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x0100000000000000, possibleSquares2, SoEa),
                             0x0102040810204080 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x0100000000000000, possibleSquares3, SoEa),
                             0x0102040810204080 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x0100000000000000, soloBlocker2, SoEa),
                             0x0102040810204080 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x8000000000000000, possibleSquares3, SoWe),
                             0x8040201008040201 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x8000000000000000, possibleSquares4, SoWe),
                             0x8040201008040201 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x8000000000000000, soloBlocker3, SoWe),
                             0x8040201008040201 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x80, possibleSquares4, NoWe),
                             0x0102040810204080 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x80, possibleSquares1, NoWe),
                             0x0102040810204080 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x80, soloBlocker4, NoWe),
                             0x0102040810204080 & (0xffffffffffffffff >> (testcase * 8)))

    def test_popCount(self):
        self.assertEqual(popCount(0x0101010101010101), 8)
        self.assertEqual(popCount(0x0100110001110101), 8)
        self.assertEqual(popCount(0x0000100001000010), 3)
        self.assertEqual(popCount(0x7000000700030000), 8)
        self.assertEqual(popCount(0x700f000700030000), 12)
        self.assertEqual(popCount(0x7003730070003000), 15)
        self.assertEqual(popCount(0x1234567890000000), 15)

    def test_bitScan(self):
        for _ in range(64):
            random_int32 = random.randint(0, (0x1 << 32) - 1)
            self.assertEqual(bitScanReverse((0x1 << 32) + random_int32), 32)
            self.assertEqual(bitScanForward(
                (random_int32 << 32) + 0x80000000), 31)
            self.assertEqual(bitScan((0x1 << 32) + random_int32, True), 32)
            self.assertEqual(
                bitScan((random_int32 << 32) + 0x80000000, False), 31)

    def test_getRayBlocks(self):
        random_int_list = [random.randint(0, (0x1 << (9 * (length + 1))) - 1)
                           for length in range(6)]

        for length in range(6):
            self.assertEqual(getRayProtected((random_int_list[length] << (55 - length * 9)) | (0x1 << (54 - length * 9)), NoEa, 0),
                             rayAttacks[NoEa][54 - length * 9])
            self.assertEqual(getRayProtected(random_int_list[length] | (0x1 << (9 + length * 9)), SoWe, 63),
                             rayAttacks[SoWe][9 + length * 9])

    def test_getPawnForward(self):
        random_square = random.randint(48, 55)
        self.assertEqual(getPawnForward(0xffffffffffffffff, random_square, 1),
                         (0x101 << random_square) >> 16)
        random_square = random.randint(8, 15)
        self.assertEqual(getPawnForward(0xffffffffffffffff, random_square, 0),
                         (0x101 << (random_square + 8)) & 0xffffffffffffffff)
        random_square = random.randint(0, 63)
        self.assertEqual(getPawnForward(0xffffffffffffffff - ((0x1 << random_square) >> 8), random_square, 1),
                         0x0)
        random_square = random.randint(0, 63)
        self.assertEqual(getPawnForward(0xffffffffffffffff - ((0x1 << (random_square + 8)) & 0xffffffffffffffff), random_square, 0),
                         0x0)
        random_square = random.randint(0, 63)
        self.assertEqual(getPawnForward(0xffffffffffffffff - ((0x1 << random_square) >> 16), random_square, 1),
                         (0x1 << random_square) >> 8)
        random_square = random.randint(0, 63)
        self.assertEqual(getPawnForward(0xffffffffffffffff - ((0x1 << (random_square + 16)) & 0xffffffffffffffff), random_square, 0),
                         (0x1 << (random_square + 8)) & 0xffffffffffffffff)

    def test_getPawnAttacks(self):
        for _ in range(64):
            random_squares = [random.randint(0, 63) for _ in range(2)]
            basePawnattacks = [EastOnestep((0x1 << random_squares[color]))
                               | westOnestep((0x1 << random_squares[color]))
                               for color in range(2)]
            for color in range(2):
                self.assertEqual(getPawnAttacks(0xffffffffffffffff, random_squares[color], color),
                                 ((basePawnattacks[color] << 8) >> (color << 4)) & 0xffffffffffffffff)

    def test_getKnightAttacks(self):
        # getKnightAttacks : return knightAttacks[square] & notSamecolored
        None

    def test_getKnightsAttacks(self):
        # const
        firstBaseAttacks = [0x040000, 0x10040000, 0x0800040000]

        soloAttacks = knightAttacks[18]
        duoAttacks1 = soloAttacks | knightAttacks[28]
        duoAttacks2 = soloAttacks | knightAttacks[35]

        secondBaseAttacks = [soloAttacks, duoAttacks1, duoAttacks2]

        for _ in range(64):
            # const for loop
            random_offsets = [
                random.randint(0, 3) + (random.randint(0, 3) << 3),
                random.randint(0, 1) + (random.randint(0, 2) << 3),
                random.randint(0, 2) + (random.randint(0, 1) << 3)
            ]

            for loop in range(3):
                first = getKnightsAttacks(
                    firstBaseAttacks[loop] << random_offsets[loop])
                second = secondBaseAttacks[loop] << random_offsets[loop]

                self.assertEqual(first, second,
                                 f"\nloop : {loop}, offset : {random_offsets[loop]}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}")

    def test_getBishopAttacks(self):

        random_square = (random.randint(1, 6) << 3) + random.randint(1, 6)
        for direction in range(8):
            first = getBishopAttacks(
                0x1 << random_square + move_shift[direction],
                random_square)
            second = bishopAttacks[random_square]
            if direction & 0x1 == 0:
                second \
                    ^= rayAttacks[direction][random_square + move_shift[direction]]
            self.assertEqual(first, second,
                             f"\ndirection : {direction}, square : {random_square}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}")

    def test_getRookAttacks(self):

        random_square = (random.randint(1, 6) << 3) + random.randint(1, 6)
        for direction in range(8):
            first = getRookAttacks(
                0x1 << random_square + move_shift[direction],
                random_square)
            second = rookAttacks[random_square]
            if direction & 0x1 == 1:
                second \
                    ^= rayAttacks[direction][random_square + move_shift[direction]]
            self.assertEqual(first, second,
                             f"\ndirection : {direction}, square : {random_square}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}")

    def test_getQueenAttacks(self):

        random_square = (random.randint(1, 6) << 3) + random.randint(1, 6)
        for direction in range(8):
            first = getQueenAttacks(
                0x1 << random_square + move_shift[direction],
                random_square)
            second = queenAttacks[random_square]
            second ^= rayAttacks[direction][random_square +
                                            move_shift[direction]]
            self.assertEqual(first, second,
                             f"\ndirection : {direction}, square : {random_square}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}")

    def test_getKingAttacks(self):
        # getKingAttacks : return KingAttacks[square] & notSamecolored
        None

    def test_pinnedPieces(self):
        # if color is same, absoluted pins
        # if color is different, discovered checkers
        baseTestBoard = [
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            black+bishop,   empty,          black +
            queen,    empty,          empty,          empty,          empty,          empty,
            empty,          black+knight,   white+knight,   black +
            knight,   empty,          empty,          empty,          empty,
            black+bishop,   black+knight,   white+king,     black +
            knight,   black+queen,    empty,          empty,          empty,
            empty,          black+knight,   white+knight,   black +
            knight,   empty,          empty,          empty,          empty,
            black+queen,    empty,          black+rook,     empty,          black +
            rook,     empty,          empty,          empty
        ]

        baseTestBBs = Board2BitBoardSet(baseTestBoard)

        for _ in range(64):
            random_offset = random.randint(0, 3) + (random.randint(0, 3) << 3)
            testBBs = [rotateLeft64int(baseTestBBs[i], random_offset)
                       for i in range(10)]

            first = pinnedPieces(testBBs, white)
            second = 0x06080600 << random_offset

            self.assertEqual(first, second,
                             f"\nsquare : {18 + random_offset}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}\
                            \n bitboard : {getBitBoardSetString(testBBs)}")

    def test_getAttackers(self):
        baseTestBoard = [
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            white + bishop, empty,          white + queen,  empty,          black +
            bishop, empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            white + rook,   white + knight, empty,          black +
            knight, black + rook,   empty,          empty,          empty,
            empty,          white + pawn,    empty,          black +
            pawn,   empty,          empty,          empty,          empty,
            empty,          white + knight, black + queen,  black +
            knight, empty,          empty,          empty,          empty
        ]

        baseTestBBs = Board2BitBoardSet(baseTestBoard)

        for _ in range(8):
            random_offset = random.randint(0, 3) + (random.randint(0, 3) << 3)
            testBBs = [rotateLeft64int(baseTestBBs[i], random_offset)
                       for i in range(10)]

            first = getAttackers(testBBs, 18 + random_offset, black)
            second = 0x000000100000080c << random_offset

            self.assertEqual(first, second,
                             f"\nsquare : {18 + random_offset}\
                            \n first : \n{getBitBoardString(first)}\
                            \n second : \n{getBitBoardString(second)}\
                            \n bitboard : {getBitBoardSetString(testBBs)}")

    def test_possibleMove(self):
        # base data for generating test suite
        baseTestBoard = [
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            black + bishop, empty,          empty,          empty,          black +
            rook,   empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            empty,          black + king,   white + bishop, empty,          white +
            bishop, empty,          empty,          empty,
            empty,          empty,          empty,          empty,          empty,          empty,          empty,          empty,
            black + queen,  empty,          white + rook,   empty,          white +
            king,   empty,          empty,          empty
        ]
        baseTestBBs = Board2BitBoardSet(baseTestBoard)
        baseTestSquares = [18, 2, 36, 0]
        baseTestResult = [0x0000000102000800, 0x000000000000000b,
                          0x0000000e10100000, 0x0000000001050306]

        for _ in range(16):
            random_offset = random.randint(0, 3) + (random.randint(0, 3) << 3)

            # test suite
            testBBs = [rotateLeft64int(baseTestBBs[i], random_offset)
                       for i in range(10)]
            testBoard = []
            testResult = [baseTestResult[i] << random_offset for i in range(4)]
            testResult[2] |= (getRayAttacks(0x0, 1,
                                            (baseTestSquares[2] + random_offset)))
            testResult[2] |= (getRayAttacks(0x0, 3,
                                            (baseTestSquares[2] + random_offset)))
            testResult[3] |= (getRayAttacks(0x0, 0,
                                            (baseTestSquares[3] + random_offset)))
            testResult[3] |= (getRayAttacks(0x0, 4,
                                            (baseTestSquares[3] + random_offset)))
            testResult[3] |= (getRayAttacks(0x0, 5,
                                            (baseTestSquares[3] + random_offset)))
            testResult[3] |= (getRayAttacks(0x0, 6,
                                            (baseTestSquares[3] + random_offset)))
            testResult[3] |= (getRayAttacks(0x0, 7,
                                            (baseTestSquares[3] + random_offset)))
            # get testBoard
            for rank in range(7, -1, -1):
                for file in range(8):
                    index = 8 * rank + file
                    piece = empty

                    if testBBs[nEmpty] & (1 << index):
                        testBoard.append(piece)
                        continue

                    for color in range(2):
                        if testBBs[color] & (1 << index):
                            piece = (1 << color)
                            break

                    for pieceType in range(2, 8):
                        if testBBs[pieceType] & (1 << index):
                            piece |= (1 << pieceType)
                            break

                    testBoard.append(piece)

            for i in range(4):
                # args
                currentPosition = baseTestSquares[i] + random_offset
                first = possibleMove(testBBs,
                                     testBoard,
                                     currentPosition)
                second = testResult[i] & 0xffffffffffffffff

                # test
                self.assertEqual(first, second,
                                 f"\nsquare : {baseTestSquares[i] + random_offset}\
                                \n first : \n{getBitBoardString(first)}\
                                \n second : \n{getBitBoardString(second)}\
                                \n piece : \n{str(testBoard[(8*(7 - (currentPosition >> 3)) + (currentPosition & 0b111))])}\
                                \n bitboard : \n{getBitBoardSetString(testBBs)}")


# precalculated perft results
perftTestcasesResults = \
    [[20, 400, 8902, 197281, 4865609],
     [48, 2039, 97862, 4085603, 193690690],
     [14, 191, 2812, 43238, 674624],
     [6, 264, 9467, 422333, 15833292],
     [44, 1486, 62379, 2103487, 89941194],
     [46, 2079, 89890, 3894594, 164075551]]

# initial Positions for perft test
perftTestInitPositions = \
    ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -",
     "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -",
     "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
     "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
     "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"]

if __name__ == '__main__':
    f = open("test_result.txt", "a")
    
    chess = Chess()
    
    # basic testcase
    for depth in range(1, 6):
        # set initial position
        chess.reset()
        chess._set(perftTestInitPositions[0])

        # process
        perftResult = chess.perftDivide(depth)
        if perftResult == perftTestcasesResults[0][depth - 1]:
            print(f'Perft({depth}) : {perftResult}')
            print(f'testcase0 - depth {depth} Done')
            f.write(f'Perft({depth}) : {perftResult}\n')
            f.write(f'testcase0 - depth {depth} Done\n')
        else:
            print(f'Perft({depth}) : {perftResult} (wrong)\n')
            f.write(f'Perft({depth}) : {perftResult} (wrong)\n')
            f.close()
            raise Exception

    # testcase 2 ~ 6
    for testcaseIndex in range(1, 6):
        for depth in range(1, 5):
            # set initial position
            chess.reset()
            chess._set(perftTestInitPositions[testcaseIndex])

            # process
            perftResult = chess.perftDivide(depth)
            if perftResult == perftTestcasesResults[testcaseIndex][depth - 1]:
                print(f'Perft({depth}) : {perftResult}')
                print(f'testcase{testcaseIndex+1} - depth {depth} Done')
                f.write('Perft({depth}) : {perftResult}\n')
                f.write(f'testcase{testcaseIndex+1} - depth {depth} Done\n')
            else:
                print(f'Perft({depth}) : {perftResult} (wrong)\n')
                f.write('Perft({depth}) : {perftResult} (wrong)\n')
                f.close()
                raise Exception

    f.close()

    # temp code : unittest.main()
