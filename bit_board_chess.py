from const_variable import *

from printing_chessboard import *

from chess_module import *
from chess_bitmap_module import *

from multipledispatch import dispatch

# ======== class ======== #
class Chess():
    def __init__(self):
        # placement of pieces
        self.board = defaultBoardPlacement.copy()
        self.bitBoardSet = bitBoardDefaultSet.copy()
        self.PositionsOfKings = [4, 60] # bitBoard index

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
        
        if len(FENList) > 4:
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

            #printBitMap(rayAttacks[direction][squareOfKing])
            #printBitMap(oppositeBQ)

            # process
            if oppositeBQAttackers == 0:
                continue
            
            #print(f'oppositeBQAttackers')
            #printBitMap(oppositeBQAttackers)

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
        result = (getPawnAttacks(nPieceBB, square, attackerColor^0b1)
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
            if self._getAttackers(possibleSquare, colorOfKing^0b1, (1 << squareOfKing), (1 << possibleSquare)):    # oppColorType : nWhite, nBlack -> white, black
                result ^= (1 << possibleSquare)
        
        return result & (self.bitBoardSet[nEmpty] | self.bitBoardSet[colorOfKing^0b1])

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
            raise ValueError(f'sideToMove and colorType are not matched - sideToMove : {sideToMove}, colorType : {colorType}, fromSquare : {fromSquare}, currentPosition : {currentPosition}')
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
                    possibleSquares &= getRayAttacks(CheckersBB, direction, kingPosition)
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
                                kingPosition) \
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

    # update chess state
    

    # movement functions

    def _moveWithoutTest(self, currentPosition: int, nextPosition: int, colorType: int, pieceType: int, cpieceType: int) -> None:
        """
        update the board placement data by piece movement.
        there is no handling. all parameters should be BBIndex.

        Args:
            currentPosition (int): \n
                square of piece that is being moved.
            nextPosition (int): \n
                square of piece that is being moved to.
            colorType (int): \n
                color of piece that is being moved. 0, 1
            pieceType (int): \n
                type of piece that is being moved. 2 ~ 7
            cpieceType (int): \n
                type of piece that is being captured. 2 ~ 7. if movement is not capturing, 0.
        """

        # process
        fromBB = 1 << currentPosition
        ToBB = 1 << nextPosition
        fromToBB = fromBB ^ ToBB

        self.bitBoardSet[pieceType] ^= fromToBB
        self.bitBoardSet[colorType] ^= fromToBB

        # capture case
        if cpieceType:
            self.bitBoardSet[1 - colorType] ^= ToBB
            self.bitBoardSet[cpieceType] ^= ToBB
            self.bitBoardSet[nEmpty] ^= ToBB
            self.bitBoardSet[nPiece] ^= ToBB

        self.bitBoardSet[nEmpty] ^= fromToBB
        self.bitBoardSet[nPiece] ^= fromToBB

        self.board = Bitmaps2Board(self.bitBoardSet)

        return

    def _changePiece(self, Square: int, piece: int) -> None:
        '''
        change piece on the square.
        it doesn't care about the square is empty or not.
        piece also could be empty.
        if there is piece on the square, color is not changed.
        
        Args:
            Square (int): \n
                square of piece that is being change.
            piece (int): \n
                piece that is being change.
                
        Raises:
            ValueError: \n
                pieceType is not defined
            ValueError: \n
                colorType is not defined    
        '''
        
        # variables and raises
        squarePiece = self.board[Square ^ 0b111000]
        
        toPieceType = piece & 0b11111100
        fromPieceType = squarePiece & 0b11111100
        if piece and toPieceType not in pieceTypes:
            raise ValueError("pieceType is not defined")
        if squarePiece and fromPieceType not in pieceTypes:
            raise ValueError("pieceType is not defined")
        
        colorType = piece & 0b11
        if colorType == 3:
            raise ValueError("colorType is not defined")
        
        squareBitmap = (1 << Square) & self.bitBoardSet[nPiece] # if piece in this square, then it is set. Otherwise 0
        maskBitmap = colorType << Square                        # if piece is empty, then it is 0. Otherwise set
        
        colorType >>= 1
        maskBitmap >>= colorType
        
        colorType |= (squarePiece & 0b11) >> 1
        if colorType == 3:
            raise ValueError("colorType is not defined")
        
        # process
        
        # bitmaps
        
        # if piece is set or removed, then process
        self.bitBoardSet[nEmpty] ^= (squareBitmap ^ maskBitmap)
        self.bitBoardSet[nPiece] ^= (squareBitmap ^ maskBitmap)
        # if piece is not empty, then process
        self.bitBoardSet[pieceTypesToBBIndex[fromPieceType >> 2]] ^= squareBitmap
        self.bitBoardSet[pieceTypesToBBIndex[toPieceType >> 2]] |= maskBitmap
        
        self.bitBoardSet[colorType] ^= (squareBitmap ^ maskBitmap)
        
        # board
        self.board[Square ^ 0b111000] = piece
        
        # print(f'After set piece : \n')
        # printchess(self.board)

        return

    def _setPiece(self, Square: int, piece: int) -> None:
        '''
        set piece on the square. it doesn't care about the square is empty or not.
        
        Args:
            Square (int): \n
                square of piece that is being set.
            piece (int): \n
                piece that is being set.
                
        Raises:
            ValueError: \n
                pieceType is not defined
            ValueError: \n
                colorType is not defined    
        '''        
        # variables
        pieceType = piece & 0b11111100
        colorType = (piece & 0b11) - 1
        squareBitmap = (1 << Square) & self.bitBoardSet[nEmpty] # if empty in this square, then it is set. Otherwise 0
        
        # raise
        if pieceType not in pieceTypes:
            raise ValueError("pieceType is not defined")
        if colorType >> 1:
            raise ValueError("colorType is not defined")

        # process
        
        # bitmaps
        # off nEmpty, on nPiece
        self.bitBoardSet[nEmpty] ^= squareBitmap
        self.bitBoardSet[nPiece] ^= squareBitmap
        #
        self.bitBoardSet[pieceTypesToBBIndex[pieceType >> 2]] |= squareBitmap
        self.bitBoardSet[colorType] |= squareBitmap
        
        # board
        self.board[Square ^ 0b111000] = piece
        
        # print(f'After set piece : \n')
        # printchess(self.board)

        return

    def _Promotion(self, square: int, pieceType: int) -> None:
        """
        update the board placement data by piece promotion.

        Args:
            square (int): \n
                square of piece that is being promoted.
            pieceType (int): \n
                pieceType that is being promoted to.

        Raises:
            ValueError: \n
                if promotionPieceType is not defined.
            ValueError: \n
                if promotion target is not pawn.
        """

        # raise
        if pieceType not in pieceTypes:
            raise ValueError("promotionPieceType is not defined : {pieceType}")
        if self.board[square ^ 0b111000] & pawn == 0:
            raise ValueError(f'promotion target is not pawn : {self.board[square ^ 0b111000]}')

        # board update
        self.board[square ^ 0b111000] += (pieceType - pawn)

        # bitboard update
        self.bitBoardSet[nPawn] ^= (1 << square)
        self.bitBoardSet[pieceTypesToBBIndex[pieceType >> 2]] ^= (1 << square)

        return

    def _UnPromotion(self, square: int, colorType: int) -> None:
        """
        unpromotion piece for unmake.

        Args:
            square (int): \n
                square of piece that is being unpromoted.
            colorType (int): \n
                color of piece that is being unpromoted to.
        
        Raises:
            ValueError: \n
                if square is not in promotion area.
            ValueError: \n
                if unpromotion target is not pawn.
        """

        # raise
        if (square & 0b111000) ^ (0b111000 >> (colorType << 3)):
            raise ValueError("square is not in promotion area")
        if self.board[square ^ 0b111000] & pawn:
            raise ValueError(f'unpromotion target is pawn')

        promotionPieceType = (self.board[square ^ 0b111000] & 0b11111100)

        # board update
        self.board[square ^ 0b111000] = ((self.board[square ^ 0b111000] & 0b11) | pawn)

        # bitboard update
        self.bitBoardSet[nPawn] ^= (1 << square)
        self.bitBoardSet[pieceTypesToBBIndex[promotionPieceType >> 2]] ^= (1 << square)

        return

    def _IsCastling(self, castlingIndex: int) -> bool:
        """
        check if castling conditions is possible.
        this function also checking if castlingFlag is set

        Args:
            castlingIndex (int): \n
                index of castling. 0 - white king side, 1 - white queen side, 2 - black king side, 3 - black queen side

        Returns:
            bool: \n
                if castling is possible, return True. otherwise, return False.
        """

        # print(f'castlingIndex : {castlingIndex}')
        if (castlingIndex >> 1) == (2 >> self.sideToMove):
            return False
        if self.castlingFlags[castlingIndex] == False:
            return False
        

        # variables
        # types
        colorType = castlingIndex >> 1  # 0 - white, 1 - black
        isKingSide = (castlingIndex + 1) & 0b1
        # squares
        kingSquare = 4 + 56*colorType
        
        # process
        # is there a any piece in the castling way?
        
        # print(f'castlingIndex : {castlingIndex}')
        if (self.bitBoardSet[nPiece] & castlingWayMasks[castlingIndex]):
            return False
        # current king, castling king and route is not checked?
        
        # print(f'castlingIndex : {castlingIndex}')
        if self._getAttackers(kingSquare, colorType^0b1):
            return False
        
        # print(f'castlingIndex : {castlingIndex}')
        if self._getAttackers(2 + (isKingSide << 2) + 56*colorType, colorType^0b1):
            return False
        
        # print(f'castlingIndex : {castlingIndex}')
        if self._getAttackers(3 + (isKingSide << 1) + 56*colorType, colorType^0b1):
            return False
        
        # print(f'castlingIndex : {castlingIndex}')

        return True
    
    def _castling(self, castlingIndex: int) -> bool:
        """
        castling only it is possible.
        this function also checking if castlingFlag is set
        this function anly updates kingsPos and castlingFlags

        Args:
            castlingIndex (int): \n
                index of castling. 0 - white king side, 1 - white queen side, 2 - black king side, 3 - black queen side

        Returns:
            bool: \n
                if castling is possible, return True. otherwise, return False.
        """

        if self._IsCastling(castlingIndex) == False:
            return False

        # variables
        # types
        colorType = castlingIndex >> 1  # 0 - white, 1 - black
        isKingSide = (castlingIndex + 1) & 0b1
        # squares
        kingSquare = 4 + 56*colorType
        kingToSquare = (kingSquare - 2) + (isKingSide << 2)
        rookSquare = 7*(isKingSide) + 56*colorType

        # move
        self._moveWithoutTest(
            kingSquare, kingToSquare, colorType, nKing, 0)
        self._moveWithoutTest(
            rookSquare, 3 + (isKingSide << 1) + 56*colorType, colorType, nRook, 0)

        # update
        # king square
        self.PositionsOfKings[colorType] = kingToSquare
        # castling flags
        self.castlingFlags[colorType << 1] = False
        self.castlingFlags[(colorType << 1) + 1] = False

        return True

    @dispatch(str)
    def makeMove(self, pureCoordinate: str) -> bool:
        # variables
        moveArgs = pureCoordinate2args(pureCoordinate)
        # positions
        currentPosition = moveArgs[0]
        nextPosition = moveArgs[1]
        # types
        promoPieceType = moveArgs[2]
        colorType = (self.board[currentPosition ^ 0b111000] & 0b00000011) >> 1
        pieceType = pieceTypesToBBIndex[(
            self.board[currentPosition ^ 0b111000] & 0b11111100) >> 2]
        moveType = 1    # for moveList parameter

        cpiece = self.board[nextPosition ^ 0b111000]

        toBB = 1 << nextPosition

        enPassantTarget = self.enPassantTarget

        result = False

        # raise
        if self.bitBoardSet[colorType] & toBB:
            raise ValueError(
                "move to square of same color piece is not allowed")

        # castling
        if pieceType == nKing:
            if pureCoordinate == "e1g1":
                result = self._castling(0)
            if pureCoordinate == "e1c1":
                result = self._castling(1)
            if pureCoordinate == "e8g8":
                result = self._castling(2)
            if pureCoordinate == "e8c8":
                result = self._castling(3)
            
            if result:
                moveType = 4

        # filter Illegal move, it is not check castling
        if (result == False) and (self._possibleMove(currentPosition) & toBB) == 0:
            return False

        # normal move
        if result == False:
            self._moveWithoutTest(currentPosition, nextPosition,
                              colorType, pieceType, pieceTypesToBBIndex[(cpiece & 0b11111100) >> 2])
            moveType = 1
        
        # en passant capture
        # if enPassantTarget:
            # print(f'enPassantTarget : {enPassantTarget}, nextPosition : {nextPosition}, pieceType : {pieceType}')
        if enPassantTarget and nextPosition == enPassantTarget and pieceType == nPawn:
            # print(enPassantTarget - 8 + (colorType << 4))
            self._changePiece(enPassantTarget - 8 + (colorType << 4), empty)    # remove capture piece
        
        # promotion
        if promoPieceType:
            self._changePiece(nextPosition, (promoPieceType | colorType + 1))
            moveType = 2


        # [ update process ]

        # update king square
        if pieceType == nKing:
            self.PositionsOfKings[colorType] = nextPosition
        
        # update castling flags: if king moves, remove castling flags
        if pieceType == nKing:
            self.castlingFlags[colorType << 1] = False
            self.castlingFlags[(colorType << 1) + 1] = False
        # if rook moves, remove castling flags
        if (pieceType == nRook) and (0x8100000000000081 & (1 << currentPosition)):
            if currentPosition == 7:
                self.castlingFlags[0] = False
            if currentPosition == 0:
                self.castlingFlags[1] = False
            if currentPosition == 63:
                self.castlingFlags[2] = False
            if currentPosition == 56:
                self.castlingFlags[3] = False
        # if capture is rook, then remove castling flags
        if (cpiece & rook) and (0x8100000000000081 & toBB):
            if nextPosition == 7:
                self.castlingFlags[0] = False
            if nextPosition == 0:
                self.castlingFlags[1] = False
            if nextPosition == 63:
                self.castlingFlags[2] = False
            if nextPosition == 56:
                self.castlingFlags[3] = False

        # set en passant target
        self.enPassantTarget = 0
        
        if (pieceType == nPawn) and (currentPosition + 16 == nextPosition + colorType*32):
            self.enPassantTarget = (currentPosition + nextPosition) >> 1
        #     print(f'enPassantTarget : {self.enPassantTarget}')

        # move list
        self.moveList[self.moveListCurrent] = Move(
            currentPosition, nextPosition, colorType, moveType, cpiece, promoPieceType, tuple(self.castlingFlags.copy()))
        self.moveListCurrent += 1
        
        print(f'After make : {pureCoordinate}')
        print(f'castlingFlags: {self.castlingFlags.copy()}')
        printBitMaps(self.bitBoardSet)
        printchess(self.board)
        
        # chess state
        self.nextRound()

        return True

    @dispatch(Move)
    def makeMove(self, move: Move):
        # variables

        # positions
        currentPosition = move.fromSquare
        nextPosition = move.toSquare
        # types
        promoPieceType = move.promotionPiece
        colorType = move.colorType
        pieceType = pieceTypesToBBIndex[(
            self.board[currentPosition ^ 0b111000] & 0b11111100) >> 2]
        moveType = move.moveType    # for moveList parameter

        cpiece = move.capturedPiece

        enPassantTarget = move.previousEpTarget

        # castling
        if (moveType & 0b100):
            if nextPosition == 6:
                self._castling(0)
            if nextPosition == 2:
                self._castling(1)
            if nextPosition == 62:
                self._castling(2)
            if nextPosition == 58:
                self._castling(3)

        # normal move
        if (moveType & 0b11):
            self._moveWithoutTest(currentPosition, nextPosition,
                              colorType, pieceType, pieceTypesToBBIndex[(cpiece & 0b11111100) >> 2])

        # en passant capture
        # print(f'enPassantTarget : {enPassantTarget}')
        # if enPassantTarget:
        #     print(f'nextPosition : {nextPosition}, pieceType : {pieceType}')
        if enPassantTarget and nextPosition == enPassantTarget and pieceType == nPawn:
            self._changePiece(enPassantTarget - 8 + (colorType << 4), empty)    # remove capture piece

        # promotion
        if (moveType & 0b10):
            self._changePiece(nextPosition, (promoPieceType | colorType + 1))


        # [ update process ]

        # update king square
        if pieceType == nKing:
            self.PositionsOfKings[colorType] = nextPosition

        # update castling flags: if king moves, remove castling flags
        if pieceType == nKing:
            self.castlingFlags[colorType << 1] = False
            self.castlingFlags[(colorType << 1) + 1] = False
        # if rook moves, remove castling flags
        if (pieceType == nRook) and (0x8100000000000081 & (1 << currentPosition)):
            if currentPosition == 7:
                self.castlingFlags[0] = False
            if currentPosition == 0:
                self.castlingFlags[1] = False
            if currentPosition == 63:
                self.castlingFlags[2] = False
            if currentPosition == 56:
                self.castlingFlags[3] = False
        # if capture is rook, then remove castling flags
        if (cpiece & rook) and (0x8100000000000081 & (1 << nextPosition)):
            if nextPosition == 7:
                self.castlingFlags[0] = False
            if nextPosition == 0:
                self.castlingFlags[1] = False
            if nextPosition == 63:
                self.castlingFlags[2] = False
            if nextPosition == 56:
                self.castlingFlags[3] = False

        # set en passant target
        self.enPassantTarget = 0
        
        if (pieceType == nPawn) and (currentPosition + 16 == nextPosition + colorType*32):
            self.enPassantTarget = (currentPosition + nextPosition) >> 1
        #     print(f'enPassantTarget : {self.enPassantTarget}')
            
        # move list
        self.moveList[self.moveListCurrent] = Move(
            currentPosition, nextPosition, colorType, moveType, cpiece, promoPieceType, move.previousCastlingFlags)
        self.moveListCurrent += 1
        
        # update chess state
        self.nextRound()
        
        # print(f'After make : {move}')
        # printBitMaps(self.bitBoardSet)
        # printchess(self.board)

        return

    @dispatch()
    def unMakeMove(self):
        # variables
        self.moveListCurrent -= 1
        move = self.moveList[self.moveListCurrent]

        toSquare = move.toSquare
        fromSquare = move.fromSquare
        
        colorType = move.colorType
        pieceType = pieceTypesToBBIndex[(self.board[toSquare ^ 0b111000] & 0b11111100) >> 2]
        
        capturedPiece = move.capturedPiece
        moveType = move.moveType
        previousEpTarget = move.previousEpTarget

        # unpromotion
        if (moveType & 0b10):
            self._changePiece(toSquare, (pawn | colorType + 1))

        # unmake move
        self.castlingFlags = list(move.previousCastlingFlags)
        self._moveWithoutTest(toSquare, fromSquare, colorType, pieceType, empty)

        # undo capture
        if capturedPiece:
            self._changePiece(toSquare, capturedPiece)
        # undo en passant capture
        if previousEpTarget and (toSquare == previousEpTarget):
            self._changePiece(toSquare - 8 + (colorType << 4), (pawn | (colorType + 1) ^ 0b11))

        # update king square
        if pieceType == nKing:
            self.PositionsOfKings[colorType] = fromSquare

        # undo castling: undo rook move
        if (moveType & 0b100):
            self._moveWithoutTest((toSquare + fromSquare) >> 1, (((toSquare >> 2) & 0b1)*7 + (
                toSquare >> 5)*56), colorType, pieceType, empty)

        # update chess state
        self.enPassantTarget = previousEpTarget
        self.undoRound()

        return

    @dispatch(Move)
    def unMakeMove(self, move: Move):
        # variables
        self.moveListCurrent -= 1

        toSquare = move.toSquare
        fromSquare = move.fromSquare
        
        colorType = move.colorType
        pieceType = pieceTypesToBBIndex[(self.board[toSquare ^ 0b111000] & 0b11111100) >> 2]
        
        capturedPiece = move.capturedPiece
        moveType = move.moveType
        previousEpTarget = move.previousEpTarget

        # unUnpromotion
        if (moveType & 0b10):
            self._changePiece(toSquare, (pawn | colorType + 1))
            pieceType = nPawn

        # unmake move
        self.castlingFlags = list(move.previousCastlingFlags)
        self._moveWithoutTest(toSquare, fromSquare, colorType, pieceType, empty)

        # undo capture
        if capturedPiece:
            # print(f'toSquare : {toSquare}, capturedPiece : {capturedPiece}')
            self._changePiece(toSquare, capturedPiece)
        # undo en passant capture
        if previousEpTarget and (toSquare == previousEpTarget):
            self._changePiece(toSquare - 8 + (colorType << 4), (pawn | (colorType + 1) ^ 0b11))


        # update king square
        if pieceType == nKing:
            self.PositionsOfKings[colorType] = fromSquare

        # undo castling: undo rook move
        if (moveType & 0b100):
            self._moveWithoutTest((toSquare + fromSquare) >> 1, (((toSquare >> 2) & 0b1)*7 + (
                toSquare >> 5)*56), colorType, nRook, empty)

        # update chess state
        self.enPassantTarget = previousEpTarget
        self.undoRound()
        
        
        # print(f'After unMake : {move}')
        # printBitMaps(self.bitBoardSet)
        # printchess(self.board)
        return


    # funciton for testing

    def _getMoveList(self, sideToMove: int = 0) -> list:
        """
        return a list of possible movement for sideToMove.
        if sideToMove is not defined, return a list of all possible movement.

        Args:
            sideToMove (int, optional): \n
                side to move. 0 - none, 1 - white, 2 - black. Defaults to 0.

        Returns:
            Movelist (list[tuple[int]]): \n
                list of possible movement.
        """

        moveList = []
        castlingFlags = self.castlingFlags.copy()
        EpTarget = self.enPassantTarget

        for index in range(4):
            if self._IsCastling(index):
                # variables
                # types
                colorType = index >> 1  # 0 - white, 1 - black
                isKingSide = (index + 1) & 0b1
                # squares
                kingSquare = 4 + 56*colorType
                kingToSquare = (kingSquare - 2) + (isKingSide << 2)
                
                moveList.append(
                        Move(kingSquare, kingToSquare, colorType, 4, empty, empty, castlingFlags))

        # printchess(self.board)
        # printBitMaps(self.bitBoardSet)
        
        for currentPos in range(63, -1, -1):
            possibleMoveBB = self._possibleMove(currentPos, sideToMove)

            if possibleMoveBB == 0:
                continue

            piece = self.board[currentPos ^ 0b111000]

            for _ in range(64):
                if possibleMoveBB:
                    # variables
                    nextPos = bitScan(possibleMoveBB, False)
                    colorType = sideToMove >> 1
                    cpiece = self.board[nextPos ^ 0b111000]

                    # update possibleMoveBB
                    possibleMoveBB &= (possibleMoveBB - 1)

                    # promotion case
                    if (piece == white + pawn and (nextPos & 0b111000) == 56) or \
                        (piece == black + pawn and (nextPos & 0b111000) == 0):
                        moveList.append(
                            Move(currentPos, nextPos, colorType, 2, cpiece, (1 << 3), castlingFlags, EpTarget))
                        moveList.append(
                            Move(currentPos, nextPos, colorType, 2, cpiece, (1 << 4), castlingFlags, EpTarget))
                        moveList.append(
                            Move(currentPos, nextPos, colorType, 2, cpiece, (1 << 5), castlingFlags, EpTarget))
                        moveList.append(
                            Move(currentPos, nextPos, colorType, 2, cpiece, (1 << 6), castlingFlags, EpTarget))
                        continue

                    moveList.append(
                        Move(currentPos, nextPos, colorType, 1, cpiece, empty, castlingFlags, EpTarget))
                    continue

                break

        return moveList

    def perft(self, depth: int) -> int:
        '''
        #### initial position must be set before calling this function.\n
        
        return the number of nodes at depth.
        
        Args:
            depth (int): \n
                depth of perft.
                
        Returns:
            int: \n
                number of nodes at depth.
        '''
        possibleMoveList = [Move() for _ in range(256)]
        nodes = 0
        
        if depth == 0:
            return 1

        possibleMoveList = self._getMoveList(self.sideToMove)

        # printBitMaps(self.bitBoardSet)

        for move in possibleMoveList:
            self.makeMove(move)
            # if depth >> 1:
            #   printMove(move)
            nodes += self.perft(depth - 1)
            self.unMakeMove(move)
        
        # print(f'nodes : {nodes}')
        return nodes

    def perftDivide(self, depth: int) -> int:
        '''
        #### initial position must be set before calling this function.\n
        
        return the number of nodes at depth.
        
        Args:
            depth (int): \n
                depth of perft.
                
        Returns:
            int: \n
                number of nodes at depth.
        '''
        possibleMoveList = [Move() for _ in range(256)]
        divideList = []
        nodes = 0
        
        if depth == 0:
            return 1

        possibleMoveList = self._getMoveList(self.sideToMove)
        
        # print(f'len( possibleMoveList ) : \n{len(possibleMoveList)}\n')
        # printBitMaps(self.bitBoardSet)

        for index, move in enumerate(possibleMoveList):
            self.makeMove(move)
            
            divideList.append(self.perft(depth - 1))
            nodes += divideList[index]
            
            self.unMakeMove(move)
        
        # for index, node in enumerate(divideList):
            # printMove(possibleMoveList[index])
            # print(possibleMoveList[index])
            # print(f' : {node}')

        # print(f'nodes : {nodes}')
        return nodes

    # =================================================================

    

    def _IsEnd(self):
        # check end condition of game
        # check and checkmate condition is allowed for only 'side to move'
        # if opponent of 'side to move' is in check or checkmate, previous move is invalid move

        side = self.sideToMove
        count = 0

        # check previous move is self check
        if self._IsPositionUnderAttack(self.PositionsOfKings[2 - side]) != []:
            raise ValueError("self check is not allowed")

        posOfKing = self.PositionsOfKings[side - 1]

        if self._IsPositionUnderAttack(posOfKing) != []:
            print("White" if side == white else "Black", end="")

            if self._IsCheckMate(posOfKing):
                print(" is CheckMate!")
                return True
            else:
                print(" is Check!")

        return False