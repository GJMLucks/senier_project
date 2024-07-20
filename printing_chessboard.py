from const_variable import *


def PrintPiece(chess_positons: list[int], Pos: int) -> None:
    piece_type = chess_positons[Pos] % 8

    if piece_type == empty:
        print("| __ ", end="")
        return

    color = chess_positons[Pos]//8

    print("| ", end="")

    initial = pieceInitials[piece_type]

    # "." mean black piece
    print("b" if color else "w", end="")

    if initial:
        print(initial, end=" ")
    else:
        print("Piece Print err")
        return


# 체스 출력
def PrintChess(chess_positons: list[int]) -> None:
    print("  *=======================================*")

    for i in range(8):
        # rank number
        print(8-i, end=" ")
        # piece initial
        for j in range(8):
            PrintPiece(chess_positons, i*8 + j)
        # vertical line
        print("|")
        if i == 7:
            break
        # horizontal line
        print("  -----------------------------------------")

    print("  *=======================================*")
    print("     a    b    c    f    e    f    g    h ")
    print("    (1)  (2)  (3)  (4)  (5)  (6)  (7)  (8)")
