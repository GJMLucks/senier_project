# Piece coding

empty = 0

# color : 1 << 0 ~ 1
colors = [1 << shift for shift in range(2)]
white, black = colors

# pawn ~ king : 1 << 2 ~ 7
pieceTypes = [1 << shift for shift in range(2, 8)]
pawn, rook, knight, bishop, queen, king = pieceTypes

pieceLiteral = ("P", "R", "N", "B", "Q", "K")

# precalculated offset
knight_move_offset = (-17, -15, -10, -6, 6, 10, 15, 17)
