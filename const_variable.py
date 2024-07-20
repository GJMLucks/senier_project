# Piece coding

empty = 0

# color : 1 << 0 ~ 1
white, black = [1 << shift for shift in range(2)]

# pawn ~ king : 1 << 2 ~ 7
pawn, rook, knight, bishop, queen, king = [1 << shift for shift in range(2, 8)]

pieceLiteral = ("P", "R", "N", "B", "Q", "K")

# precalculated offset
knight_move_offset = (-17, -15, -10, -6, 6, 10, 15, 17)
