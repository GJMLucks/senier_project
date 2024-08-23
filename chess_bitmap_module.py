from const_variable import *


def convertBoard2Bitmaps(board: list) -> list:
    """
    convert board to bitmaps.\n
    return list of bitboards.

    Args:
        board (list(int)) : \n
            pieces placement on board.

    Returns:
        bitmaps (list(int)) : \n
            list of bitboards that represent pieces placement on board.\n 
            bitBoardSet Index -
            [ anywhite, anyblack,
            // pawn, knight, bishop, rook, queen, king,
            // anyPieces, emptySquare ]
    """

    # variable
    bitBoardSet = [0x0 for _ in range(10)]

    for rank in range(8):
        for file in range(8):
            # variable
            index = 56 - (8 * rank) + file
            piece = board[(8 * rank) + file]

            # process
            if piece == empty:
                bitBoardSet[nEmpty] |= (1 << index)
                continue

            bitBoardSet[nPiece] |= (1 << index)
            bitBoardSet[(piece & 0b00000011) - 1] |= (1 << index)

            for pieceType in range(2, 8):
                if (piece & 0b11111100) == pieceTypes[pieceType - 2]:
                    bitBoardSet[pieceType] |= (1 << index)
                    break

    return bitBoardSet



# bit rotate operation

def rotateLeft64int(bitmap: int, offset: int) -> int:
    """
    rotate left 64bit integer bitmap by offset.\n

    Args:
        bitmap (int) : \n
            64bit integer bitmap to rotate.
        offset (int) : \n
            offset to rotate bitmap.\n
            precondition: offset is in range -64..64.

    Returns:
        bitmap (int): \n
            rotated 64bit integer bitmap.
    """

    return ((bitmap << offset) | (bitmap >> (64 - offset))) if (offset > 0) \
        else ((bitmap >> -offset) | (bitmap << (64 + offset)))



# ray-movement

def occludedFill(pieces: int, possibleSqures: int, dir8: int) -> int:
    """
    include positions itself, 
    fill squares from positions of pieces by sliding to 'dir8' direction 
    until blocked by any other pieces. 

    Args:
        pieces (int) : \n
            positions of piece to slide.
        possibleSqures (int) : \n
            empty squares.
            possible squares to fill.
        dir8 (int) : \n
            direction to slide.

    Returns:
        bitmap (int) : \n
            filled squares from positions of pieces by sliding to 'dir8' direction
    """

    # variable
    offset = move_shift[dir8]
    possibleSqures &= avoidWrap[dir8]

    # process
    pieces |= (possibleSqures & rotateLeft64int(pieces, offset))
    possibleSqures &= rotateLeft64int(possibleSqures, offset)
    pieces |= (possibleSqures & rotateLeft64int(pieces, offset << 1))
    possibleSqures &= rotateLeft64int(possibleSqures, offset << 1)
    pieces |= (possibleSqures & rotateLeft64int(pieces, offset << 2))

    return pieces



# one step functions

# variables for one step functions

notAFile = 0xfefefefefefefefe
notHFile = 0x7f7f7f7f7f7f7f7f


# functions

def noWeOneStep(bitBoard: int):
    return (bitBoard << 7) & notHFile

def nortOnestep(bitBoard: int):
    return bitBoard << 8 & 0xffffffffffffffff

def noEaOnestep(bitBoard: int):
    return (bitBoard << 9) & notAFile

def EastOnestep(bitBoard: int):
    return (bitBoard << 1) & notAFile

def soEaOnestep(bitBoard: int):
    return (bitBoard >> 7) & notAFile

def soutOnestep(bitBoard: int):
    return bitBoard >> 8 & 0xffffffffffffffff

def soWeOnestep(bitBoard: int):
    return (bitBoard >> 9) & notHFile

def westOnestep(bitBoard: int):
    return (bitBoard >> 1) & notHFile



# precalculated attacks

# variables for precalculation

boundary = 0xffffffffffffffff

basenort = 0x0101010101010100
basesout = 0x0080808080808080
basenowe = 0x0102040810204000
basenoea = 0x8040201008040200
baseeast = 0x00000000000000fe
basesoea = 0x0002040810204080
basesowe = 0x0040201008040201
basewest = 0x7f00000000000000

rayAttacks = [[0x0000000000000000 for i in range(64)] for j in range(8)]


# precalculations

# [ north, south ]

for position in range(64):
    rayAttacks[Nort][position] = basenort
    basenort = (basenort << 1) & boundary

    rayAttacks[Sout][63 - position] = basesout
    basesout >>= 1

# [ NoWest, NoEast, East, SoEast, SoWest, West]

for file in range(8):
    tempNowe = basenowe
    tempnoea = basenoea
    tempeast = baseeast
    tempsoea = basesoea
    tempsowe = basesowe
    tempwest = basewest

    for rank in range(8):
        rayAttacks[NoWe][8 * rank + (7 - file)] = tempNowe
        tempNowe = (tempNowe << 8) & boundary

        rayAttacks[NoEa][8 * rank + file] = tempnoea
        tempnoea = (tempnoea << 8) & boundary

        rayAttacks[East][8 * rank + file] = tempeast
        tempeast = (tempeast << 8) & boundary

        rayAttacks[SoEa][56 - 8 * rank + file] = tempsoea
        tempsoea >>= 8

        rayAttacks[SoWe][63 - 8 * rank - file] = tempsowe
        tempsowe >>= 8

        rayAttacks[West][63 - 8 * rank - file] = tempwest
        tempwest >>= 8

    basenowe = westOnestep(basenowe)
    basenoea = EastOnestep(basenoea)
    baseeast = EastOnestep(baseeast)
    basesoea = EastOnestep(basesoea)
    basesowe = westOnestep(basesowe)
    basewest = westOnestep(basewest)

# ray Attacks

rankAttacks = [rayAttacks[Nort][position] |
               rayAttacks[Sout][position] |
               (0x1 << position) for position in range(64)]
fileAttacks = [rayAttacks[East][position] |
               rayAttacks[West][position] |
               (0x1 << position) for position in range(64)]
diagAttacks = [rayAttacks[NoEa][position] |
               rayAttacks[SoWe][position] |
               (0x1 << position) for position in range(64)]
antidiagAttacks = [rayAttacks[NoWe][position] |
                   rayAttacks[SoEa][position] |
                   (0x1 << position) for position in range(64)]

# piece Attacks

# rook, bishop, queen Attacks

rookAttacks = [rankAttacks[position] | fileAttacks[position]
               for position in range(64)]
bishopAttacks = [diagAttacks[position] | antidiagAttacks[position]
                 for position in range(64)]
queenAttacks = [rookAttacks[position] | bishopAttacks[position]
                for position in range(64)]

# knight and king Attacks

baseKingAttack = 0x01c1c1c0000000000000
baseKnightAttack = 0x0

kingMoveSqures = [[basePosition] for basePosition in range(64)]

for position in range(64):
    if position & 0x7 != 0:
        kingMoveSqures[position].append(position - 1)
    if position & 0x7 != 7:
        kingMoveSqures[position].append(position + 1)
    if position >> 3 != 0:
        upperKingMoveSqures \
            = [basePosition - 8 for basePosition in kingMoveSqures[position]]
        kingMoveSqures[position].extend(upperKingMoveSqures)
    if position >> 3 != 7:
        lowerKingMoveSqures \
            = [basePosition + 8 for basePosition in kingMoveSqures[position]]
        kingMoveSqures[position].extend(lowerKingMoveSqures)
    kingMoveSqures[position].remove(position)

for offset in knight_move_offset:
    if offset > 0:
        baseKnightAttack |= (1 << 63) << offset
    else:
        baseKnightAttack |= (1 << 63) >> -offset

KingAttacks = [0x0 for _ in range(64)]
knightAttacks = [0x0 for _ in range(64)]

for position in range(64):
    knightAttack = baseKnightAttack >> position
    kingAttack = baseKingAttack >> position

    if (position & 0x7) >> 1 == 0x3:
        knightAttack &= 0x3f3f3f3f3f3f3f3f
        kingAttack &= 0x3f3f3f3f3f
    elif (position & 0x7) >> 1 == 0x0:
        knightAttack &= 0xfcfcfcfcfcfcfcfc
        kingAttack &= 0xfcfcfcfcfcfcfcfc

    knightAttacks[63 - position] = knightAttack & 0xffffffffffffffff
    KingAttacks[63 - position] = kingAttack & 0xffffffffffffffff



# population count
# https://www.chessprogramming.org/Population_Count

def popCount(bitBoard: int) -> int:
    """
    return number of '1' in int64(bitBoard)

    Args:
        bitBoard (int) : \n
            int64 to count

    Returns:
        int : \n
            number of '1' in int64(bitBoard)
    """
    # count each 2bit
    bitBoard -= (bitBoard >> 1) & 0x5555555555555555

    # count each 4bit
    bitBoard = (bitBoard & 0x3333333333333333) + \
        ((bitBoard >> 2) & 0x3333333333333333)

    # count each 8bit
    bitBoard = (bitBoard & 0x0f0f0f0f0f0f0f0f) + \
        ((bitBoard >> 4) & 0x0f0f0f0f0f0f0f0f)

    return ((bitBoard * 0x0101010101010101) >> 56) & 0xff



# bitScan function

# bitScanForward LSB

def bitScanForward(bitBoard: int) -> int:
    """
    index(0..63) of least significant one bit of bitBoard
    
    Raises:
        ValueError : \n
            bitBoard is zero

    Args:
        bitBoard (int) : \n
            bitboard to scan
            precondition: bitBoard != 0

    Returns:
        LS1B (int) : \n
            index(0..63) of least significant one bit
    """
    if bitBoard == 0:
        raise ValueError('{__myname__} : bitBoard is zero')

    return (popCount((bitBoard & -bitBoard) - 1))


# bitScanReverse MSB

index64 = [0, 47,  1, 56, 48, 27,  2, 60,
           57, 49, 41, 37, 28, 16,  3, 61,
           54, 58, 35, 52, 50, 42, 21, 44,
           38, 32, 29, 23, 17, 11,  4, 62,
           46, 55, 26, 59, 40, 36, 15, 53,
           34, 51, 20, 43, 31, 22, 10, 45,
           25, 39, 14, 33, 19, 30,  9, 24,
           13, 18,  8, 12,  7,  6,  5, 63]


def bitScanReverse(bitBoard: int) -> int:
    """
    index(0..63) of most significant one bit of bitBoard
    @authors Kim Walisch, Mark Dickinson
    
    Raises:
        ValueError : \n
            bitBoard is zero

    Args:
        bitBoard (int) : \n
            bitboard to scan
            precondition: bitBoard != 0

    Returns:
        MS1B (int) : \n
            index(0..63) of most significant one bit
    """

    if bitBoard == 0:
        raise ValueError('{__myname__} : bitBoard is zero')

    bitBoard |= bitBoard >> 1
    bitBoard |= bitBoard >> 2
    bitBoard |= bitBoard >> 4
    bitBoard |= bitBoard >> 8
    bitBoard |= bitBoard >> 16
    bitBoard |= bitBoard >> 32

    return index64[((bitBoard * 0x03f79d71b4cb0a89) >> 58) & 0x3f]


# generalized bitScan

def bitScan(bitBoard: int, reverse: bool) -> int:
    """
    index(0..63) of least/most significant one bit of bitBoard.
    generalized bitScan that include forward and reverse bitScan.
    @author Gerd Isenberg

    Raises:
        ValueError : \n
            bitBoard is zero. (implemented in inner function)

    Args:
        bitBoard (int) : \n
            int64 bitBoard to bitScan
        reverse (bool) : \n
            reverse bitScan if True, forward bitScan if False

    Returns:
        LS1B/MS1B (int) : \n
            index (0..63) of least/most significant one bit
    """

    return bitScanReverse(bitBoard) if reverse else bitScanReverse(bitBoard & -bitBoard)


# ray-movement module

# precalculated masks and bit for generalizing direction

dirMask = [0x0000000000000000, 0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
           0xffffffffffffffff, 0xffffffffffffffff, 0xffffffffffffffff, 0xffffffffffffffff]
dirBit = [0x8000000000000000, 0x8000000000000000, 0x8000000000000000, 0x8000000000000000,
          0x0000000000000001, 0x0000000000000001, 0x0000000000000001, 0x0000000000000001]


def getRayProtected(occupied: int, direction: int, square: int) -> int:
    """
    return bitmap that are protected by blocker from 'direction' attack from 'square'.

    Args:
        occupied (int) : \n
            bitmap of any pieces
        direction (int) : \n
            direction of attack
        square (int) : \n
            position of attacker

    Returns:
        bitmap (int) : \n
            bitmap that are protected by blocker
    """

    attacks = rayAttacks[direction][square]
    blocker = attacks & occupied
    blocker |= dirBit[direction]
    blocker &= ((-blocker) | dirMask[direction])
    square = bitScanReverse(blocker)

    return rayAttacks[direction][square]


def getRayAttacks(occupied: int, direction: int, square: int) -> int:
    """
    return bitmap that able to attack from square by 'direction'.
    
    caution: this function does not consider blocker's color\n
    therefore, blocker could be same color as attacker.
    
    Args:
        occupied (int) : \n
            bitmap of any pieces
        direction (int) : \n
            direction of attack
        square (int) : \n
            position of attacker

    Returns:
        bitmap (int) : \n
            bitmap that able to attack from square by 'direction'.
    """

    return rayAttacks[direction][square] ^ getRayProtected(occupied, direction, square)



# piece movement module

def getPawnForward(emptied: int, square: int, isBlack: int) -> int:
    """
    return bitmap of possible forward movement of pawn for square

    Raises:
        ValueError : \n
            square/isBlack is out of range

    Args:
        emptied (int) : \n
            bitmap of empty squares
        square (int) : \n
            position of pawn
        isBlack (int): \n
            if True, black pawn, if False, white pawn

    Returns:
        bitmap (int) : \n
            bitmap of possible forward movement of pawn
    """

    if square >> 6 or isBlack >> 1:
        raise ValueError('{__myname__} : square/isBlack is out of range')

    # one Forward
    oneforward = emptied\
        & (0x800000000000000000 >> (63 - square + (isBlack << 4)))

    # two Forward
    twoforward = emptied\
        & (((0x00FF00000000FF00 & (1 << square)) << 16) >> (isBlack << 5))

    return oneforward | (twoforward & ((oneforward << 8) >> (isBlack << 4)))


def getPawnAttacks(occupied: int, square: int, isBlack: int):
    """
    return bitmap of possible attack of pawn for square

    Raises:
        ValueError : \n
            square/isBlack is out of range

    Args:
        occupied (int) : \n
            bitmap of any pieces
        square (int) : \n
            position of pawn
        isBlack (int): \n
            if True, black pawn, if False, white pawn

    Returns:
        bitmap (int) : \n
            bitmap of possible attack of pawn
    """

    if square >> 6 or isBlack >> 1:
        raise ValueError('{__myname__} : square/isBlack is out of range')

    forwardMask \
        = (0x01400140000000000000 >> (63 - square)) \
        & (0x00FF0000000000000000 >> (((63 - square) & 0b111000) + (isBlack << 4)))

    return occupied & forwardMask

# TODO: an passant function


def getKnightAttacks(notSamecolored: int, square: int) -> int:
    """
    get bitmap of knight attacks for square

    Args:
        notSamecolored (int) : \n
            bitmap of not same colored pieces, include empty squares
        square (int): \n
            position of knight

    Returns:
        bitmap : \n
            bitmap of possible knight attacks for square
    """

    return knightAttacks[square] & notSamecolored


def getKnightsAttacks(knights: int) -> int:
    """
    return bitmap of possible multiple knight attacks for square

    Args:
        knights (int) : \n
            positions of knights

    Returns:
        bitmap : \n
            position of possible multiple knight attacks for square
    """

    l1 = (knights >> 1) & 0x7f7f7f7f7f7f7f7f
    l2 = (knights >> 2) & 0x3f3f3f3f3f3f3f3f
    r1 = (knights << 1) & 0xfefefefefefefefe
    r2 = (knights << 2) & 0xfcfcfcfcfcfcfcfc
    h1 = l2 | r2
    h2 = l1 | r1

    return (h1 << 8) | (h1 >> 8) | (h2 << 16) | (h2 >> 16)


def getBishopAttacks(occupied: int, square: int) -> int:
    """
    return bitmap of possible bishop attacks for square

    caution: this function does not consider blocker's color\n
    therefore, blocker could be same color as attacker.
    
    Args:
        occupied (int): \n
            bitmap of any pieces
        square (int): \n
            position of bishop

    Returns:
        bitmap : \n
            bitmap of possible bishop attacks for square
    """

    # edge square could be same color
    attacks = bishopAttacks[square]
    for direction in range(0, 8, 2):
        attacks ^= getRayProtected(occupied, direction, square)

    return attacks


def getRookAttacks(occupied: int, square: int):
    """
    return bitmap of possible rook attacks for square

    caution: this function does not consider blocker's color\n
    therefore, blocker could be same color as attacker.
    
    Args:
        occupied (int): \n
            bitmap of any pieces
        square (int): \n
            position of rook

    Returns:
        bitmap : \n
            bitmap of possible rook attacks for square
    """

    # edge square could be same color
    attacks = rookAttacks[square]
    for direction in range(1, 8, 2):
        attacks ^= getRayProtected(occupied, direction, square)

    return attacks


def getQueenAttacks(occupied: int, square: int):
    """
    return bitmap of possible queen attacks for square

    caution: this function does not consider blocker's color\n
    therefore, blocker could be same color as attacker.
    
    Args:
        occupied (int): \n
            bitmap of any pieces
        square (int): \n
            position of queen

    Returns:
        bitmap : \n
            bitmap of possible queen attacks for square
    """

    # edge square could be same color
    attacks = queenAttacks[square]
    for direction in range(8):
        attacks ^= getRayProtected(occupied, direction, square)

    return attacks


def getKingAttacks(notSamecolored: int, square: int):
    """
    get bitmap of king attacks for square

    Args:
        notSamecolored (int) : \n
            bitmap of not same colored pieces, include empty squares
        square (int): \n
            position of king

    Returns:
        bitmap : \n
            bitmap of possible king attacks for square
    """

    return KingAttacks[square] & notSamecolored


def pinnedPieces(bitBoardSet: list, colorOfKing: int):
    """_summary_

    Args:
        bitBoardSet (list): _description_
        colorOfKing (int): _description_

    Returns:
        _type_: _description_
    """
    # colorOfKing : color of king for getting pinned pieces
    #
    # if color is same, absoluted pins
    # if color is different, discovered checkers

    #
    squareOfKing \
        = bitScanForward(bitBoardSet[nKing]
                         & bitBoardSet[colorOfKing - 1])

    oppColor = 2 - colorOfKing

    oppositeBQ \
        = (bitBoardSet[nBishop] | bitBoardSet[nQueen]) \
        & bitBoardSet[oppColor]
    oppositeRQ \
        = (bitBoardSet[nRook] | bitBoardSet[nQueen]) \
        & bitBoardSet[oppColor]

    nPieceBB = bitBoardSet[nPiece]

    result = 0x0000000000000000

    #
    for direction in range(0, 8, 2):
        result \
            |= getRayAttacks(nPieceBB,
                             direction,
                             squareOfKing) \
            & getRayAttacks(nPieceBB,
                            (direction + 4) & 0x7,
                            bitScan(rayAttacks[direction][squareOfKing] & oppositeBQ, direction >> 2))

    for direction in range(1, 8, 2):
        result \
            |= getRayAttacks(nPieceBB,
                             direction,
                             squareOfKing) \
            & getRayAttacks(nPieceBB,
                            (direction + 4) & 0x7,
                            bitScan(rayAttacks[direction][squareOfKing] & oppositeRQ, direction >> 2))

    return result


def getAttackers(bitBoardSet: list, square: int, attackerColor: int):
    # get all attackers
    # return bitboard of all attackers
    # attackerColor : 1 or 2
    if attackerColor >> 2:
        raise ValueError('attackerColor is out of range')

    attackerColor >>= 1

    result = (getPawnAttacks(bitBoardSet[nPiece], square, attackerColor)
              & bitBoardSet[nPawn])
    result |= (getKnightAttacks(bitBoardSet[nPiece], square)
               & bitBoardSet[nKnight])
    result |= (getBishopAttacks(bitBoardSet[nPiece], square)
               & bitBoardSet[nBishop])
    result |= (getRookAttacks(bitBoardSet[nPiece], square)
               & bitBoardSet[nRook])
    result |= (getQueenAttacks(bitBoardSet[nPiece], square)
               & bitBoardSet[nQueen])
    result |= (getKingAttacks(bitBoardSet[nPiece], square)
               & bitBoardSet[nKing])
    return result & bitBoardSet[attackerColor]


def possibleMove(bitBoardSet: list, board: list, currentPosition: int, nextPosition: int, moveColor: int):
    if currentPosition >> 6:
        raise ValueError("currentPos is out of range")
    if nextPosition >> 6:
        raise ValueError("nextPos is out of range")

    fromSquare = board[currentPosition]
    toSquare = board[nextPosition]

    pieceType = fromSquare % 0xfc
    colorType = fromSquare % 0x3
    oppColorType = 0x4 >> colorType

    if pieceType == empty:
        return 0x0

    if pieceType == (1 << nPawn):
        return getPawnAttacks(bitBoardSet[nPiece], fromSquare, colorType >> 1) \
            | getPawnForward(bitBoardSet[nEmpty], fromSquare, colorType >> 1)

    if pieceType == (1 << nKnight):
        return getKnightAttacks(bitBoardSet[nEmpty] | bitBoardSet[oppColorType], fromSquare)

    if pieceType == (1 << nBishop):
        return getBishopAttacks(bitBoardSet[oppColorType], fromSquare)

    if pieceType == (1 << nRook):
        return getRookAttacks(bitBoardSet[oppColorType], fromSquare)

    if pieceType == (1 << nQueen):
        return getQueenAttacks(bitBoardSet[oppColorType], fromSquare)

    if pieceType == (1 << nKing):
        safeSquare = kingMoveSqures[currentPosition]
        for possibleMove in kingMoveSqures[currentPosition]:
            if getAttackers(bitBoardSet, possibleMove, oppColorType):
                safeSquare ^= 1 << possibleMove

        return safeSquare \
            & getKingAttacks(bitBoardSet[nEmpty] | bitBoardSet[0x4 >> colorType], fromSquare)


def moveWithoutTest(bitBoardSet: list, currentPosition: int, nextPosition: int, colorType: int, pieceType: int, cpieceType: int = None):
    # https://www.chessprogramming.org/General_Setwise_Operations#Intersection
    # colorType : 1 or 2
    if colorType >> 1:
        raise ValueError('colorType is out of range')
    # pieceType : 2 ~ 7
    if (pieceType >> 1) == 0 or pieceType >> 3:
        raise ValueError('pieceType is out of range')
    # currentPosition, nextPosition : 0 ~ 63
    if currentPosition >> 6 or nextPosition >> 6:
        raise ValueError('some position is out of range')

    fromBB = 1 << currentPosition
    ToBB = 1 << nextPosition
    fromToBB = fromBB ^ ToBB

    bitBoardSet[pieceType] ^= fromToBB
    bitBoardSet[colorType] ^= fromToBB

    if cpieceType:
        bitBoardSet[1 - colorType] ^= ToBB
        bitBoardSet[cpieceType] ^= ToBB
        bitBoardSet[nEmpty] ^= fromBB
        bitBoardSet[nPiece] ^= fromBB
        return

    bitBoardSet[nEmpty] ^= fromToBB
    bitBoardSet[nPiece] ^= fromToBB
    return
