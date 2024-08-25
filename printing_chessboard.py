from const_variable import *


def printpiece(pieceplacement: list[int], index: int) -> None:
    if 0 > index or index >= 64:
        raise ValueError("index is out of range")

    piece = pieceplacement[index]

    # empty check
    if piece == empty:
        print("| __ ", end="")
        return


    piece_color = piece & 0b00000011
    piece_type = piece & 0b11111100

    if not piece_type or not piece_color:
        raise ValueError("undefined piece")

    print("| ", end="")


    if piece_color == 0b11:
        raise ValueError("undefined piece_color")

    print("w" if piece_color == 1 else "b", end="")


    for i in range(2, 8):
        if piece_type == 1 << i:
            print(pieceLiteral[i - 2], end=" ")
            break
        if i == 7:
            raise ValueError("undefined piece_type")

    return


def printchess(pieceplacement: list[int]) -> None:
    print("  *=======================================*")

    for i in range(8):
        # rank index
        print(8-i, end=" ")

        # piece initial
        for j in range(8):
            printpiece(pieceplacement, i*8 + j)

        print("|")
        if i == 7:
            break

        print("  -----------------------------------------")

    print("  *=======================================*")
    print("     a    b    c    f    e    f    g    h ")
    print("    (1)  (2)  (3)  (4)  (5)  (6)  (7)  (8)")


def getBitBoardString(board: int) -> str:
    s = ""
    for rank in range(7, -1, -1):
        for file in range(8):
            s += "1 " if board & (0x1 << (8 * rank + file)) else ". "
        s += "\n"
    return s


def getBitBoardSetString(bitBoardSet: list) -> str:
    s = "\n"
    for BBSetIndex in range(10):
        s += f"{bitBoardSetIndexNames[BBSetIndex]} : \n"
        s += getBitBoardString(bitBoardSet[BBSetIndex])
    return s


def printBitBoard(board: int):
    for rank in range(7, -1, -1):
        for file in range(8):
            print("1" if board & (0x1 << (8 * rank + file)) else "0", end="")
        print()
    print()
