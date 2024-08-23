# move offset

# clock wise, start north direction
# : [ NW, N, NE, E, SE, S, SW, W ]

NoWe, Nort, NoEa, East, SoEa, Sout, SoWe, West = range(8)

move_shift = (7, 8, 9, 1, -7, -8, -9, -1)
knight_move_offset = (-15, -6, 10, 17, 15, 6, -10, -17)


# const_variable for board-array representation

# Piece coding
empty = 0

# color : 1, 2
colors = [1 << shift for shift in range(2)]
white, black = colors

# pawn ~ king : 1 << 2 ~ 7
pieceTypes = [1 << shift for shift in range(2, 8)]
pawn, knight, bishop, rook, queen, king = pieceTypes

pieceLiteral = ("P", "R", "N", "B", "Q", "K")

defaultBoardPlacement = {
    black + rook, black + knight, black + bishop, black +
    queen, black + king, black + bishop, black + knight, black + rook,
    black + pawn, black + pawn, black + pawn, black +
    pawn, black + pawn, black + pawn, black + pawn, black + pawn,
    empty, empty, empty, empty, empty, empty, empty, empty,
    empty, empty, empty, empty, empty, empty, empty, empty,
    empty, empty, empty, empty, empty, empty, empty, empty,
    empty, empty, empty, empty, empty, empty, empty, empty,
    white + pawn, white + pawn, white + pawn, white +
    pawn, white + pawn, white + pawn, white + pawn, white + pawn,
    white + rook, white + knight, white + bishop, white +
    queen, white + king, white + bishop, white + knight, white + rook
}


# const_variable for bitboard representation

# remove wrapping made by shifting
# it corresponds to each direction and move_shift


avoidWrap = [
    0x7f7f7f7f7f7f7f00,
    0xffffffffffffff00,
    0xfefefefefefefe00,
    0xfefefefefefefefe,
    0x00fefefefefefefe,
    0x00ffffffffffffff,
    0x007f7f7f7f7f7f7f,
    0x7f7f7f7f7f7f7f7f
]

# bitBoardSetIndex
# : [ anywhite, anyblack, // pawn, knight, bishop, rook, queen, king, // antPieces, emptySquare ]
nWhite, nBlack, nPawn, nKnight, nBishop, nRook, nQueen, nKing, nPiece, nEmpty \
    = range(10)

bitBoardSetIndexNames = ["nWhite", "nBlack", "nPawn", "nKnight",
                         "nBishop", "nRook", "nQueen", "nKing", "nPiece", "nEmpty"]

# initial boards
# Mapping direction : Little-Endian Rank-File Mapping
bitBoardDefaultSet = {
    0x000000000000FFFF,  # any white pieces
    0xFFFF000000000000,  # any black pieces
    0x00FF00000000FF00,  # pawns sets
    0x2400000000000024,  # knight sets
    0x4200000000000042,  # bishop sets
    0x8100000000000081,  # rook sets
    0x0800000000000008,  # queen sets
    0x1000000000000010,  # king sets
    0xFFFF00000000FFFF,  # any pieces
    0x0000FFFFFFFF0000,  # empty squares
}
