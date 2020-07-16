from enum import Enum, auto

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
    Name.King: '♔', Name.Queen: '♕', Name.Rook: '♖', Name.Bishop: '♗', Name.Knight: '♘', Name.Pawn: '♙'
}
TO_BLACK_PIECE = {
    Name.King: '♚', Name.Queen: '♛', Name.Rook: '♜', Name.Bishop: '♝', Name.Knight: '♞', Name.Pawn: '♟︎'
}

class Figure:
    def __init__(self, name, color, position, possible_moves):
        self.name = name
        self.color = color
        self.position = position
        self.possible_moves = possible_moves

    def as_piece(self):
        if self.color == Color.White:
            return TO_WHITE_PIECE[self.name]
        else:
            return TO_BLACK_PIECE[self.name]

    def as_name(self):
        return self.color.name + ' ' + self.name.name
class Game:
    def __init__(self):
        self.in_play = []
        self.captured = []
        self.pos_white = []
        self.pos_black = []

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
        self.in_play.append(figure)
        if figure.color == Color.White:
            self.pos_white.append(figure.position)
        else:
            self.pos_black.append(figure.position)

    def is_legal(self, figure, target):
        move = (target[0] - figure.position[0], target[1] - figure.position[1])
        move_size = max(abs(move[0]), abs(move[1]))
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
            if move_size == 2:
                if figure.color == Color.White and curr_position[0] != 2:
                    return False
                if figure == Color.Black and curr_position[0] != 7:
                    return False
            if move[0] != 0 and move[1] != 0:
                if figure.color == Color.White and target not in self.pos_black:
                    return False
                if figure.color == Color.Black and target not in self.pos_white:
                    return False

        for i in range(1, move_size):
            test_position = (curr_position[0] + i * dx, curr_position[1] + i * dy)
            if test_position in self.pos_white or test_position in self.pos_black:
                return False

        return True

game = Game()

# simple visualization
board = [[' '] * 8 for _ in range(8)]
for figure in game.in_play:
    row, col = figure.position
    board[row-1][col-1] = figure.as_piece()

for row in board:
    print(''.join(row))

# show all legal starting moves
for row in range(1, 9):
    for col in range(1, 9):
        for fig in game.in_play:
            if game.is_legal(fig, (row, col)):
                print(fig.as_name(), (row, col))