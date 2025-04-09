from const_variable import *
from chess_module import *
from chess_bitmap_module import (
    Board2BitBoardSet,
    bitScanForward,
    rayAttacks,
    getRayAttacks,
    bitScan,
    getPawnAttacks,
    getKnightAttacks,
    getBishopAttacks,
    getRookAttacks,
    getQueenAttacks,
    getKingAttacks,
    KingAttacks,
    kingMoveSquares,
    knightAttacks,
    getPawnForward,
    Bitmap2matrix
)


class Chess():
    def __init__(self):
        # placement of pieces
        self.board = defaultBoardPlacement.copy()
        self.bitBoardSet = bitBoardDefaultSet.copy()
        self.PositionsOfKings = [4, 60]  # bitBoard index

        # Side to move : 0 - not defined, 1 - white, 2 - black
        self.sideToMove = 0

        # for special moves

        # Castling ability
        # [ white king color castling( K, h1 )
        # , white queen color castling( Q, a1 )
        # , black king color castling( k, h8 )
        # , black right castling( q, a8 ) ]
        self.castlingFlags = [True, True, True, True]

        # en passant target square
        self.enPassantTarget = 0

        #

        # Halfmove clock
        self.halfMoveClock = 0

        # fullmove counter
        self.fullMoveCounter = 0

        # move list for undoing

        # [ fromSquare, toSquare, colorType, moveType, capturedPiece, previousCastlingFlags ]
        self.moveList = [Move() for _ in range(1 << 10)]
        self.moveListCurrent = 0

    # basic oparation of chess

    def reset(self) -> None:
        self.board = defaultBoardPlacement.copy()
        self.bitBoardSet = bitBoardDefaultSet.copy()
        self.PositionsOfKings = [4, 60]

        self.sideToMove = white

        self.castlingFlags = [True, True, True, True]
        self.enPassantTarget = 0

        self.halfMoveClock = 0
        self.fullMoveCounter = 1

        self.moveList = [Move() for _ in range(1 << 10)]
        self.moveListCurrent = 0

        return

    def _set(self, FEN: str) -> None:
        # variables
        FENList = FEN.split(" ")
        placement = FENList[0]
        sideToMove = FENList[1]
        castling = FENList[2]
        enPassant = FENList[3]

        if FEN != "" and len(FENList) > 4:
            halfMoveClock = FENList[4]
            fullMoveCounter = FENList[5]

        # process
        # print(FENList)
        self.board = FENboard2board(placement)
        self.bitBoardSet = Board2BitBoardSet(self.board)
        self.sideToMove = white if sideToMove[0].lower() == 'w' else black
        self.halfMoveClock = int(halfMoveClock) if len(FENList) > 4 else 0
        self.fullMoveCounter = int(fullMoveCounter) if len(FENList) > 4 else 0
        # castlingFlags
        for char in castling:
            if char == '-':
                self.castlingFlags = [False, False, False, False]
                break
            if char == 'K':
                self.castlingFlags[0] = True
            if char == 'Q':
                self.castlingFlags[1] = True
            if char == 'k':
                self.castlingFlags[2] = True
            if char == 'q':
                self.castlingFlags[3] = True

        # enPassantTarget
        for char in enPassant:
            if char == '-':
                self.enPassantTarget = 0
                break
            self.enPassantTarget = algebraic2index(enPassant)
        # PositionsOfKings
        for index, piece in enumerate(self.board):
            if piece & king:
                self.PositionsOfKings[(piece & 0b11) >> 1] = index ^ 0b111000

        # reset the move list
        self.moveList = [Move() for _ in range(1 << 10)]
        self.moveListCurrent = 0

        return

    def nextRound(self) -> None:
        self.sideToMove = (self.sideToMove & 0b1) + 1
        self.fullMoveCounter += 1

        return

    def undoRound(self) -> None:
        self.sideToMove = (self.sideToMove & 0b1) + 1
        self.fullMoveCounter += 1

        return

    # return bitmap index

    def _getKingSquare(self, colorOfKing: int) -> int:
        """
        return square of king for colorOfKing.

        Args:
            colorOfKing (int): \n
                color of king for getting square. 1, 2
            
        Raises:
            ValueError: \n
                colorOfKing is out of range
            ValueError: \n
                there is no king
                
        Returns:
            squareIndex: \n
                square of king for colorOfKing
        """

        # raises
        if (colorOfKing - 1) >> 1:
            raise ValueError("colorOfKing is out of range")
        if (self.bitBoardSet[nKing] & self.bitBoardSet[colorOfKing >> 1]) == 0:
            raise ValueError("there is no king")

        return bitScanForward(self.bitBoardSet[nKing] & self.bitBoardSet[colorOfKing >> 1])

    # return bitmap

    def _pinnedPieces(self, colorOfKing: int) -> int:
        """
        return bitmap of pinned pieces.
        if color is same, absoluted pins.
        if color is different, discovered checkers.
        
        Args:
            colorOfKing (int): \n
                color of king for getting pinned pieces. 0, 1

        Returns:
            bitmap: \n
                bitmap of pinned pieces
        """

        # Raise
        if colorOfKing >> 1:
            raise ValueError("colorOfKing is out of range")

        # variables
        squareOfKing = self.PositionsOfKings[colorOfKing]

        oppColor = colorOfKing ^ 0b1

        nPieceBB = self.bitBoardSet[nPiece]
        result = 0x0000000000000000

        oppositeBQ \
            = (self.bitBoardSet[nBishop] | self.bitBoardSet[nQueen]) \
            & self.bitBoardSet[oppColor]
        oppositeRQ \
            = (self.bitBoardSet[nRook] | self.bitBoardSet[nQueen]) \
            & self.bitBoardSet[oppColor]

        # check for bishop and queen
        for direction in range(0, 8, 2):
            # variable
            oppositeBQAttackers = rayAttacks[direction][squareOfKing] & oppositeBQ

            # printBitMap(rayAttacks[direction][squareOfKing])
            # printBitMap(oppositeBQ)

            # process
            if oppositeBQAttackers == 0:
                continue

            # print(f'oppositeBQAttackers')
            # printBitMap(oppositeBQAttackers)

            result \
                |= (getRayAttacks(nPieceBB,
                                  direction,
                                  squareOfKing)
                    & getRayAttacks(nPieceBB,
                                    (direction ^ 0b100),
                    bitScan(oppositeBQAttackers, direction >> 2)))

        # check for rook and queen
        for direction in range(1, 8, 2):
            # variable
            oppositeRQAttackers = rayAttacks[direction][squareOfKing] & oppositeRQ

            # process
            if oppositeRQAttackers == 0:
                continue

            result \
                |= (getRayAttacks(nPieceBB,
                                  direction,
                                  squareOfKing)
                    & getRayAttacks(nPieceBB,
                                    (direction + 4) & 0x7,
                    bitScan(oppositeRQAttackers, direction >> 2)))

        return result

    def _getAttackers(self, square: int, attackerColor: int, moveFromBB: int = 0, moveToBB: int = 0) -> int:
        """
        get all attackers that are able to attack the square.

        Args:
            square (int): \n
                position of square that is being attacked.
            attackerColor (int): \n
                color of attackers. 0 - nWhite, 1 - nBlack. same as isBlack
            moveFromBB (int): \n
                bitmap of moving piece. default is 0.
            moveToBB (int): \n
                bitmap of moving piece. default is 0.
            
        Raises:
            ValueError: \n
                attackerColor is out of range

        Returns:
            bitmap: \n
                bitmap of all attackers
        """

        # Raise
        if attackerColor >> 1:
            raise ValueError('attackerColor is out of range')

        nPieceBB = self.bitBoardSet[nPiece]
        nPieceBB |= moveToBB
        nPieceBB ^= moveFromBB

        # process
        result = (getPawnAttacks(nPieceBB, square, attackerColor ^ 0b1)
                  & self.bitBoardSet[nPawn])
        result |= (getKnightAttacks(nPieceBB, square)
                   & self.bitBoardSet[nKnight])
        result |= (getBishopAttacks(nPieceBB, square)
                   & self.bitBoardSet[nBishop])
        result |= (getRookAttacks(nPieceBB, square)
                   & self.bitBoardSet[nRook])
        result |= (getQueenAttacks(nPieceBB, square)
                   & self.bitBoardSet[nQueen])
        result |= (getKingAttacks(nPieceBB, square)
                   & self.bitBoardSet[nKing])

        result &= self.bitBoardSet[attackerColor]
        result &= (0xffffffffffffffff ^ moveToBB)

        return result

    def _getSafeMoveOfKing(self, colorOfKing: int) -> int:
        """
        get bitmap of safe movement for king.
        
        Args:
            colorOfKing (int): \n
                color of king for getting safe movement. 0, 1

        Returns:
            bitmap: \n
                bitmap of safe movement for king.
        """

        # variables
        squareOfKing = self.PositionsOfKings[colorOfKing]
        result = KingAttacks[squareOfKing]

        # process
        for possibleSquare in kingMoveSquares[squareOfKing]:
            # oppColorType : nWhite, nBlack -> white, black
            if self._getAttackers(possibleSquare, colorOfKing ^ 0b1, (1 << squareOfKing), (1 << possibleSquare)):
                result ^= (1 << possibleSquare)

        return result & (self.bitBoardSet[nEmpty] | self.bitBoardSet[colorOfKing ^ 0b1])

    def _possibleMove(self, currentPosition: int, sideToMove: int = 0) -> int:
        """
        get bitmap of possible movement for piece on currentPosition.

        Args:
            currentPosition (int): \n
                position of piece that is being moved.
            sideToMove (int): \n
                side to move. default is 0. 0 - none, 1 - white, 2 - black

        Raises:
            ValueError: \n
                currentPosition is out of range.

        Returns:
            bitmap: \n
                bitmap of possible movement for piece on currentPosition.
        """

        # raise for out of range
        if currentPosition >> 6:
            raise ValueError("currentPos is out of range")

        curPosBB = 1 << currentPosition

        # exception handling
        if self.bitBoardSet[nEmpty] & curPosBB:
            return 0x0  # moving piece is nonexistent
        if sideToMove and (self.bitBoardSet[sideToMove & 1] & curPosBB):
            return 0x0  # moving piece is not same color with sideToMove

        # variables
        fromSquare = self.board[currentPosition ^ 0b111000]

        pieceType = fromSquare & 0b11111100
        colorType = fromSquare & 0b00000011
        colorType >>= 1                 # white, black -> nWhite, nBlack
        oppColorType = colorType ^ 0b1

        kingPosition = self.PositionsOfKings[colorType]

        # mask
        possibleSquares = (self.bitBoardSet[nEmpty]
                           | self.bitBoardSet[oppColorType])

        # raise for valid values
        if sideToMove and colorType == (sideToMove & 1):
            raise ValueError(f'sideToMove and colorType are not matched - sideToMove : {sideToMove}, colorType : {
                             colorType}, fromSquare : {fromSquare}, currentPosition : {currentPosition}')
        if pieceType == empty:
            raise ValueError("board and bitbaord are not matched")

        # process

        # first, check if king is in check
        CheckersBB = self._getAttackers(kingPosition, oppColorType)

        if CheckersBB:
            # safe move for king
            if pieceType & king:
                return self._getSafeMoveOfKing(colorType)

            # is double check?
            if CheckersBB & (CheckersBB - 1):
                return 0x0

            # single check : 1. king safe move 2. capture or block
            for direction in range(8):
                if CheckersBB & rayAttacks[direction][kingPosition]:
                    possibleSquares &= getRayAttacks(
                        CheckersBB, direction, kingPosition)
                    CheckersBB = 0
                    break
            # if direction is nonexistent, then it is knight check
            if CheckersBB:
                possibleSquares = CheckersBB & knightAttacks[kingPosition]

            if possibleSquares == 0:
                raise Exception("CheckersBB is error")

        # check absolute pin case
        if (self._pinnedPieces(colorType) & curPosBB):
            # printBitMap(self._pinnedPieces(colorType))
            direction = 0

            # get direction
            if kingPosition > currentPosition:
                direction = 4
                distance = kingPosition - currentPosition
            else:
                distance = currentPosition - kingPosition

            if (distance & 0b000111) == 0:
                direction += 1
            elif (kingPosition & 0b111000) == (currentPosition & 0b111000):
                direction += 3
            elif ((distance >> 3) & 0b000111) == (distance & 0b000111):
                direction += 2

            # possible move for absolute pin
            # print(f'currentPosition : {currentPosition}, direction : {direction}, kingPosition : {kingPosition}')
            # printBitMap(possibleSquares)
            possibleSquares \
                &= (getRayAttacks(self.bitBoardSet[nPiece] ^ curPosBB,
                                  direction,
                                  kingPosition)
                    ^ curPosBB)
            # printBitMap(possibleSquares)

        # each case by pieceType
        if pieceType & pawn:
            pawnPossible = getPawnAttacks(self.bitBoardSet[nPiece], currentPosition, colorType)\
                | getPawnForward(self.bitBoardSet[nEmpty], currentPosition, colorType)
            enPassantTarget = self.enPassantTarget
            ePCurPos = enPassantTarget - 9 + (colorType << 4)
            ePBB = 1 << enPassantTarget

            if enPassantTarget and (enPassantTarget & 0b000111) and (currentPosition == ePCurPos):
                pawnPossible |= ePBB
            if enPassantTarget and ((enPassantTarget + 1) & 0b000111) and (currentPosition == ePCurPos + 2):
                pawnPossible |= ePBB
            # checked by en passant movement. it should be illegal
            if (ePBB & pawnPossible) and self._getAttackers(kingPosition, oppColorType, ((1 << currentPosition) | (2 << ePCurPos)), ePBB):
                pawnPossible ^= ePBB
            return possibleSquares & pawnPossible

        if pieceType & knight:
            return possibleSquares & getKnightAttacks(self.bitBoardSet[nEmpty] | self.bitBoardSet[oppColorType], currentPosition)
        if pieceType & bishop:
            return possibleSquares & getBishopAttacks(self.bitBoardSet[nPiece], currentPosition)
        if pieceType & rook:
            return possibleSquares & getRookAttacks(self.bitBoardSet[nPiece], currentPosition)
        if pieceType & queen:
            return possibleSquares & getQueenAttacks(self.bitBoardSet[nPiece], currentPosition)
        if pieceType & king:
            return self._getSafeMoveOfKing(colorType)

        # exception handling
        raise ValueError("pieceType is not defined")

    def _possiblePromotion(self, sideToMove: int) -> list[int]:
        """
        get bitmap of possible promotion for sideToMove.

        Args:
            sideToMove (int): \n
                side to move. 1 - white, 2 - black
        
        Returns:
            possiblePromotionFile (list[8bit]): \n
                list of possible promotion file. \n
                [0] - left forward mov,  \n
                [1] - forward mov,  \n
                [2] - right forward mov \n
        """
        if sideToMove and (sideToMove - 1) >> 1 == 0:
            pass
        else:
            raise ValueError("sideToMove is not valid")

        colorPawnBB = self.bitBoardSet[nPawn] & self.bitBoardSet[sideToMove - 1]
        result = [0 for _ in range(3)]
        possiblePromotionFiles = [0 for _ in range(3)]
        curPos = 87 - (sideToMove * 40)
        mask = 1 << curPos

        for _ in range(8):
            curPos += 1
            mask <<= 1

            if colorPawnBB & mask:
                possibleMoveBB = self._possibleMove(curPos, sideToMove)

                nextPosMask = mask >> 7
                if sideToMove == white:
                    nextPosMask <<= 16

                for index in range(2, -1, -1):
                    if nextPosMask & possibleMoveBB:
                        possiblePromotionFiles[index] |= (
                            1 << (curPos & 0b111))
                        result[index] |= (1 << ((curPos & 0b111) << 2))
                    nextPosMask >>= 1
            else:
                continue

        for index in range(3):
            result[index]*0b1111
            if sideToMove == black:
                result[index] <<= 32

        return result, possiblePromotionFiles

    # ================================ possibleBit ================================ #

    def getPossibleMoveBBs(self, sideToMove: int) -> list[list[int]]:
        """
        Get possible move bitboards for sideToMove.
        
        Args:
            sideToMove (int, optional): 1 is white, 2 is black. Defaults to 0.

        Returns:
            list[list[int]]: possible move bitboards for sideToMove.
        """
        possibleMoveBBs = emptyPossibleMovBBs.copy()

        possiblePromotionBBs, possiblePromotionFiles = self._possiblePromotion(
            sideToMove)

        for currentPos in range(64):
            possibleMoveBBs[currentPos] = Bitmap2matrix(
                self._possibleMove(currentPos, sideToMove))

        for index in range(3):
            for file in range(8):
                # remove non-promotion moves
                if possiblePromotionFiles[index] & (1 << file):
                    curPos = 88 - sideToMove*40 + file
                    nextPos = curPos + 23 - sideToMove*16 + index
                    possibleMoveBBs[curPos][nextPos] = 0

            # append the promotion moves
            possibleMoveBBs[64 +
                            index] = Bitmap2matrix(possiblePromotionBBs[index])

        return possibleMoveBBs
