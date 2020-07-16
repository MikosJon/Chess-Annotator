NAMES = {'king': 'K', 'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'N', 'pawn': 'P'}

KING_MOVES       = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROOK_MOVES       = [(0, x) for x in range(-7, 8) if x != 0] + [(x, 0) for x in range(-7, 8) if x != 0]
BISHOP_MOVES     = [(x, x) for x in range(-7, 8) if x != 0] + [(x, -x) for x in range(-7, 8) if x != 0]
QUEEN_MOVES      = ROOK_MOVES + BISHOP_MOVES
KNIGHT_MOVES     = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
WHITE_PAWN_MOVES = [(1, -1), (1, 0), (2, 0), (1, 1)]
BLACK_PAWN_MOVES = [(-1, -1), (-1, 0), (-2, 0), (-1, 1)]

class Figure:
    def __init__(self, name, possible_moves, position, color):
        self.name = name
        self.possible_moves = possible_moves
        self.position = position
        self.color = color

class Game:
    def __init__(self):
        self.in_play = []
        self.captured = []
        self.pos_white = []
        self.pos_black = []

        self.add_figure(Figure(NAMES['king']  , KING_MOVES  , (1, 5), 'W'))   # white king
        self.add_figure(Figure(NAMES['queen'] , QUEEN_MOVES , (1, 4), 'W'))   # white queen
        self.add_figure(Figure(NAMES['rook']  , ROOK_MOVES  , (1, 1), 'W'))   # white rook on a1
        self.add_figure(Figure(NAMES['rook']  , ROOK_MOVES  , (1, 8), 'W'))   # white rook on h1
        self.add_figure(Figure(NAMES['bishop'], BISHOP_MOVES, (1, 3), 'W'))   # white dark-squared bishop
        self.add_figure(Figure(NAMES['bishop'], BISHOP_MOVES, (1, 6), 'W'))   # white light-squared bishop
        self.add_figure(Figure(NAMES['knight'], KNIGHT_MOVES, (1, 2), 'W'))   # white knight on b1
        self.add_figure(Figure(NAMES['knight'], KNIGHT_MOVES, (1, 7), 'W'))   # white knight on g1
        for i in range(1, 9):
            self.add_figure(Figure(NAMES['pawn'], WHITE_PAWN_MOVES, (2, i), 'W'))   # white pawns

        self.add_figure(Figure(NAMES['king']  , KING_MOVES  , (8, 5), 'B'))   # black king
        self.add_figure(Figure(NAMES['queen'] , QUEEN_MOVES , (8, 4), 'B'))   # black queen
        self.add_figure(Figure(NAMES['rook']  , ROOK_MOVES  , (8, 1), 'B'))   # black rook on a8
        self.add_figure(Figure(NAMES['rook']  , ROOK_MOVES  , (8, 8), 'B'))   # black rook on h8
        self.add_figure(Figure(NAMES['bishop'], BISHOP_MOVES, (8, 3), 'B'))   # black light-squared bishop
        self.add_figure(Figure(NAMES['bishop'], BISHOP_MOVES, (8, 6), 'B'))   # black dark-squared bishop
        self.add_figure(Figure(NAMES['knight'], KNIGHT_MOVES, (8, 2), 'B'))   # black knight on b8
        self.add_figure(Figure(NAMES['knight'], KNIGHT_MOVES, (8, 7), 'B'))   # black knight on g8
        for i in range(1, 9):
            self.add_figure(Figure(NAMES['pawn'], BLACK_PAWN_MOVES, (7, i), 'B'))   # black pawns

    def add_figure(self, figure):
        self.in_play.append(figure)
        if figure.color == 'W':
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

        if figure.color == 'W' and target in self.pos_white:
            return False
        if figure.color == 'B' and target in self.pos_black:
            return False

        if figure.name == NAMES['knight']:
            return True

        if figure.name == NAMES['pawn']:
            if move_size == 2:
                if figure.color == 'W' and curr_position[0] != 2:
                    return False
                if figure == 'B' and curr_position[0] != 7:
                    return False
            if move[0] != 0 and move[1] != 0:
                if figure.color == 'W' and target not in self.pos_black:
                    return False
                if figure.color == 'B' and target not in self.pos_white:
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
    board[row-1][col-1] = figure.name

for row in board:
    print(''.join(row))

# show all legal starting moves
for row in range(1, 9):
    for col in range(1, 9):
        for fig in game.in_play:
            if game.is_legal(fig, (row, col)):
                print(fig.name, (row, col))