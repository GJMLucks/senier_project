from const_variable import *

# bit rotate operation


def rotateLeft64int(bitmap: int, offset: int):
    # precondition: offset is in range -64..64
    return ((bitmap << offset) | (bitmap >> (64 - offset))) if (offset > 0) \
        else ((bitmap >> -offset) | (bitmap << (64 + offset)))


# ray-movement


def occludedFill(pieces: int, possibleSqures: int, dir8: int = -1) -> int:
    if dir8 == -1:
        raise ValueError('dir8 should be assigned')

    offset = move_shift[dir8]
    possibleSqures &= avoidWrap[dir8]

    pieces |= possibleSqures & rotateLeft64int(pieces, offset)
    possibleSqures &= rotateLeft64int(possibleSqures, offset)
    pieces |= possibleSqures & rotateLeft64int(pieces, offset << 1)
    possibleSqures &= rotateLeft64int(possibleSqures, offset << 1)
    pieces |= possibleSqures & rotateLeft64int(pieces, offset << 2)

    return pieces


# one step functions
notAFile = 0xfefefefefefefefe
notHFile = 0x7f7f7f7f7f7f7f7f


def noWeOneStep(bitBoard: int):
    return (bitBoard << 7) & notHFile


def nortOnestep(bitBoard: int):
    return bitBoard << 8


def noEaOnestep(bitBoard: int):
    return (bitBoard << 9) & notAFile


def EastOnestep(bitBoard: int):
    return (bitBoard << 1) & notAFile


def soEaOnestep(bitBoard: int):
    return (bitBoard >> 7) & notAFile


def soutOnestep(bitBoard: int):
    return bitBoard >> 8


def soWeOnestep(bitBoard: int):
    return (bitBoard >> 9) & notHFile


def westOnestep(bitBoard: int):
    return (bitBoard >> 1) & notHFile

# precalculated attacks


rayAttacks = [[0x0000000000000000 for i in range(64)] for j in range(8)]

boundary = 0xffffffffffffffff

basenort = 0x0101010101010100
basesout = 0x0080808080808080

for position in range(64):
    rayAttacks[Nort][position] = basenort
    basenort = (basenort << 1) & boundary

    rayAttacks[Sout][63 - position] = basesout
    basesout >>= 1

basenowe = 0x0102040810204000
basenoea = 0x8040201008040200
baseeast = 0x00000000000000fe
basesoea = 0x0020408010204080
basesowe = 0x0040201008040201
basewest = 0xef00000000000000

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

rankAttacks = [rayAttacks[Nort][position] |
               rayAttacks[Sout][position] for position in range(64)]
fileAttacks = [rayAttacks[East][position] |
               rayAttacks[West][position] for position in range(64)]
diagAttacks = [rayAttacks[NoEa][position] |
               rayAttacks[SoWe][position] for position in range(64)]
antidiagAttacks = [rayAttacks[NoWe][position] |
                   rayAttacks[SoEa][position] for position in range(64)]

rookAttacks = [rankAttacks[position] | fileAttacks[position]
               for position in range(64)]
bishopAttacks = [diagAttacks[position] | antidiagAttacks[position]
                 for position in range(64)]
queenAttacks = [rookAttacks[position] | bishopAttacks[position]
                for position in range(64)]

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


def popCount(bitBoard: int):
    # count each 2bit
    bitBoard -= (bitBoard >> 1) & 0x5555555555555555

    # count each 4bit
    bitBoard = (bitBoard & 0x3333333333333333) + \
        ((bitBoard >> 2) & 0x3333333333333333)

    # count each 8bit
    bitBoard = (bitBoard + (bitBoard >> 4)) & 0x0f0f0f0f0f0f0f0f
    return (bitBoard * 0x0101010101010101) >> 56


# bitScan function

# bitScanForward LSB


def bitScanForward(bitBoard: int):
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


# bitScanReverse
# @authors Kim Walisch, Mark Dickinson
# @precondition bb != 0
# @return index (0..63) of most significant one bit

def bitScanReverse(bitBoard: int):
    bitBoard |= bitBoard >> 1
    bitBoard |= bitBoard >> 2
    bitBoard |= bitBoard >> 4
    bitBoard |= bitBoard >> 8
    bitBoard |= bitBoard >> 16
    bitBoard |= bitBoard >> 32
    return index64[(bitBoard * 0x03f79d71b4cb0a89) >> 58]

# generalized bitScan
# @author Gerd Isenberg
# @param bb bitboard to scan
# @precondition bb != 0
# @param reverse, true bitScanReverse, false bitScanForward
# @return index (0..63) of least/most significant one bit


def bitScan(bitBoard: int, reverse: bool):
    return bitScanReverse(bitBoard) if reverse else bitScanReverse(bitBoard & -bitBoard)


dirMask = [0x0000000000000000, 0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
           0xffffffffffffffff, 0xffffffffffffffff, 0xffffffffffffffff, 0xffffffffffffffff]
dirBit = [0x8000000000000000, 0x8000000000000000, 0x8000000000000000, 0x8000000000000000,
          0x0000000000000001, 0x0000000000000001, 0x0000000000000001, 0x0000000000000001]

# ray-movement module


def getRayBlocks(occupied: int, direction: int, square: int):
    attacks = rayAttacks[direction][square]
    blocker = attacks & occupied
    blocker &= -blocker | dirMask[direction]
    square = bitScanReverse(blocker | dirBit[direction])
    return rayAttacks[direction][square]


def getRayAttacks(occupied: int, direction: int, square: int):
    return rayAttacks[direction][square] ^ getRayBlocks(occupied, direction, square)


# piece movement module


def getPawnForward(emptied: int, square: int, isBlack: int):
    # one Forward
    oneforward = emptied & (0x800000000000000000 >>
                            (63 - square + isBlack << 4))
    # two Forward
    twoforward = emptied & (
        ((0x00FF00000000FF00 & (1 << square)) << 16) >> (isBlack << 5))
    return oneforward | (twoforward & (oneforward << 8) >> (isBlack << 5))


def getPawnAttacks(occupied: int, square: int, isBlack: int):
    forwardMask \
        = 0x01400140000000000000 >> (63 - square) \
        & 0xFF0000000000000000 >> ((63 - square) & 0x38 + isBlack << 4)
    return occupied & forwardMask


def getKnightAttacks(notSamecolored: int, square: int):
    return knightAttacks[square] & notSamecolored


def getKnightsAttacks(knights: int) -> int:
    l1 = (knights >> 1) & 0x7f7f7f7f7f7f7f7f
    l2 = (knights >> 2) & 0x3f3f3f3f3f3f3f3f
    r1 = (knights << 1) & 0xfefefefefefefefe
    r2 = (knights << 2) & 0xfcfcfcfcfcfcfcfc
    h1 = l2 | r2
    h2 = l1 | r1
    return (h1 << 8) | (h1 >> 8) | (h2 << 16) | (h2 >> 16)


def getBishopAttacks(occupied: int, square: int):
    # edge square could be same color
    attacks = bishopAttacks[square]
    for direction in range(0, 8, 2):
        attacks ^= getRayBlocks(occupied, direction, square)
    return attacks


def getRookAttacks(occupied: int, square: int):
    # edge square could be same color
    attacks = rookAttacks[square]
    for direction in range(1, 8, 2):
        attacks ^= getRayBlocks(occupied, direction, square)
    return attacks


def getQueenAttacks(occupied: int, square: int):
    # edge square could be same color
    attacks = queenAttacks[square]
    for direction in range(8):
        attacks ^= getRayBlocks(occupied, direction, square)
    return attacks


def getKingAttacks(notSamecolored: int, square: int):
    return KingAttacks[square] & notSamecolored


def pinnedPieces(bitBoardSet: list, occupied: int, squareOfKing: int, isBlack: int):
    # if color is same, absoluted pins
    # if color is different, discovered checkers

    nPieceBB = bitBoardSet[nPiece]

    oppositeBQ \
        = (bitBoardSet[nBishop] | bitBoardSet[nQueen]) \
        & bitBoardSet[nBlack - isBlack]
    oppositeRQ \
        = (bitBoardSet[nRook] | bitBoardSet[nQueen]) \
        & bitBoardSet[nBlack - isBlack]

    result = 0x0000000000000000

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
