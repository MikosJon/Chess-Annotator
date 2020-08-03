from definicije import *

class Figure:
    def __init__(self, name, color, position, possible_moves):
        self.name = name
        self.color = color
        self.position = position
        self.possible_moves = possible_moves

    @property
    def rank(self):
        return self.position[0]

    @property
    def file(self):
        return 'abcdefgh'[self.position[1] - 1]

    def as_piece(self):
        if self.color == Color.White:
            return TO_WHITE_PIECE[self.name]
        else:
            return TO_BLACK_PIECE[self.name]

    def as_name(self):
        return self.color.name + ' ' + self.name.name


class Game:
    def __init__(self):
        self.in_play = set()
        self.captured = set()
        self.promoted_pawns = set()

        self.moves = []

        self.white_short_castle = True
        self.white_long_castle = True
        self.black_short_castle = True
        self.black_long_castle = True

        self.white_long_rook = Figure(Name.Rook, Color.White, (1, 1), ROOK_MOVES)
        self.white_short_rook = Figure(Name.Rook, Color.White, (1, 8), ROOK_MOVES)

        self.in_play.add(self.white_long_rook)
        self.in_play.add(self.white_short_rook)

        self.black_long_rook = Figure(Name.Rook, Color.Black, (8, 1), ROOK_MOVES)
        self.black_short_rook = Figure(Name.Rook, Color.Black, (8, 8), ROOK_MOVES)

        self.in_play.add(self.black_long_rook)
        self.in_play.add(self.black_short_rook)

        self.in_play.add(Figure(Name.King  , Color.White, (1, 5), KING_MOVES))
        self.in_play.add(Figure(Name.Queen , Color.White, (1, 4), QUEEN_MOVES))
        self.in_play.add(Figure(Name.Bishop, Color.White, (1, 3), BISHOP_MOVES))
        self.in_play.add(Figure(Name.Bishop, Color.White, (1, 6), BISHOP_MOVES))
        self.in_play.add(Figure(Name.Knight, Color.White, (1, 2), KNIGHT_MOVES))
        self.in_play.add(Figure(Name.Knight, Color.White, (1, 7), KNIGHT_MOVES))
        for i in range(1, 9):
            self.in_play.add(Figure(Name.Pawn, Color.White, (2, i), WHITE_PAWN_MOVES))

        self.in_play.add(Figure(Name.King  , Color.Black, (8, 5), KING_MOVES))
        self.in_play.add(Figure(Name.Queen , Color.Black, (8, 4), QUEEN_MOVES))
        self.in_play.add(Figure(Name.Bishop, Color.Black, (8, 3), BISHOP_MOVES))
        self.in_play.add(Figure(Name.Bishop, Color.Black, (8, 6), BISHOP_MOVES))
        self.in_play.add(Figure(Name.Knight, Color.Black, (8, 2), KNIGHT_MOVES))
        self.in_play.add(Figure(Name.Knight, Color.Black, (8, 7), KNIGHT_MOVES))
        for i in range(1, 9):
            self.in_play.add(Figure(Name.Pawn, Color.Black, (7, i), BLACK_PAWN_MOVES))

    @property
    def last_move(self):
        return self.moves[-1][0]

    def printable_state(self):
        out = ''
        board = [['.'] * 8 for _ in range(8)]
        for fig in self.in_play:
            row, col = fig.position
            board[row-1][col-1] = fig.as_piece()
        for i, row in enumerate(reversed(board)):
            out += ''.join(row) + ' ' + str(8 - i) + '\n'
        out += 'abcdefgh'
        return out

    def remove_from_play(self, figure):
        self.in_play.remove(figure)
        self.captured.add(figure)

    def get_figures_by_name(self, name, color):
        out = []
        for fig in self.in_play:
            if fig.name == name and fig.color == color:
                out.append(fig)
        return out

    def get_figure_by_pos(self, pos):
        for fig in self.in_play:
            if fig.position == pos:
                return fig

    def promote_pawn(self, pawn, piece):
        self.in_play.remove(pawn)
        self.promoted_pawns.add(pawn)
        self.in_play.add(Figure(piece, pawn.color, pawn.position, PROMOTION_MOVES[piece]))

    def undo_promotion(self, pawn):
        promoted_piece = self.get_figure_by_pos(pawn.position)
        self.in_play.remove(promoted_piece)
        self.in_play.add(pawn)

    def is_stalemate(self, color):
        if self.is_king_in_check_now(color):
            return False
        for figure in self.in_play:
            if figure.color == color:
                if len(self.figure_legal_moves(figure)) != 0:
                    return False
        return True

    def is_mate(self):
        return self.moves[-1][1].mate

    def get_info(self, figure, target, *, promo_piece=None):
        notation_info = NotationInfo()
        notation_info.promotion = promo_piece

        opponent = other_color(figure.color)
        notation_info.check = self.is_king_in_check_after(figure, target, color=opponent, promo_piece=promo_piece)
        if notation_info.check:
            if len(self.all_legal_moves_after(figure, target, color=opponent, promo_piece=promo_piece)) == 0:
                notation_info.mate = True

        same_pieces = self.get_figures_by_name(figure.name, figure.color)
        same_pieces.remove(figure)
        if len(same_pieces) != 0:
            for fig in same_pieces:
                if self.is_legal(fig, target, promo_piece=promo_piece):
                    notation_info.unique = False
                    if fig.rank == figure.rank:
                        notation_info.rank = True
                    if fig.file == figure.file:
                        notation_info.file = True

        if self.get_figure_by_pos(target) is not None:
            notation_info.captures = True
        elif self.is_en_passant(figure, target):
            notation_info.captures = True
        return notation_info

    def get_move(self, figure, target, *, promo_piece=None):
        move = Move()
        move.piece = figure.name
        move.color = figure.color
        move.start = figure.position
        move.target = target
        move.en_passant = self.is_en_passant(figure, target)
        move.castling = self.is_castling_legal(figure, target)
        move.promo_piece = promo_piece
        return move

    def move_figure_to(self, figure, target, *, promo_piece=None):
        if self.is_en_passant(figure, target):
            captured_figure = self.get_figure_by_pos(self.last_move.target)
        else:
            captured_figure = self.get_figure_by_pos(target)

        if captured_figure:
            self.remove_from_play(captured_figure)
        figure.position = target

        if figure.name == Name.Pawn and target[0] in {1, 8}:
            if promo_piece is not None:
                self.promote_pawn(figure, promo_piece)

    def is_legal(self, figure, target, *, promo_piece=None):
        if self.is_move_possible(figure, target):
            if not self.is_king_in_check_after(figure, target, promo_piece=promo_piece):
                return True
        return False

    def is_move_possible(self, figure, target, *, check_flag=True):
        if check_flag:
            opponent_king = self.get_figures_by_name(Name.King, other_color(figure.color))[0]
            if target == opponent_king.position:
                return False

        move = (target[0] - figure.position[0], target[1] - figure.position[1])
        number_of_moved_squares = max(abs(move[0]), abs(move[1]))
        curr_position = figure.position

        if target[0] not in range(1, 9) or target[1] not in range(1, 9):
            return False

        if figure.name == Name.King and number_of_moved_squares == 2:
            return self.is_castling_legal(figure, target)

        if move not in figure.possible_moves:
            return False

        if move[0] == 0:
            dx = 0
        else:
            dx = move[0] // abs(move[0])
        if move[1] == 0:
            dy = 0
        else:
            dy = move[1] // abs(move[1])

        pos_white = set()
        pos_black = set()

        for fig in self.in_play:
            if fig.color == Color.White:
                pos_white.add(fig.position)
            else:
                pos_black.add(fig.position)

        if figure.color == Color.White and target in pos_white:
            return False
        if figure.color == Color.Black and target in pos_black:
            return False

        if figure.name == Name.Knight:
            return True

        if figure.name == Name.Pawn:
            if number_of_moved_squares == 2:
                if figure.color == Color.White and curr_position[0] != 2:
                    return False
                if figure.color == Color.Black and curr_position[0] != 7:
                    return False
            if move[1] != 0 and not self.is_en_passant(figure, target):
                if figure.color == Color.White and target not in pos_black:
                    return False
                if figure.color == Color.Black and target not in pos_white:
                    return False
            else:
                if target in pos_black or target in pos_white:
                    return False

        for i in range(1, number_of_moved_squares):
            test_position = (curr_position[0] + i * dx, curr_position[1] + i * dy)
            if test_position in pos_white or test_position in pos_black:
                return False

        return True

    def is_castling_legal(self, king, target):
        if king.name != Name.King:
            return False
        if king.color == Color.White:
            if target[1] == 7 and self.white_short_castle:
                figure = self.get_figure_by_pos((1, 8))
                if figure is None or figure.name != Name.Rook or figure.color == Color.Black:
                    return False
                if self.get_figure_by_pos((1, 6)) is not None or self.get_figure_by_pos((1, 7)) is not None:
                    return False
                if self.is_king_in_check_now(king.color):
                    return False
                king.position = (1, 6)
                if self.is_king_in_check_now(king.color):
                    king.position = (1, 5)
                    return False
                king.position = (1, 7)
                if self.is_king_in_check_now(king.color):
                    king.position = (1, 5)
                    return False
                king.position = (1, 5)

            elif target[1] == 3 and self.white_long_castle:
                figure = self.get_figure_by_pos((1, 1))
                if figure is None or figure.name != Name.Rook or figure.color == Color.Black:
                    return False
                for col in range(2, 5):
                    if self.get_figure_by_pos((1, col)) is not None:
                        return False
                if self.is_king_in_check_now(king.color):
                    return False
                king.position = (1, 4)
                if self.is_king_in_check_now(king.color):
                    king.position = (1, 5)
                    return False
                king.position = (1, 3)
                if self.is_king_in_check_now(king.color):
                    king.position = (1, 5)
                    return False
                king.position = (1, 5)
            else:
                return False
        else:
            if target[1] == 7 and self.black_short_castle:
                figure = self.get_figure_by_pos((8, 8))
                if figure is None or figure.name != Name.Rook or figure.color == Color.White:
                    return False
                if self.get_figure_by_pos((8, 6)) is not None or self.get_figure_by_pos((8, 7)) is not None:
                    return False
                if self.is_king_in_check_now(king.color):
                    return False
                king.position = (8, 6)
                if self.is_king_in_check_now(king.color):
                    king.position = (8, 5)
                    return False
                king.position = (8, 7)
                if self.is_king_in_check_now(king.color):
                    king.position = (8, 5)
                    return False
                king.position = (8, 5)
            elif target[1] == 3 and self.black_long_castle:
                figure = self.get_figure_by_pos((8, 1))
                if figure is None or figure.name != Name.Rook or figure.color == Color.White:
                    return False
                for col in range(2, 5):
                    if self.get_figure_by_pos((8, col)) is not None:
                        return False
                if self.is_king_in_check_now(king.color):
                    return False
                king.position = (8, 4)
                if self.is_king_in_check_now(king.color):
                    king.position = (8, 5)
                    return False
                king.position = (8, 3)
                if self.is_king_in_check_now(king.color):
                    king.position = (8, 5)
                    return False
                king.position = (8, 5)
            else:
                return False
        return True

    def is_en_passant(self, pawn, target):
        if pawn.name != Name.Pawn:
            return False
        if len(self.moves) == 0:
            return False
        if self.last_move.color != other_color(pawn.color):
            return False
        if self.last_move.piece != Name.Pawn:
            return False
        if pawn.position[0] != self.last_move.target[0]:
            return False
        if target[1] != self.last_move.target[1]:
            return False
        if self.last_move.start[0] == 2 and self.last_move.target[0] == 4:
            if target[0] != 3:
                return False
        if self.last_move.start[0] == 7 and self.last_move.target[0] == 5:
            if target[0] != 6:
                return False
        return True

    def is_king_in_check_now(self, color):
        king = self.get_figures_by_name(Name.King, color)[0]
        for fig in list(self.in_play):
            if fig.color == color:
                continue
            if self.is_move_possible(fig, king.position, check_flag=False):
                return True
        return False

    def is_king_in_check_after(self, figure, target,  *, color=None, promo_piece=None):
        if color is None:
            color = figure.color

        if self.is_en_passant(figure, target):
            removed_piece = self.get_figure_by_pos(self.last_move.target)
        else:
            removed_piece = self.get_figure_by_pos(target)

        if removed_piece:
            self.remove_from_play(removed_piece)

        starting_position = figure.position
        castling = self.is_castling_legal(figure, target)

        if castling:
            if figure.color == Color.White:
                row = 1
            else:
                row = 8
            if target[1] == 7:
                rook = self.get_figure_by_pos((row, 8))
                rook_starting = rook.position
                self.move_figure_to(rook, (row, 6))
            elif target[1] == 3:
                rook = self.get_figure_by_pos((row, 1))
                rook_starting = rook.position
                self.move_figure_to(rook, (row, 4))
            self.move_figure_to(figure, target, promo_piece=promo_piece)
        else:
            self.move_figure_to(figure, target, promo_piece=promo_piece)

        answer = self.is_king_in_check_now(color)

        if promo_piece is not None:
            self.undo_promotion(figure)

        if removed_piece:
            self.in_play.add(removed_piece)
            self.captured.remove(removed_piece)

        figure.position = starting_position

        if castling:
            rook.position = rook_starting
        return answer

    def figure_legal_moves(self, figure):
        moves = []
        pos_white = set()
        pos_black = set()

        for fig in self.in_play:
            if fig.color == Color.White:
                pos_white.add(fig.position)
            else:
                pos_black.add(fig.position)

        if figure.name == Name.Pawn:
            for dx, dy in figure.possible_moves:
                target = (figure.position[0] + dx, figure.position[1] + dy)
                if target[0] not in range(1, 9) or target[1] not in range(1, 9):
                    continue
                if dx in {-2, 2}:
                    if figure.color == Color.White and figure.position[0] != 2:
                        continue
                    if figure.color == Color.Black and figure.position[0] != 7:
                        continue
                    blockade = (figure.position[0] + dx // 2, figure.position[1])
                    if blockade in pos_black or blockade in pos_white:
                        continue
                    if target in pos_black or target in pos_white:
                        continue
                elif dy != 0 and not self.is_en_passant(figure, target):
                    if figure.color == Color.White and target not in pos_black:
                        continue
                    if figure.color == Color.Black and target not in pos_white:
                        continue
                else:
                    if target in pos_black or target in pos_white:
                        continue
                if not self.is_king_in_check_after(figure, target):
                    move = self.get_move(figure, target)
                    notation_info = self.get_info(figure, target)
                    moves.append((move, notation_info))
        elif figure.name == Name.King or figure.name == Name.Knight:
            for dx, dy in figure.possible_moves:
                target = (figure.position[0] + dx, figure.position[1] + dy)
                if target[0] not in range(1, 9) or target[1] not in range(1, 9):
                    continue
                if figure.color == Color.White and target in pos_white:
                    continue
                if figure.color == Color.Black and target in pos_black:
                    continue
                if not self.is_king_in_check_after(figure, target):
                    move = self.get_move(figure, target)
                    notation_info = self.get_info(figure, target)
                    moves.append((move, notation_info))
            if figure.name == Name.King:
                for dy in {-2, 2}:
                    target = (figure.position[0], figure.position[1] + dy)
                    if self.is_castling_legal(figure, target): # add a flag to not call is_castling_legal?
                        move = self.get_move(figure, target)
                        notation_info = self.get_info(figure, target)
                        moves.append((move, notation_info))
        else:
            seen = [False] * 8
            if figure.name == Name.Rook:
                for i in {0, 2, 5, 7}:
                    seen[i] = True
            elif figure.name == Name.Bishop:
                for i in {1, 3, 4, 6}:
                    seen[i] = True

            for r in range(1, 8):
                if all(seen):
                    break
                for idx, (dx, dy) in enumerate(DIRECTIONS):
                    if seen[idx]:
                        continue
                    target = (figure.position[0] + r * dx, figure.position[1] + r * dy)
                    if target[0] not in range(1, 9) or target[1] not in range(1, 9):
                        seen[idx] = True
                        continue
                    if figure.color == Color.White:
                        if target in pos_white:
                            seen[idx] = True
                            continue
                        elif target in pos_black:
                            seen[idx] = True
                    else:
                        if target in pos_black:
                            seen[idx] = True
                            continue
                        elif target in pos_white:
                            seen[idx] = True
                    if not self.is_king_in_check_after(figure, target):
                        move = self.get_move(figure, target)
                        notation_info = self.get_info(figure, target)
                        moves.append((move, notation_info))

        return moves

    def all_legal_moves(self, color):
        moves = []
        for figure in list(self.in_play):
            if figure.color != color:
                continue
            for bundle in self.figure_legal_moves(figure):
                moves.append(bundle)
        return moves

    def all_legal_moves_after(self, figure, target, *, color=None, promo_piece=None):
        if color is None:
            color = other_color(figure.color)

        if self.is_en_passant(figure, target):
            removed_piece = self.get_figure_by_pos(self.last_move.target)
        else:
            removed_piece = self.get_figure_by_pos(target)

        if removed_piece:
            self.remove_from_play(removed_piece)
        starting_position = figure.position
        self.move_figure_to(figure, target, promo_piece=promo_piece)

        castling = self.is_castling_legal(figure, target)
        if castling:
            if figure.color == Color.White:
                row = 1
            else:
                row = 8
            if target[1] == 7:
                rook = self.get_figure_by_pos((row, 8))
                rook_starting = rook.position
                self.move_figure_to(rook, (row, 6))
            elif target[1] == 3:
                rook = self.get_figure_by_pos((row, 1))
                rook_starting = rook.position
                self.move_figure_to(rook, (row, 4))
            castling = True

        moves = self.all_legal_moves(color)

        if promo_piece is not None:
            self.undo_promotion(figure)

        if removed_piece:
            self.in_play.add(removed_piece)
            self.captured.remove(removed_piece)

        figure.position = starting_position

        if castling:
            rook.position = rook_starting
        return moves

    def make_move_from_notation(self, notation, color):
        if (match := parse_notation(notation)) is None:
            raise ValueError('Wrong notation')

        if match.group('castling'):
            figure = self.get_figures_by_name(Name.King, color)[0]
            if match.group('long_castle'):
                if color == Color.White:
                    target = (1, 3)
                else:
                    target = (8, 3)
            else:
                if color == Color.White:
                    target = (1, 7)
                else:
                    target = (8, 7)

            if not self.is_legal(figure, target):
                raise ValueError('Illegal move')

            move = self.get_move(figure, target)
            notation_info = self.get_info(figure, target)

            self.move_figure_to(figure, target)
            self.moves.append((move, notation_info))

            if figure.color == Color.White:
                row = 1
                self.white_short_castle = False
                self.white_long_castle = False
            else:
                row = 8
                self.black_short_castle = False
                self.black_long_castle = False
            if move.target[1] == 7:
                rook = self.get_figure_by_pos((row, 8))
                self.move_figure_to(rook, (row, 6))
            elif move.target[1] == 3:
                rook = self.get_figure_by_pos((row, 1))
                self.move_figure_to(rook, (row, 4))

            return None

        if not (notation_name := match.group('name')):
            name = Name.Pawn
        elif notation_name in ALGEBRAIC_NAMES:
            name = FROM_ALGEBRAIC[notation_name]
        else:
            name, fig_color = FROM_FIGURINE[notation_name]
            if fig_color != color:
                raise ValueError('Bad input - piece color and input color are different')

        figures = self.get_figures_by_name(name, color)
        target = square_to_pos(match.group('target'))

        rank = None
        if (notation_rank := match.group('rank')):
            rank = int(notation_rank)
        file = match.group('file')

        promo_piece = None
        if (notation_promo_piece := match.group('promo_piece')):
            if notation_promo_piece in ALGEBRAIC_NAMES:
                promo_piece = FROM_ALGEBRAIC[notation_promo_piece]
            else:
                promo_piece, _ = FROM_FIGURINE[notation_promo_piece]

        possible_figures = []
        for fig in figures:
            if not self.is_legal(fig, target):
                continue
            if rank and fig.rank != rank:
                continue
            if file and fig.file != file:
                continue
            possible_figures.append(fig)

        if len(possible_figures) == 0:
            raise ValueError('Illegal move')
        elif len(possible_figures) >= 2:
            raise ValueError('Not enough info')

        figure = possible_figures[0]

        move = self.get_move(figure, target, promo_piece=promo_piece)
        notation_info = self.get_info(figure, target, promo_piece=promo_piece)

        self.move_figure_to(figure, target, promo_piece=promo_piece)
        self.moves.append((move, notation_info))

        if figure.name == Name.King:
            if figure.color == Color.White:
                self.white_short_castle = False
                self.white_long_castle = False
            else:
                self.black_short_castle = False
                self.black_long_castle = False

        if figure is self.white_short_rook:
            self.white_short_castle = False

        elif figure is self.white_long_rook:
            self.white_long_castle = False

        elif figure is self.black_short_rook:
            self.black_short_castle = False

        elif figure is self.black_long_rook:
            self.black_long_castle = False