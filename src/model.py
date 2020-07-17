from enum import Enum, auto
from random import choice
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

    def is_legal(self, figure, target):
        return self.is_move_possible(figure, target) and not self.is_king_in_check_after(figure, target)

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

    def move_figure_to(self, figure, target):
        for fig in self.in_play:
            if fig.position == target:
                self.remove_from_play(fig)
                break
        figure.position = target
        self.update_positions()


    @staticmethod
    def to_figurine_notation(figure, target, *, captures=False, check=False, mate=False, file=False, rank=False):
        out = ''
        if figure.name != Name.Pawn:
            out += figure.as_piece()
        if file:
            out += figure.file
        if rank:
            out += figure.rank
        if captures:
            out += 'x'
        out += 'abcdefgh'[target[1] - 1] + str(target[0])
        if check:
            out += '+'
        if mate:
            out += '#'
        return out

    def print_state(self):
        board = [['-'] * 8 for _ in range(8)]
        for fig in self.in_play:
            row, col = fig.position
            board[row-1][col-1] = fig.as_piece()
        for row in reversed(board):
            print(''.join(row))

    def all_legal_moves(self, color):
        moves = set()
        for row in range(1, 9):
            for col in range(1, 9):
                for fig in game.in_play:
                    if fig.color == color and game.is_legal(fig, (row, col)):
                        moves.add((fig, (row, col)))
        return moves

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


game = Game()

color = Color.White
for asdf in range(50):
    all_legal_moves = list(game.all_legal_moves(color))
    random_move = choice(all_legal_moves)

    game.move_figure_to(*random_move)
    print(game.to_figurine_notation(*random_move))
    print([game.to_figurine_notation(*move) for move in all_legal_moves])
    game.print_state()
    print()

    if color == Color.White:
        color = Color.Black
    else:
        color = Color.White