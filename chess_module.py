from const_variable import *


def algebraic2index(algebraic: str) -> int:
    # variables
    index = 0

    # raises
    if len(algebraic) != 2:
        raise ValueError("invalid algebraic notation")
    if not ('a' <= algebraic[0] <= 'h' and '1' <= algebraic[1] <= '8'):
        raise ValueError("invalid algebraic notation")

    # process
    index += ord(algebraic[0]) - ord('a')
    index += 8 * (ord(algebraic[1]) - ord('1'))

    return index


def FENboard2board(FENboard: str) -> list[int]:
    # variables
    board = [empty for _ in range(64)]
    index = 0

    # process
    for char in FENboard:
        if char == " ":
            break
        if char == "/":
            continue
        if char.isdigit():
            index += int(char)
            continue
        # colorType
        piece = 0
        if char.isupper():
            piece |= 0b00000001
        else:
            piece |= 0b00000010
        # pieceType
        char = char.upper()
        for i in range(7):
            if char == pieceLiteral[i]:
                piece |= (1 << (i + 2))
                break
            if i == 7:
                raise ValueError("undefined piece")

        board[index] = piece
        index += 1

    return board
