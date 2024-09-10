from const_variable import *


def printpiece(piece: int) -> None:
    # empty check
    if piece == empty:
        print("| __ ", end="")
        return


    piece_color = piece & 0b00000011
    piece_type = piece & 0b11111100

    if not piece_type or not piece_color:
        raise ValueError(f'undefined piece : {piece}')

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
            printpiece(pieceplacement[i*8 + j])

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

def printBitMap(bitMap: int):
    for rank in range(7, -1, -1):
        for file in range(8):
            print("1" if bitMap & (0x1 << (8 * rank + file)) else "0", end="")
        print()
    print()

def printBitMaps(bitMaps: list[int]):
    print(f'nWhite\tnBlack\tnPawn\tnKnight\tnBishop\tnRook\tnQueen\tnKing\tnPiece\tnEmpty')
    for rank in range(7, -1, -1):
        for index in range(10):
            for file in range(8):
                print("1" if bitMaps[index] & (0x1 << (8 * rank + file)) else "0", end="")
            print(end="\t")
        print()
    print()

def printMove(move: Move):
    fromSquare = move.fromSquare
    toSquare = move.toSquare
    
    print(f'move : {chr(ord('a') + (fromSquare & 0x7))}{chr(ord('1') + (fromSquare >> 3))}{chr(ord('a') + (toSquare & 0x7))}{chr(ord('1') + (toSquare >> 3))}')