from enum import Enum, auto
from dataclasses import dataclass
from random import choice

@dataclass
class MoveInfo:
    captures = False
    check = False
    mate = False
    unique = True
    file = False
    rank = False
    promotion = None

@dataclass
class Move:
    piece = None
    color = None
    start = None
    target = None
    position_info = None
    promo_piece = None
    en_passant = False

class Name(Enum):
    King = auto()
    Queen = auto()
    Rook = auto()
    Bishop = auto()
    Knight = auto()
    Pawn = auto()

class Color(Enum):
    White = auto()
    Black = auto()

def other_color(color):
    if color == Color.White:
        return Color.Black
    return Color.White

def pos_to_square(position):
    row, col = position
    return 'abcdefgh'[col - 1] + str(row)

def square_to_pos(square):
    return (int(square[-1]), 'abcdefgh'.index(square[-2]) + 1)

KING_MOVES       = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROOK_MOVES       = [(0, x) for x in range(-7, 8) if x != 0] + [(x, 0) for x in range(-7, 8) if x != 0]
BISHOP_MOVES     = [(x, x) for x in range(-7, 8) if x != 0] + [(x, -x) for x in range(-7, 8) if x != 0]
QUEEN_MOVES      = ROOK_MOVES + BISHOP_MOVES
KNIGHT_MOVES     = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
WHITE_PAWN_MOVES = [(1, -1), (1, 0), (2, 0), (1, 1)]
BLACK_PAWN_MOVES = [(-1, -1), (-1, 0), (-2, 0), (-1, 1)]

PROMOTION_MOVES = {
    Name.Queen:  QUEEN_MOVES,
    Name.Rook:   ROOK_MOVES,
    Name.Bishop: BISHOP_MOVES,
    Name.Knight: KNIGHT_MOVES
}
PROMOTION_PIECES = {Name.Queen, Name.Rook, Name.Bishop, Name.Knight}

FROM_FIGURINE = {
    '\u2654': (Name.King, Color.White),
    '\u2655': (Name.Queen, Color.White),
    '\u2656': (Name.Rook, Color.White),
    '\u2657': (Name.Bishop, Color.White),
    '\u2658': (Name.Knight, Color.White),
    '\u2659': (Name.Pawn, Color.White),

    '\u265A': (Name.King, Color.Black),
    '\u265B': (Name.Queen, Color.Black),
    '\u265C': (Name.Rook, Color.Black),
    '\u265D': (Name.Bishop, Color.Black),
    '\u265E': (Name.Knight, Color.Black),
    '\u265F': (Name.Pawn, Color.Black)
}
TO_WHITE_PIECE = {
    Name.King:   '\u2654',
    Name.Queen:  '\u2655',
    Name.Rook:   '\u2656',
    Name.Bishop: '\u2657',
    Name.Knight: '\u2658',
    Name.Pawn:   '\u2659',
}
TO_BLACK_PIECE = {
    Name.King:   '\u265A',
    Name.Queen:  '\u265B',
    Name.Rook:   '\u265C',
    Name.Bishop: '\u265D',
    Name.Knight: '\u265E',
    Name.Pawn:   '\u265F',
}

FROM_ALGEBRAIC = {
    'K': Name.King,
    'Q': Name.Queen,
    'R': Name.Rook,
    'B': Name.Bishop,
    'N': Name.Knight
}
TO_ALGEBRAIC = {
    Name.King:   'K',
    Name.Queen:  'Q',
    Name.Rook:   'R',
    Name.Bishop: 'B',
    Name.Knight: 'N'
}
ALGEBRAIC_NAMES = {'K', 'Q', 'R', 'B', 'N'}

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
        self.pos_white = set()
        self.pos_black = set()
        self.promoted_pawns = set()

        self.last_move = Move()

        self.add_figure(Figure(Name.King  , Color.White, (1, 5), KING_MOVES))
        self.add_figure(Figure(Name.Queen , Color.White, (1, 4), QUEEN_MOVES))
        self.add_figure(Figure(Name.Rook  , Color.White, (1, 1), ROOK_MOVES))
        self.add_figure(Figure(Name.Rook  , Color.White, (1, 8), ROOK_MOVES))
        self.add_figure(Figure(Name.Bishop, Color.White, (1, 3), BISHOP_MOVES))
        self.add_figure(Figure(Name.Bishop, Color.White, (1, 6), BISHOP_MOVES))
        self.add_figure(Figure(Name.Knight, Color.White, (1, 2), KNIGHT_MOVES))
        self.add_figure(Figure(Name.Knight, Color.White, (1, 7), KNIGHT_MOVES))
        for i in range(1, 9):
            self.add_figure(Figure(Name.Pawn, Color.White, (2, i), WHITE_PAWN_MOVES))

        self.add_figure(Figure(Name.King  , Color.Black, (8, 5), KING_MOVES))
        self.add_figure(Figure(Name.Queen , Color.Black, (8, 4), QUEEN_MOVES))
        self.add_figure(Figure(Name.Rook  , Color.Black, (8, 1), ROOK_MOVES))
        self.add_figure(Figure(Name.Rook  , Color.Black, (8, 8), ROOK_MOVES))
        self.add_figure(Figure(Name.Bishop, Color.Black, (8, 3), BISHOP_MOVES))
        self.add_figure(Figure(Name.Bishop, Color.Black, (8, 6), BISHOP_MOVES))
        self.add_figure(Figure(Name.Knight, Color.Black, (8, 2), KNIGHT_MOVES))
        self.add_figure(Figure(Name.Knight, Color.Black, (8, 7), KNIGHT_MOVES))
        for i in range(1, 9):
            self.add_figure(Figure(Name.Pawn, Color.Black, (7, i), BLACK_PAWN_MOVES))

    def add_figure(self, figure):
        self.in_play.add(figure)
        if figure.color == Color.White:
            self.pos_white.add(figure.position)
        else:
            self.pos_black.add(figure.position)

    def remove_from_play(self, figure):
        self.in_play.remove(figure)
        self.captured.add(figure)
        if figure.color == Color.White:
            self.pos_white.remove(figure.position)
        else:
            self.pos_black.remove(figure.position)

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
        self.add_figure(Figure(piece, pawn.color, pawn.position, PROMOTION_MOVES[piece]))

    def undo_promotion(self, pawn):
        promoted_piece = self.get_figure_by_pos(pawn.position)
        self.in_play.remove(promoted_piece)
        self.add_figure(pawn)

    def get_info(self, figure, target, *, promo_piece=None):
        move_info = MoveInfo()
        move_info.promotion = promo_piece

        opponent = other_color(figure.color)
        move_info.check = self.is_king_in_check_after(figure, target, color=opponent, promo_piece=promo_piece)
        if move_info.check:
            if len(self.all_legal_moves_after(figure, target, color=opponent, promo_piece=promo_piece)) == 0:
                move_info.mate = True

        same_pieces = self.get_figures_by_name(figure.name, figure.color)
        same_pieces.remove(figure)
        if same_pieces:
            for fig in same_pieces:
                if self.is_legal(fig, target, promo_piece=promo_piece):
                    move_info.unique = False
                    if fig.rank == figure.rank:
                        move_info.rank = True
                    if fig.file == figure.file:
                        move_info.file = True

        if self.get_figure_by_pos(target) is not None:
            move_info.captures = True
        elif self.is_en_passant(figure, target):
            move_info.captures = True
        return move_info

    def move_figure_to(self, figure, target, *, return_notation=False, promo_piece=None):
        if return_notation:
            move_info = self.get_info(figure, target, promo_piece=promo_piece)
            notation = Game.to_figurine_notation(figure, target, move_info)

        if self.last_move.en_passant:
            row = self.last_move.start[0]
            col = target[1]
            captured_figure = self.get_figure_by_pos((row, col))
        else:
            captured_figure = self.get_figure_by_pos(target)

        if captured_figure:
            self.remove_from_play(captured_figure)

        if figure.color == Color.White:
            self.pos_white.remove(figure.position)
            self.pos_white.add(target)
        else:
            self.pos_black.remove(figure.position)
            self.pos_black.add(target)

        figure.position = target

        if figure.name == Name.Pawn and target[0] in {1, 8}:
            if promo_piece is not None:
                self.promote_pawn(figure, promo_piece)

        if return_notation:
            return notation

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

        if figure.color == Color.White and target in self.pos_white:
            return False
        if figure.color == Color.Black and target in self.pos_black:
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
                if figure.color == Color.White and target not in self.pos_black:
                    return False
                if figure.color == Color.Black and target not in self.pos_white:
                    return False
            else:
                if target in self.pos_black or target in self.pos_white:
                    return False

        for i in range(1, number_of_moved_squares):
            test_position = (curr_position[0] + i * dx, curr_position[1] + i * dy)
            if test_position in self.pos_white or test_position in self.pos_black:
                return False

        return True

    def is_en_passant(self, figure, target):
        if self.last_move.color != other_color(figure.color):
            return False
        if self.last_move.piece != Name.Pawn:
            return False
        if self.last_move.start[0] not in {2, 7} or self.last_move.target[0] not in {4, 5}:
            return False
        if figure.position[0] != self.last_move.target[0]:
            return False
        if target[1] != self.last_move.target[1]:
            return False
        return True

    def is_king_in_check_now(self, color):
        king = self.get_figures_by_name(Name.King, color)[0]
        for fig in self.in_play:
            if fig.color == color:
                continue
            if self.is_move_possible(fig, king.position, check_flag=False):
                return True
        return False

    def is_king_in_check_after(self, figure, target,  *, color=None, promo_piece=None):
        if color is None:
            color = figure.color

        if self.is_en_passant(figure, target):
            row = self.last_move.start[0]
            col = target[1]
            removed_piece = self.get_figure_by_pos((row, col))
        else:
            removed_piece = self.get_figure_by_pos(target)

        if removed_piece:
            self.remove_from_play(removed_piece)
        starting_position = figure.position
        self.move_figure_to(figure, target, promo_piece=promo_piece)

        answer = self.is_king_in_check_now(color)

        if promo_piece is not None:
            self.undo_promotion(figure)

        if removed_piece:
            self.add_figure(removed_piece)
            self.captured.remove(removed_piece)

        self.move_figure_to(figure, starting_position)
        return answer

    def all_legal_moves(self, color):
        moves = []
        for figure in self.in_play:
            if figure.color != color:
                continue
            for dx, dy in figure.possible_moves:
                target = (figure.position[0] + dx, figure.position[1] + dy)
                if not self.is_legal(figure, target):
                    continue

                if figure.name == Name.Pawn and target[0] in {1,8}:
                    for piece in PROMOTION_PIECES:
                        move_info = self.get_info(figure, target, promo_piece=piece)
                        moves.append((figure, target, move_info))
                else:
                    move_info = self.get_info(figure, target)
                    moves.append((figure, target, move_info))
        return moves

    def all_legal_moves_after(self, figure, target, *, color=None, promo_piece=None):
        if color is None:
            color = other_color(figure.color)

        if self.is_en_passant(figure, target):
            row = self.last_move.start[0]
            col = target[1]
            removed_piece = self.get_figure_by_pos((row, col))
        else:
            removed_piece = self.get_figure_by_pos(target)

        if removed_piece:
            self.remove_from_play(removed_piece)
        starting_position = figure.position
        self.move_figure_to(figure, target, promo_piece=promo_piece)

        moves = self.all_legal_moves(color)

        if promo_piece is not None:
            self.undo_promotion(figure)

        if removed_piece:
            self.add_figure(removed_piece)
            self.captured.remove(removed_piece)

        self.move_figure_to(figure, starting_position)
        return moves

    @staticmethod
    def deconstruct_notation(notation, color=None):
        move = Move()
        notation.replace('+', '')
        notation.replace('#', '')

        if '=' in notation:
            promo_notation = notation[-1]
            notation = notation[:-2]
        else:
            promo_notation = None

        move.target = square_to_pos(notation[-2:])

        if notation[0].isascii():
            if color is None:
                raise ValueError('Missing color!')
            move.color = color

            if promo_notation:
                move.promo_piece = FROM_ALGEBRAIC[promo_notation]
            else:
                move.promo_piece = None

            if notation[0] not in ALGEBRAIC_NAMES:
                move.piece = Name.Pawn
                move.position_info = notation[:-2]

            else:
                move.piece = FROM_ALGEBRAIC[notation[0]]
                move.position_info = notation[1:-2]

        else:
            piece, color = FROM_FIGURINE[notation[0]]
            move.piece = piece
            move.color = color

            if promo_notation:
                move.promo_piece = FROM_FIGURINE[promo_notation]
            else:
                move.promo_piece = None

            if move.piece == Name.Pawn:
                move.position_info = notation[:-2]
            else:
                move.position_info = notation[1:-2]

        return move

    def make_move_from_notation(self, notation, color=None):
        move = Game.deconstruct_notation(notation, color)
        piece = move.piece
        color = move.color
        target = move.target
        position_info = move.position_info
        promo_piece = move.promo_piece

        figures = self.get_figures_by_name(piece, color)
        possible_figures = []

        if len(figures) == 1:
            figure = figures[0]

            if not self.is_legal(figure, target, promo_piece=promo_piece):
                raise ValueError('Illegal move')
            move.start = figure.position
            move.en_passant = self.is_en_passant(figure, target)
            self.last_move = move
            self.move_figure_to(figure, target, promo_piece=promo_piece)
        else:
            for figure in figures:
                if not self.is_legal(figure, target, promo_piece=promo_piece):
                    continue
                if len(position_info) != 0:
                    if position_info[0] in 'abcdefgh' and figure.file != position_info[0]:
                        continue
                    if position_info[-1] in range(1, 9) and figure.rank != position_info[-1]:
                        continue
                possible_figures.append(figure)
            if len(possible_figures) == 0:
                raise ValueError('Illegal move')
            elif len(possible_figures) >= 2:
                raise ValueError('Not enough info')
            else:
                figure = possible_figures[0]
                move.start = figure.position
                move.en_passant = self.is_en_passant(figure, target)
                self.last_move = move
                self.move_figure_to(figure, target, promo_piece=promo_piece)

    @staticmethod
    def to_figurine_notation(figure, target, move_info):
        out = ''
        if figure.name == Name.Pawn:
            if move_info.captures:
                out += figure.file
                out += 'x'
        else:
            out += figure.as_piece()
            if not move_info.unique:
                if not move_info.file:
                    out += figure.file
                elif not move_info.rank:
                    out += str(figure.rank)
                else:
                    out += figure.file + str(figure.rank)
            if move_info.captures:
                out += 'x'

        out += pos_to_square(target)

        if move_info.promotion is not None:
            out += '='
            if figure.color == Color.White:
                out += TO_WHITE_PIECE[move_info.promotion]
            else:
                out += TO_BLACK_PIECE[move_info.promotion]

        if move_info.check and not move_info.mate:
            out += '+'
        if move_info.mate:
            out += '#'

        return out

    def print_state(self):
        board = [['-'] * 8 for _ in range(8)]
        for fig in self.in_play:
            row, col = fig.position
            board[row-1][col-1] = fig.as_piece()
        for row in reversed(board):
            print(''.join(row))


game = Game()

color = Color.White
for asdf in range(200):
    all_legal_moves = game.all_legal_moves(color)
    legal_move_notations = ' '.join(sorted([game.to_figurine_notation(*move) for move in all_legal_moves]))

    figure, target, move_info = choice(all_legal_moves)
    notation = game.move_figure_to(figure, target, return_notation=True, promo_piece=move_info.promotion)

    print(notation)
    print('Vse možne poteze:', legal_move_notations)
    game.print_state()
    print()

    if '#' in notation:
        print('Game over!', color.name, 'wins!')
        break
    if len(legal_move_notations) == 0:
        print('Stalemate!')

    color = other_color(color)