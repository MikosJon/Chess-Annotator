from enum import Enum, auto
from dataclasses import dataclass
from random import choice

@dataclass
class MoveInfo:
    captures = False
    check = False
    mate = False
    file = False
    unique = True
    rank = False
    promotion = False

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
        self.update_positions()

    def remove_from_play(self, figure):
        self.in_play.remove(figure)
        self.update_positions()
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

    def update_positions(self):
        new_white = set()
        new_black = set()
        for figure in self.in_play:
            if figure.color == Color.White:
                new_white.add(figure.position)
            else:
                new_black.add(figure.position)
        self.pos_white = new_white
        self.pos_black = new_black

    def get_info(self, figure, target):
        move_info = MoveInfo()
        move_info.check = self.is_king_in_check_after(figure, target, color=other_color(figure.color))
        if move_info.check:
            if len(self.all_legal_moves_after(figure, target, color=other_color(figure.color))) == 0:
                move_info.mate = True

        same_pieces = self.get_figures_by_name(figure.name, figure.color)
        same_pieces.remove(figure)
        if same_pieces:
            for fig in same_pieces:
                if self.is_legal(fig, target):
                    move_info.unique = False
                    if fig.rank == figure.rank:
                        move_info.rank = True
                    if fig.file == figure.file:
                        move_info.file = True

        if self.get_figure_by_pos(target) is not None:
            move_info.captures = True
        return move_info

    def move_figure_to(self, figure, target, *, return_notation=False):
        if return_notation:
            info = self.get_info(figure, target)
            notation = game.to_figurine_notation(figure, target, info)

        captured_figure = self.get_figure_by_pos(target)
        if captured_figure:
            self.remove_from_play(captured_figure)

        figure.position = target
        self.update_positions()

        if return_notation:
            return notation
        return None

    def is_legal(self, figure, target):
        return self.is_move_possible(figure, target) and not self.is_king_in_check_after(figure, target)

    def is_move_possible(self, figure, target):
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
                if figure == Color.Black and curr_position[0] != 7:
                    return False
            if move[0] != 0 and move[1] != 0:
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

    def is_king_in_check_now(self, color):
        king = self.get_figures_by_name(Name.King, color)[0]
        for fig in self.in_play:
            if fig.color == color:
                continue
            if self.is_move_possible(fig, king.position):
                return True
        return False

    def is_king_in_check_after(self, figure, target,  *, color=None):
        if color is None:
            color = figure.color

        king = self.get_figures_by_name(Name.King, color)[0]
        removed_piece = self.get_figure_by_pos(target)

        if removed_piece:
            self.remove_from_play(removed_piece)
        starting_position = figure.position
        self.move_figure_to(figure, target)

        answer = self.is_king_in_check_now(color)

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
                if self.is_legal(figure, target):
                    info = self.get_info(figure, target)
                    moves.append((figure, target, info))
        return moves

    def all_legal_moves_after(self, figure, target, *, color=None):
        if color is None:
            color = other_color(figure.color)

        removed_piece = self.get_figure_by_pos(target)
        if removed_piece:
            self.remove_from_play(removed_piece)
        starting_position = figure.position
        self.move_figure_to(figure, target)

        moves = self.all_legal_moves(color)

        if removed_piece:
            self.add_figure(removed_piece)
            self.captured.remove(removed_piece)
        self.move_figure_to(figure, starting_position)
        return moves

    def deconstruct_notation(self, notation, color=None):
        notation.remove('+')
        notation.remove('#')
        target = square_to_pos(notation[-2:])

        if notation[0].isascii():
            if color is None:
                print('Missing color')
                return None

            if notation[0] not in 'KQRBN':
                piece = Name.Pawn
                info = notation[:-2]
            else:
                piece = FROM_ALGEBRAIC[notation[0]]
                info = notation[1:-2]

            return piece, color, target, info

        else:
            piece, color = FROM_FIGURINE[notation[0]]
            if piece == Name.Pawn:
                info = notation[:-2]
            else:
                info = notation[1:-2]

            return piece, color, target, info

    def make_move_from_notation(self, notation, color=None):
        piece, color, target, info = self.deconstruct_notation(notation, color)

        figures = self.get_figures_by_name(piece, color)
        possible_figures = []

        if len(figures) == 1:
            figure = figures[0]

            if not self.is_legal(figure, target):
                print('Illegal move')
                return None

            self.move_figure_to(figure, target)
        else:
            for figure in figures:
                if not self.is_legal(figure, target):
                    continue
                if len(info) != 0:
                    if info[0] in 'abcdefgh' and figure.file != info[0]:
                        continue
                    if info[-1] in range(1, 9) and figure.rank != info[-1]:
                        continue
                possible_figures.append(figure)
            if len(possible_figures) == 0:
                print('Illegal move')
            elif len(possible_figures) >= 2:
                print('Not enough info')
            else:
                self.move_figure_to(possible_figures[0], target)

    @staticmethod
    def to_figurine_notation(figure, target, info):
        out = ''
        if figure.name == Name.Pawn:
            if info.captures:
                out += figure.file
                out += 'x'
        else:
            out += figure.as_piece()
            if not info.unique:
                if not info.file:
                    out += figure.file
                elif not info.rank:
                    out += str(figure.rank)
                else:
                    out += figure.file + str(figure.rank)
            if info.captures:
                out += 'x'

        out += 'abcdefgh'[target[1] - 1] + str(target[0])
        if info.check and not info.mate:
            out += '+'
        if info.mate:
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
for asdf in range(50):
    all_legal_moves = game.all_legal_moves(color)
    figure, target, info = choice(all_legal_moves)

    notation = game.move_figure_to(figure, target, return_notation=True)
    print(notation)
    print('Vse možne poteze:', ' '.join(sorted([game.to_figurine_notation(*move) for move in all_legal_moves])))
    game.print_state()
    print()

    color = other_color(color)