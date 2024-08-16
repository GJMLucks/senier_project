import unittest
import random

# module that needs to be tested

from chess_bitmap_module import *

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
            possibleSquares1 = 0x00000000000000ff << (64 - testcase * 8)
            possibleSquares2 = ((0xff << (8 - testcase)) & 0xff) \
                * 0x0101010101010101
            possibleSquares3 = 0xff00000000000000 >> (64 - testcase * 8)
            possibleSquares4 = (0xff >> (8 - testcase)) \
                * 0x0101010101010101

            self.assertEqual(occludedFill(0x1, possibleSquares1, NoEa),
                             0x8040201008040201 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x1, possibleSquares2, NoEa),
                             0x8040201008040201 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x0100000000000000, possibleSquares2, move_shift[SoEa]),
                             0x0102040810204080 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x0100000000000000, possibleSquares3, move_shift[SoEa]),
                             0x0102040810204080 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x8000000000000000, possibleSquares3, move_shift[SoWe]),
                             0x8040201008040201 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x8000000000000000, possibleSquares4, move_shift[SoWe]),
                             0x8040201008040201 & (0xffffffffffffffff << (testcase * 8)))
            self.assertEqual(occludedFill(0x80, possibleSquares4, move_shift[NoWe]),
                             0x0102040810204080 & (0xffffffffffffffff >> (testcase * 8)))
            self.assertEqual(occludedFill(0x80, possibleSquares1, move_shift[NoWe]),
                             0x0102040810204080 & (0xffffffffffffffff >> (testcase * 8)))


if __name__ == '__main__':
    unittest.main()
