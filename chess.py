from const_variable import *
from printing_chessboard import *


class Chess():
    def __init__(self):
        # 1bit(color) + 3bit(pieceType)   ex) 1001 = black+pawn

        # 고정 초기 기물 배치
        self.__initPlacement = (
            black + rook, black + knight, black + bishop, black +
            queen, black + king, black + bishop, black + knight, black + rook,
            black + pawn, black + pawn, black + pawn, black + pawn, black +
            pawn, black + pawn, black + pawn, black + pawn,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            white + pawn, white + pawn, white + pawn, white + pawn, white +
            pawn, white + pawn, white + pawn, white + pawn,
            white + rook, white + knight, white + bishop, white + queen, white +
            king, white + bishop, white + knight, white + rook,
        )

        self.__placementsOfPieces = [set(range(48, 64)), set(range(16))]

        # Piece placement
        self.placement = list(self.__initPlacement)
        
        # Side to move : 0 - not defined, 1 - white, 2 - black
        self.colorToMove = 0

        # Castling ability
        # [ white king color castling( K, h1 ), white queen color castling( Q, a1 ), black king color castling( k, h8 ), black right castling( q, a8 ) ]
        self.specialMoveflag = [True, True, True, True]

        # en passant target square
        self.enPassantTarget = 0

        # Halfmove clock
        self.halfMoveClock = 0

        # fullmove counter
        self.fullMoveCounter = 0

        # [ start Pos, end Pos, piece ]
        self.previousMove = [0, 0, 0]

        self.PositionsOfPieaceBycolor = self._PositionsOfPiecesBycolor()
        self.PositionsOfKings = [60, 4]

    # basic oparation of chess
    def _reset(self) -> None:
        self.placement = list(self.__initPlacement)
        self.fullMoveCounter = 1
        self.colorToMove = white

        self.PositionsOfPieaceBycolor = self.__placementsOfPieces
        return

    def _NextRound(self) -> None:
        if self.colorToMove == white:
            self.colorToMove = black
            return

        self.colorToMove = black
        self.fullMoveCounter += 1
        return

    def _Promotion(self, Position: int, piece: int) -> None:
        if Position < 0 or Position >= 64:
            raise ValueError("Position is out of range")
        if (piece >> 2) not in pieceTypes or (piece & 0b11) not in colors:
            raise ValueError("piece is not defined")
        if self.placement[Position] == empty:
            raise Exception("promotion target is nonexistent")

        if self.placement[Position]:
            self.placement[Position] = piece
        return

    # TODO: make mapping function
    def _PositionsOfPiecesBycolor(self) -> list[list[int]]:
        PositionsOfPieaceBycolor = [[], []]

        for index, piece in enumerate(self.placement):
            if piece == empty:
                continue
            PositionsOfPieaceBycolor[0 if (piece >> 3) == white else 1] = index

        return PositionsOfPieaceBycolor

    # validation check
    def _directionOffset(self, firstPos: int, secondPos: int) -> int:
        if firstPos == secondPos:
            return 0

        rank_dist = secondPos % 8 - firstPos % 8
        file_dist = secondPos // 8 - firstPos // 8

        # is diagonal movement?
        if abs(file_dist) == abs(rank_dist):
            if rank_dist > 0:
                return 9 if file_dist > 0 else -7
            else:
                return 7 if file_dist > 0 else -9

        # is straight movement?
        if file_dist*rank_dist == 0:
            if rank_dist:
                return 1 if rank_dist > 0 else -1
            else:
                return 8 if file_dist > 0 else -8

        return 0

    def _absolutePinCheck(self, King_Pos: int, Pos: int) -> int:
        # King_Pos  : Position of the king
        # Pos       : Position of piece to check that it is in absolute pin

        # error : return '64'
        # if absolute pin : return 'passible Positions if exist'
        # if not absolute pin : return '64'

        piece = self.placement[Pos]

        if piece == empty:
            # print("err : _absolutePinCheck, piece is empty")
            return 64

        kingPiece = self.placement[King_Pos]

        if (kingPiece & 0b11111100) != king:
            # print("err : _absolutePinCheck, this is not king")
            return 64

        color = kingPiece & 0b00000011

        if (piece & 0b00000011) != color:
            # print("err : _absolutePinCheck, color is not same")
            return 64

        offset = self._directionOffset(King_Pos, Pos)

        # is this piece in Position that able to blocking check?
        if offset == 0:
            return 64

        # is there other piece in Position blocking check?
        for opponentPos in range(King_Pos+offset, Pos, offset):
            if self.placement[opponentPos] != empty:
                return 64

        result = [i for i in range(King_Pos+offset, Pos, offset)]

        # is there opponent piece threatening king?
        for opponentPos in range(Pos+offset, 64 if offset > 0 else -1, offset):
            # termination condition by rank
            if opponentPos < 0 or opponentPos >= 64:
                break

            piece = self.placement[opponentPos]

            if piece == empty:
                # termination condition by file
                if (opponentPos & 0b111 == 0 or opponentPos & 0b111 == 7):
                    break
                continue

            # is there other piece that is blocking check?
            if piece & 0b00000011 == color:
                return 64

            # Covered conditions : opponent piece is in this Position
            pieceType = piece & 0b11111100

            if (pieceType == queen) \
                    or (pieceType == rook and (abs(offset) == 1 or abs(offset) == 8)) \
                    or (pieceType == bishop and (abs(offset) == 7 or abs(offset) == 9)):
                return opponentPos

        return 64

    def _routeCheck(self, currentPos, nextPos) -> bool:
        if currentPos < 0 or currentPos >= 64:
            raise ValueError("currentPos is out of range")
        if nextPos < 0 or nextPos >= 64:
            raise ValueError("nextPos is out of range")

        offset = self._directionOffset(currentPos, nextPos)

        # check movement is line movement
        if offset == 0:
            return False

        # check blocking
        for i in range(currentPos + offset, nextPos, offset):
            if self.placement[i] == empty:
                continue
            return False

        return True

    def _MovRuleCheck(self, currentPos: int, nextPos: int) -> bool:
        if currentPos < 0 or currentPos >= 64:
            raise ValueError("currentPos is out of range")
        if nextPos < 0 or nextPos >= 64:
            raise ValueError("nextPos is out of range")

        piece = self.placement[currentPos]
        opponent = self.placement[nextPos]

        # is empty?
        if piece == empty:
            return False
        # are pieces same color?
        if (piece >> 2) == (opponent >> 2):
            return False

        pieceType = piece & 0b11111100
        color = piece & 0b00000011

        offset = self._directionOffset(currentPos, nextPos)

        file_dist = nextPos % 8 - currentPos % 8
        rank_dist = nextPos // 8 - currentPos // 8

        # is valid knight movement?
        if pieceType == knight:
            if (abs(abs(rank_dist) - abs(file_dist))) == 1 and abs(rank_dist) + abs(file_dist) == 3:
                return True
            return False

        # is valid direction of movement?
        if offset == 0:
            return False

        # is blocking?
        if self._routeCheck(currentPos, nextPos) is False:
            return False

        # is valid king movement?
        if pieceType == king:
            if abs(rank_dist) < 2 and abs(file_dist) < 2:
                return True
            return False

        # is valid rook movement?
        if pieceType == rook:
            if rank_dist*file_dist:
                return False
            return True

        # is valid rook movement?
        if pieceType == bishop:
            if abs(offset) == 7 or abs(offset) == 9:
                return True
            return False

        # is valid rook movement?
        if pieceType == queen:
            return True

        # white, black = 1, 2
        if pieceType == pawn:
            # forward
            if file_dist == 0:
                # one space
                if (color == white and rank_dist == -1) or (color == black and rank_dist == 1):
                    return True
                # two space
                if (color == white and rank_dist == -2 and currentPos // 8 == 6) or (color == black and rank_dist == 2 and currentPos // 8 == 1):
                    return True
            # attack
            if ((color == white and rank_dist == -1) or (color == black and rank_dist == 1)) and abs(file_dist) == 1:
                # nomal attack
                if opponent:
                    return True
                # en passant
                if opponent == empty and nextPos == self.enPassantTarget:
                    return True

        return False

    def _IsPositionUnderAttack(self, Pos, color=empty, piece=empty) -> list[int]:
        # check if Position is under attack by opponent
        # Position could be empty, but, in this case, color should be assigned by argument
        # able to assume other piece in this Position by argument value

        CheckingPiece = []

        if Pos < 0 or Pos > 63:
            raise ValueError("Pos is out of range")

        if piece == empty:
            piece = self.placement[Pos]
        if color == empty:
            color = piece & 0b00000011

        if color == empty:
            raise ValueError("color is not assigned")
        if color != piece & 0b00000011:
            raise ValueError("color and piece's color is not match")

        rankPos = Pos % 8
        filePos = Pos // 8
        pieceType = piece & 0b11111100

        # knight opponent checking
        for offset in [-17, -15, -10, -6, 6, 10, 15, 17]:
            opponentPos = Pos + offset

            # boundary
            if opponentPos < 0:
                continue
            if opponentPos > 63:
                break

            opponent = self.placement[opponentPos]

            # opponent existence
            if opponent == empty:
                continue

            opponentRankPos = opponentPos % 8
            opponentFilePos = opponentPos // 8

            # movement
            if abs(opponentRankPos - rankPos) + abs(opponentFilePos - filePos) != 3:
                continue

            if opponent & 0b11111100 == knight and opponent & 0b00000011 != color:
                CheckingPiece.append(opponentPos)

        for fileDirection, rankDirection in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            for i in range(1, 8):

                opponentFilePos = filePos + fileDirection*i
                opponentRankPos = rankPos + rankDirection*i

                # boundary
                if opponentRankPos < 0 or opponentRankPos > 7 \
                        or opponentFilePos < 0 or opponentFilePos > 7:
                    break

                opponentPos = opponentRankPos*8 + opponentFilePos

                # opponent existence
                if self.placement[opponentPos] == empty:
                    continue

                opponentColor = self.placement[opponentPos] & 0b00000011

                # color check
                if opponentColor == empty:
                    raise ValueError("opponent color is not assigned")
                if opponentColor == color:
                    break

                opponentType = self.placement[opponentPos] & 0b11111100

                # movement
                if opponentType == pawn:
                    if i != 1 or fileDirection == 0:
                        break

                    # nomal pawn attack
                    if (color == white and rankDirection == -1) \
                            and (color == black and rankDirection == 1):
                        CheckingPiece.append(opponentPos)
                        break

                    # en passant
                    if pieceType == pawn and rankDirection == 0:
                        enPassantTarget = self.enPassantTarget
                        if enPassantTarget == 0:
                            break
                        if (color == white and Pos == enPassantTarget - 8) \
                                or (color == black and Pos == enPassantTarget + 8):
                            CheckingPiece.append(opponentPos)
                    break

                if opponentType == rook:
                    if not fileDirection*rankDirection:
                        CheckingPiece.append(opponentPos)
                    break

                if opponentType == bishop:
                    if fileDirection*rankDirection:
                        CheckingPiece.append(opponentPos)
                    break

                if opponentType == queen:
                    CheckingPiece.append(opponentPos)
                    break

                if opponentType == king:
                    if i == 1:
                        CheckingPiece.append(opponentPos)
                    break

        print(CheckingPiece)

        return CheckingPiece

    def _Move(self, currentPos: int, nextPos: int) -> bool:
        if currentPos < 0 or currentPos >= 64:
            raise ValueError("currentPos is out of range")
        if nextPos < 0 or nextPos >= 64:
            raise ValueError("nextPos is out of range")
        if self._MovRuleCheck(currentPos, nextPos) == False:
            # print("movement is invalid by rule")
            return False

        piece = self.placement[currentPos]
        pieceType = piece & 0b11111100
        color = piece & 0b00000011

        if pieceType == king:
            # temparal movement
            savePos = self.placement[nextPos]
            self.placement[nextPos] = self.placement[currentPos]
            self.placement[currentPos] = empty

            if self._IsPositionUnderAttack(nextPos) == False:
                # print("King is in check")
                self.placement[currentPos] = self.placement[nextPos]
                self.placement[nextPos] = savePos
                return False

        elif self._absolutePinCheck(self.PositionsOfKings[color - 1], currentPos) != nextPos:
            # print("Piece is in absolute pin")
            return False

        # moving piece process
        self.placement[nextPos] = self.placement[currentPos]
        self.placement[currentPos] = empty

        self.PositionsOfPieaceBycolor[color-1].remove(currentPos)
        self.PositionsOfPieaceBycolor[color-1].add(nextPos)

        if pieceType == pawn \
            and ((color == white and nextPos == currentPos - 16)
                 or (color == black and nextPos == currentPos + 16)):
            self.enPassantTarget = (nextPos + currentPos) >> 1
            return True

        if pieceType == king:
            self.PositionsOfKings[color-1] = nextPos

        self.enPassantTarget = 0
        return True

    def _IsCheckMate(self, Pos):
        if Pos < 0 or Pos > 63:
            raise ValueError("Pos is out of range")

        kingPiece = self.placement[Pos]

        if kingPiece & 0b11111100 != king:
            raise ValueError("this is not king piece")

        CheckingPieces = self._IsPositionUnderAttack(Pos)

        color = kingPiece & 0b00000011
        rankPos = Pos % 8
        filePos = Pos // 8

        # checking the existence of king's escape movement
        for rankOffset, fileOffset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            opponentRankPos = rankPos + rankOffset
            opponentFilePos = filePos + fileOffset

            if opponentRankPos < 0 or opponentRankPos > 7 or opponentFilePos < 0 or opponentFilePos > 7:
                continue

            opponentPos = opponentRankPos*8 + opponentFilePos

            if self.placement[opponentPos] & 0b00000011 == color:
                continue
            if self._IsPositionUnderAttack(opponentPos, color, kingPiece):
                continue

            return False

        # if not double check
        if len(CheckingPieces) == 1:

            checkingPiecePos = CheckingPieces[0]
            blockingPieces = self._IsPositionUnderAttack(checkingPiecePos)

            # could catch checkingPiece?
            if blockingPieces != []:
                if len(blockingPieces) == 1 and self.placement[blockingPieces[0]] % 8 == 6:
                    return True
                return False

            # or could blocking checkingPiece?
            offset = 0

            if Pos//8 == checkingPiecePos//8:
                offset = 1
            else:
                for i in range(10, 7, -1):
                    if abs(checkingPiecePos - Pos) % i == 0:
                        offset = i
                        break   # if multiple conditions are satisfied, largest value is selected

            if offset == 0:
                return True

            if Pos > checkingPiecePos:
                offset = -offset

            for i in range(Pos + offset, checkingPiecePos, offset):
                if self._IsPositionUnderAttack(i, 3-color):
                    return False

        return True

    def _IsEnd(self):
        # check end condition of game
        # check and checkmate condition is allowed for only 'side to move'
        # if opponent of 'side to move' is in check or checkmate, previous move is invalid move

        side = self.colorToMove
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

# ======== main ======== #


chess = Chess()

printchess(chess.placement)

dict_PiecepieceType = {"P": 1, "R": 2, "N": 3, "B": 4, "Q": 5, "K": 6}

while (chess._IsEnd() == False):
    Round = chess.fullMoveCounter

    print("\nRound :", Round+1, "\n")

    printchess(chess.placement)

    INPUT = input()
    err_input = False
    Pos = [-1, 0]
    pieceType = 0
    castling = 0

    if len(INPUT) == 3:
        if 'PRNBQKprnbqk'.count(INPUT[0]):
            pieceType = dict_PiecepieceType.get(INPUT[0].upper(), 0)
            INPUT = INPUT[1:]
        else:
            err_input = True

    if len(INPUT) == 2:
        if 'ABCDEFGHabcdefgh12345678'.count(INPUT[0]) and '12345678'.count(INPUT[1]):
            rankPos = 0
            filePos = 8-int(INPUT[1])

            if '12345678'.count(INPUT[0]):
                rankPos = int(INPUT[0])-1
            else:
                rankPos = int(ord(INPUT[0].upper()) - ord('A'))

            Pos[1] = rankPos + filePos*8

            if pieceType:
                Possible_pieces = list(filter(
                    lambda x: chess.Position[x]//8 == Round % 2 and chess.Position[x] % 8 == pieceType, chess._IsPositionUnderAttack(Pos[1])))
            else:
                Possible_pieces = list(
                    filter(lambda x: chess.Position[x]//8 == Round % 2, chess._IsPositionUnderAttack(Pos[1])))

            if Possible_pieces:
                if len(Possible_pieces) > 1:
                    print("둘수 있는 말이 2개 이상입니다.")
                else:
                    Possible_Pos = Possible_pieces[0]
                    print(Possible_Pos % 8, Possible_Pos//8)
                    Pos[0] = Possible_Pos
            else:
                print("둘수 있는 말이 없습니다.")

            if Pos[0] == -1:
                err_input = True

        elif INPUT.isalpha() and pieceType == 0:
            if INPUT[1].upper() == 'C' and chess.special_Mov_flag[Round % 2] & 8:
                if 'RK'.count(INPUT[1].upper()):
                    castling = 2
                if 'LQ'.count(INPUT[1].upper()):
                    castling = 1

                if castling:
                    if castling == 1:
                        sign = -1
                    else:
                        sign = 1

                    for i in range(3):
                        if i and chess.Position[4+1*sign + 56*((Round+1) % 2)]:
                            castling = 0
                            break
                        if chess._IsPositionUnderAttack(4+1*sign + 56*((Round+1) % 2), Round % 2):
                            castling = 0
                            break

                else:
                    err_input = True
            else:
                err_input = True

        elif len(INPUT) == 4 and INPUT.isdigit() and not INPUT.count('9'):
            Pos[0] = (int(INPUT[0]) - 1) + (8 - int(INPUT[1]))*8
            Pos[1] = (int(INPUT[2]) - 1) + (8 - int(INPUT[3]))*8

        else:
            err_input = True

        if err_input:
            print("input err")
            continue

        if castling:
            if castling == 2:
                sign = 1
            else:
                sign = -1

            chess._Move(4, 7*(Round % 2), 4 + 2*sign, 7*(Round % 2))
            chess._Move(7*(castling-1), 7*(Round %
                                           2), 4 + 1*sign, 7*(Round % 2))
            chess.special_Mov_flag[Round % 2] = 0
            chess._NextRound()

        elif chess._MovCheck(Pos[0], Pos[1]):

            if chess.special_Mov_flag[Round % 2]:
                if Pos[0] == 56*((Round+1) % 2) or Pos[1] == 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 23
                if Pos[0] == 7 + 56*((Round+1) % 2) or Pos[1] == 7 + 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 15
                if Pos[0] == 4 + 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 7

            chess._Move(Pos[0], Pos[1])

            for i in range(64):
                if chess.Position[i] == 6 + (Round % 2)*8 and chess._IsPositionUnderAttack(i):
                    err_input = True

            if err_input:
                chess._Move(Pos[1], Pos[0])
                print("체크로 불가한 이동입니다.")
                continue

            chess._NextRound
            print('(', Pos[0] % 8 + 1, 8 - Pos[0]//8,
                  ') --> (', Pos[1] % 8 + 1, 8 - Pos[1]//8, ')')

        else:
            print("Fatal err")
            continue

        if chess.Position[Pos[0]] % 8 == 1 and abs(Pos[1] - Pos[0]) == 16:
            chess.special_Mov_flag[(Round+1) % 2] |= (Pos[0] % 8)
        else:
            chess.special_Mov_flag[(Round+1) % 2] &= 24
            chess.special_Mov_flag[Round % 2] &= 24

    chess._PrintChess()
    chess._NextRound()

if chess.colorToMove == white:
    print("white team wins")
else:
    print("black team wins")
