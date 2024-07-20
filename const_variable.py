# empty ~ king = 000(0) ~ 110(6)
empty, pawn, rook, knight, bishop, queen, king = range(7)

pieceInitials = ("_", "P", "R", "N", "B", "Q", "K")

# white, black = 0, 8
white, black = range(0, 9, 8)

# precalculated offset
knight_move_offset = (-17, -15, -10, -6, 6, 10, 15, 17)
