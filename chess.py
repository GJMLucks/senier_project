from const_variable import *
import printing_chessboard


class Chess():
    def __init__(self):
        # 1bit(color) + 3bit(piece_type)   ex) 1001 = black+pawn

        # 고정 초기 기물 배치
        self.__initalPosition = (
            black+rook, black+knight, black+bishop, black+queen, black +
            king, black+bishop, black+knight, black+rook,
            black+pawn, black+pawn, black+pawn, black+pawn, black +
            pawn, black+pawn, black+pawn, black+pawn,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            empty, empty, empty, empty, empty, empty, empty, empty,
            white+pawn, white+pawn, white+pawn, white+pawn, white +
            pawn, white+pawn, white+pawn, white+pawn,
            white+rook, white+knight, white+bishop, white+queen, white +
            king, white+bishop, white+knight, white+rook,
        )

        self.__positionsOfPieces = [set(range(48, 64)), set(range(16))]

        self.position = list(self.__initalPosition)
        
        self.positionsOfPieaceByColor = self._PositionsOfPiecesByColor()

        self.positionsOfKings = [60, 4]

        self.round = 0

        # [ white left castling( a1 ), white right castling, black left castling, black right castling ]
        self.special_Move_flag = [True, True, True, True]

        # [ start pos, end pos, piece ]
        self.previous_Move = [0, 0, 0]

    def _PositionsOfPiecesByColor(self) -> list[list[int]]:
        positionsOfPieaceByColor = [[], []]

        for index, piece in enumerate(self.position):
            if piece == empty:
                continue
            positionsOfPieaceByColor[0 if (piece >> 3) == white else 1] = index

        return positionsOfPieaceByColor

    def _reset(self) -> None:
        self.position = list(self.__initalPosition)
        self.round = 0
        self.positionsOfPieaceByColor = self.__positionsOfPieces

    def _NextRound(self) -> None:
        self.round += 1

    def _PrintPiece(self, Pos: int) -> None:
        piece_type = self.position[Pos] % 8
        
        if piece_type == empty:
            print("| __ ", end="")
            return
        
        color = self.position[Pos]//8

        print("| ", end="")

        initial = pieceInitials[piece_type]

        # "." mean black piece
        print("b" if color else "w", end="")
        
        if initial:
            print(initial, end=" ")
        else:
            print("Piece Print err")
            return


    # 체스 출력
    def _PrintChess(self) -> None:
        print("  *=======================================*")

        for i in range(8):
            # rank number
            print(8-i, end=" ")
            # piece initial
            for j in range(8):
                self._PrintPiece(i*8 + j)
            # vertical line
            print("|")
            if i == 7:
                break
            # horizontal line
            print("  -----------------------------------------")

        print("  *=======================================*")
        print("     a    b    c    f    e    f    g    h ")
        print("    (1)  (2)  (3)  (4)  (5)  (6)  (7)  (8)")

    def _Move(self, Pos: int, Mov_Pos: int) -> None:
        self.position[Mov_Pos] = self.position[Pos]
        self.position[Pos] = empty

    def _Promotion(self, Pos: int, Piece: int) -> None:
        if self.position[Pos]:
            self.position[Pos] = Piece
        else:
            print("Change err")

    def _directionOffset(self, firstPos: int, secondPos: int) -> int:
        rank_dist = secondPos % 8 - firstPos % 8
        file_dist = secondPos//8 - firstPos//8

        if abs(file_dist) == abs(rank_dist):
            if rank_dist > 0:
                return 9 if file_dist > 0 else -7
            else:
                return 7 if file_dist > 0 else -9

        if (not file_dist or not rank_dist) and file_dist*rank_dist == 0:
            if rank_dist:
                return 1 if rank_dist > 0 else -1
            else:
                return 8 if file_dist > 0 else -8

        return 0

    def _AbsolutePinCheck(self, King_pos: int, Pos: int) -> list[int]:
        # King_pos  : position of the king
        # Pos       : position of piece to check that it is in absolute pin

        # error : return [ negative error code ]
        # if absolute pin : return [ passible positions if exist ]
        # if not absolute pin : return [ 64 ]

        piece = self.position[Pos]

        if piece == empty:
            print("err : _AbsolutePinCheck, piece is empty")
            return [-1]

        kingPiece = self.position[King_pos]

        if (kingPiece % 8) != king:
            print("err : _AbsolutePinCheck, this is not king")
            return [-2]

        color = kingPiece // 8

        if (piece // 8) != color:
            print("err : _AbsolutePinCheck, color is not same")
            return [-3]

        offset = self._directionOffset(King_pos, Pos)

        # this piece is not in absolute pin position
        if offset == 0:
            return [64]

        # there is no piece between king and piece
        for current_pos in range(King_pos+offset, Pos, offset):
            if self.position[current_pos] != empty:
                return [64]

        result = [i for i in range(King_pos+offset, Pos, offset)]

        # there is opponent piece threatening king
        for current_pos in range(Pos+offset, 65 if offset > 0 else -1, offset):
            piece = self.position[current_pos]

            # existence check
            if piece == empty:
                # edge position check
                if (current_pos % 8 == 0 or current_pos % 8 == 7):
                    break
                continue
            # color check
            if piece//8 == color:
                return [64]

            piece_type = piece % 8

            if (piece_type == queen) or (piece_type == rook and (abs(offset) == 1 or abs(offset) == 8)) or (piece_type == bishop and (abs(offset) == 7 or abs(offset) == 9)):
                result.extend([
                    i for i in range(Pos+offset, current_pos, offset)
                ])
                return result

        return [64]

    def _RouteCheck(self, Pos, Mov_Pos):
        offset = self._directionOffset(Pos, Mov_Pos)

        # invalid movement
        if offset == 0:
            print("? err")
            return False

        # blocking check
        for i in range(Pos + offset, Mov_Pos, offset):
            if self.position[i] == empty:
                continue

            print(i, "--- err" if abs(offset) ==
                  1 else "| err" if abs(offset) == 8 else "X err")
            return False

        return True

    def _MovRuleCheck(self, Pos: int, mov_Pos: int) -> bool:
        # boundary check
        if Pos < 0 or Pos > 63:
            return False
        if mov_Pos < 0 or mov_Pos > 63:
            return False

        piece = self.position[Pos]
        opp_piece = self.position[mov_Pos]

        if piece == empty:
            print("there is no piece")
            return False
        if piece//8 != (self.round) % 2:
            print("Round err")
            return False
        if opp_piece and piece//8 == opp_piece//8:
            print("Color err")
            return False

        piece_type = piece % 8
        Color = piece//8

        rank_dist = mov_Pos % 8 - Pos % 8
        file_dist = mov_Pos//8 - Pos//8

        if piece_type == knight:
            if not ((abs(abs(rank_dist) - abs(file_dist))) == 1 and abs(abs(rank_dist) + abs(file_dist)) == 3):
                print("N err")
                return False
            return True

        if not self._RouteCheck(Pos, mov_Pos):
            print("Blocking err")
            return False

        if piece_type == king:
            if not (abs(rank_dist) < 2 and abs(file_dist) < 2):
                print("K err")
                return False
            return True

        if piece_type == rook:
            if rank_dist*file_dist:
                print("R err")
                return False
            return True

        if piece_type == bishop:
            if abs(rank_dist) != abs(file_dist):
                print("B err")
                return False
            return True

        if piece_type == queen:
            if rank_dist*file_dist and abs(rank_dist) != abs(file_dist):
                print("Q err")
                return False
            return True

        # white, black = 0, 1
        if piece_type == pawn:
            # forward
            if rank_dist == 0:
                # one space
                if file_dist + 1 == 2*Color:
                    return True
                # two space
                if ((Pos//8) + (5*Color)) == 6 and file_dist + 2 == 4*Color:
                    return True
            # attack
            if abs(rank_dist) == 1 and file_dist + 1 == 2*Color and opp_piece:
                return True
            # en passant
            prev_mov = self.previous_Move
            prev_move_file = prev_mov[0] % 8
            if prev_mov[2] % 8 == pawn and abs((prev_mov[0]//8) - (prev_mov[1]//8)) == 2 and prev_move_file == mov_Pos % 8 and abs(prev_move_file - (Pos % 8)) == 1:
                return True

        return True

    def _Mov(self, Pos: int, mov_Pos: int) -> bool:
        if self._MovRuleCheck(Pos, mov_Pos) == False:
            print("movement is invalid by rule")
            return False

        piece = self.position[Pos]
        color = piece//8

        if self._AbsolutePinCheck(self.positionsOfKings[color], Pos):
            print("Piece is in absolute pin")
            return False

        self.positionsOfPieaceByColor[color].remove(Pos)
        self.positionsOfPieaceByColor[color].add(mov_Pos)

        if piece % 8 == king:
            self.positionsOfKings[color] = mov_Pos

        return True

    def _IsCheck(self, Pos, Color=None, piece_type=None):
        # _IsCheck 는 그 위치가 체크인지 확인하는 함수다.
        # 팀은 정해져야하며 기물 없이 빈칸이어도 된다.
        # 기물 유무에 상관없이 해당 팀의 기물을 그 위치에 움직인다면 잡힐 가능성이 있는지 확인한다.
        # 위 서술은 'en passant' 에서 헷갈릴 수 있다.

        CheckingPiece = []

        # boundary checking
        if Pos < 0 or Pos > 63:
            print("Pos err")
            return [-1]  # Pos err

        # color checking
        if Color is None:
            if self.position[Pos] == empty:
                print("Color is not assigned err")
                return [-2]  # Color is not assigned err
            Color = self.position[Pos]//8
        else:
            if Color != self.position[Pos]//8:
                print("Color is wrong err")
                return [-3]  # Color is wrong err

        # piece_type checking
        if piece_type is None:
            piece_type = self.position[Pos] % 8

        rank_pos = Pos % 8
        file_pos = Pos // 8

        # knight movement checking
        for offset in knight_move_offset:
            current_pos = Pos + offset

            # boundary checking
            if Pos < 0 or Pos > 63:
                continue

            checking_rank_pos = current_pos % 8
            checking_file_pos = current_pos // 8

            if abs(checking_rank_pos - rank_pos) + abs(checking_file_pos - file_pos) != 3:
                continue
            if self.position[current_pos] % 8 == knight and self.position[current_pos]//8 != Color:
                CheckingPiece.append(Pos)

        for x_direction, y_direction in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            for i in range(1, 8):
                X = rank_pos + x_direction*i
                Y = file_pos + y_direction*i

                # boundary checking
                if X < 0 or X > 7 or Y < 0 or Y > 7:
                    continue
                current_pos = Y*8 + X

                # opponent existence checking
                if self.position[current_pos] == empty:
                    continue
                opp_color = self.position[current_pos]//8
                if opp_color == Color:
                    break

                opp_piece_type = self.position[current_pos] % 8

                if opp_piece_type == pawn:
                    if i != 1 or x_direction == 0:
                        break

                    # nomal pawn movement
                    if Color*2 - y_direction == 1:
                        CheckingPiece.append(pos)
                        break

                    # en passant
                    if piece_type == pawn and self.position[Pos+16-32*Color] == pawn+8*Color and self.position[Pos+8-16*Color] == empty and y_direction == 0:
                        CheckingPiece.append(pos)
                        break

                if opp_piece_type == rook:
                    if not x_direction*y_direction:
                        CheckingPiece.append(pos)
                    break

                if opp_piece_type == bishop:
                    if x_direction*y_direction:
                        CheckingPiece.append(pos)
                    break

                if opp_piece_type == queen:
                    CheckingPiece.append(pos)
                    break

                if opp_piece_type == king:
                    if i == 1:
                        CheckingPiece.append(pos)
                    break

        print(CheckingPiece)

        return CheckingPiece

    def _IsCheckMate(self, Pos):
        if self.position[Pos] % 8 != king:
            print("error : this is not king piece")
            return False

        CheckingPieces = self._IsCheck(Pos)

        Color = self.position[Pos]//8
        rank_pos = Pos % 8
        file_pos = Pos//8

        # checking the existence of king's escape movement
        for x_offset, y_offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            X = rank_pos + x_offset
            Y = file_pos + y_offset

            if X < 0 or X > 7 or Y < 0 or Y > 7:
                continue
            current_pos = Y*8 + X

            if self.position[current_pos]//8 == Color:
                continue
            if self._IsCheck(current_pos, Color):
                continue

            return False

        # if not double check, 1) could catch checking piece?
        if len(CheckingPieces) == 1:

            opp_Pos = CheckingPieces[0]
            opp_CheckingPieces = self._IsCheck(opp_Pos)

            if opp_CheckingPieces:
                if len(opp_CheckingPieces) == 1 and self.position[opp_CheckingPieces[0]] % 8 == 6:
                    return True
                return False

            basic_offsets = {-1, 1, -8, 8, -9, -7, 7, 9}
            offset = 0

            if Pos//8 == opp_Pos//8:
                if opp_Pos > Pos:
                    offset = 1
                else:
                    offset = -1
            else:
                for i in range(2, 8):
                    if (opp_Pos - Pos) % basic_offsets[i] == 0:
                        offset = basic_offsets[i]

            if offset == 0:
                return True

            for i in range(Pos + offset, opp_Pos, offset):
                if self._IsCheck(i, abs(1-Color)):
                    return False

        return True

    def _IsEnd(self):
        Turn = self.round % 2
        count = 0

        for i in range(64):
            if self.position[i] % 8 == 6:
                count += 1
                if self._IsCheck(i):
                    if Turn:
                        print("Black", end="")
                    else:
                        print("White", end="")

                    if self._IsCheckMate(i):
                        print(" is CheckMate!")
                        return True
                    else:
                        print(" is Check!")

                elif self._IsCheck(i):
                    print("End game err")
                    return True

        if count != 2:
            print("End game err")
            return True

        return False

# ======== main ======== #


chess = Chess()

chess._PrintChess()

dict_Piecepiece_type = {"P": 1, "R": 2, "N": 3, "B": 4, "Q": 5, "K": 6}

while (chess._IsEnd() == False):
    Round = chess.round

    print("\nRound :", Round+1, "\n")
    chess._PrintChess

    INPUT = input()
    err_input = False
    pos = [-1, 0]
    piece_type = 0
    castling = 0

    if len(INPUT) == 3:
        if 'PRNBQKprnbqk'.count(INPUT[0]):
            piece_type = dict_Piecepiece_type.get(INPUT[0].upper(), 0)
            INPUT = INPUT[1:]
        else:
            err_input = True

    if len(INPUT) == 2:
        if 'ABCDEFGHabcdefgh12345678'.count(INPUT[0]) and '12345678'.count(INPUT[1]):
            rank_pos = 0
            file_pos = 8-int(INPUT[1])

            if '12345678'.count(INPUT[0]):
                rank_pos = int(INPUT[0])-1
            else:
                rank_pos = int(ord(INPUT[0].upper()) - ord('A'))

            pos[1] = rank_pos + file_pos*8

            if piece_type:
                possible_pieces = list(filter(
                    lambda x: chess.position[x]//8 == Round % 2 and chess.position[x] % 8 == piece_type, chess._IsCheck(pos[1])))
            else:
                possible_pieces = list(
                    filter(lambda x: chess.position[x]//8 == Round % 2, chess._IsCheck(pos[1])))

            if possible_pieces:
                if len(possible_pieces) > 1:
                    print("둘수 있는 말이 2개 이상입니다.")
                else:
                    possible_pos = possible_pieces[0]
                    print(possible_pos % 8, possible_pos//8)
                    pos[0] = possible_pos
            else:
                print("둘수 있는 말이 없습니다.")

            if pos[0] == -1:
                err_input = True

        elif INPUT.isalpha() and piece_type == 0:
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
                        if i and chess.position[4+1*sign + 56*((Round+1) % 2)]:
                            castling = 0
                            break
                        if chess._IsCheck(4+1*sign + 56*((Round+1) % 2), Round % 2):
                            castling = 0
                            break

                else:
                    err_input = True
            else:
                err_input = True

        elif len(INPUT) == 4 and INPUT.isdigit() and not INPUT.count('9'):
            pos[0] = (int(INPUT[0]) - 1) + (8 - int(INPUT[1]))*8
            pos[1] = (int(INPUT[2]) - 1) + (8 - int(INPUT[3]))*8

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

        elif chess._MovCheck(pos[0], pos[1]):

            if chess.special_Mov_flag[Round % 2]:
                if pos[0] == 56*((Round+1) % 2) or pos[1] == 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 23
                if pos[0] == 7 + 56*((Round+1) % 2) or pos[1] == 7 + 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 15
                if pos[0] == 4 + 56*((Round+1) % 2):
                    chess.special_Mov_flag[Round % 2] &= 7

            chess._Move(pos[0], pos[1])

            for i in range(64):
                if chess.position[i] == 6 + (Round % 2)*8 and chess._IsCheck(i):
                    err_input = True

            if err_input:
                chess._Move(pos[1], pos[0])
                print("체크로 불가한 이동입니다.")
                continue

            chess._NextRound
            print('(', pos[0] % 8 + 1, 8 - pos[0]//8,
                  ') --> (', pos[1] % 8 + 1, 8 - pos[1]//8, ')')

        else:
            print("Fatal err")
            continue

        if chess.position[pos[0]] % 8 == 1 and abs(pos[1] - pos[0]) == 16:
            chess.special_Mov_flag[(Round+1) % 2] |= (pos[0] % 8)
        else:
            chess.special_Mov_flag[(Round+1) % 2] &= 24
            chess.special_Mov_flag[Round % 2] &= 24

    chess._PrintChess()
    chess._NextRound()

if chess.round % 2 == 0:
    print("흰팀 승리")
else:
    print("검팀 승리")
