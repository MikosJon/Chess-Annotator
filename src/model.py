NAMES = {'king': 'K', 'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'N', 'pawn': 'P'}

KING_MOVES       = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROOK_MOVES       = [(0, x) for x in range(-7, 8) if x != 0] + [(x, 0) for x in range(-7, 8) if x != 0]
BISHOP_MOVES     = [(x, x) for x in range(-7, 8) if x != 0] + [(x, -x) for x in range(-7, 8) if x != 0]
QUEEN_MOVES      = ROOK_MOVES + BISHOP_MOVES
KNIGHT_MOVES     = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
WHITE_PAWN_MOVES = [(1, -1), (1, 0), (2, 0), (1, 1)]
BLACK_PAWN_MOVES = [(-1, -1), (-1, 0), (-2, 0), (-1, 1)]

class Figure:
    def __init__(self, name, moves, pos, color):
        self.name = name
        self.moves = moves
        self.pos = pos
        self.color = color

game = []   # will make it a Game object later

game.append(Figure(NAMES['king']  , KING_MOVES  , (1, 5), 'W'))   # white king
game.append(Figure(NAMES['queen'] , QUEEN_MOVES , (1, 4), 'W'))   # white queen
game.append(Figure(NAMES['rook']  , ROOK_MOVES  , (1, 1), 'W'))   # white rook on a1
game.append(Figure(NAMES['rook']  , ROOK_MOVES  , (1, 8), 'W'))   # white rook on h1
game.append(Figure(NAMES['bishop'], BISHOP_MOVES, (1, 3), 'W'))   # white dark-squared bishop
game.append(Figure(NAMES['bishop'], BISHOP_MOVES, (1, 6), 'W'))   # white light-squared bishop
game.append(Figure(NAMES['knight'], KNIGHT_MOVES, (1, 2), 'W'))   # white knight on b1
game.append(Figure(NAMES['knight'], KNIGHT_MOVES, (1, 7), 'W'))   # white knight on g1
for i in range(1, 9):
    game.append(Figure(NAMES['pawn'], WHITE_PAWN_MOVES, (2, i), 'W'))   # white pawns

game.append(Figure(NAMES['king']  , KING_MOVES  , (8, 5), 'B'))   # black king
game.append(Figure(NAMES['queen'] , QUEEN_MOVES , (8, 4), 'B'))   # black queen
game.append(Figure(NAMES['rook']  , ROOK_MOVES  , (8, 1), 'B'))   # black rook on a8
game.append(Figure(NAMES['rook']  , ROOK_MOVES  , (8, 8), 'B'))   # black rook on h8
game.append(Figure(NAMES['bishop'], BISHOP_MOVES, (8, 3), 'B'))   # black light-squared bishop
game.append(Figure(NAMES['bishop'], BISHOP_MOVES, (8, 6), 'B'))   # black dark-squared bishop
game.append(Figure(NAMES['knight'], KNIGHT_MOVES, (8, 2), 'B'))   # black knight on b8
game.append(Figure(NAMES['knight'], KNIGHT_MOVES, (8, 7), 'B'))   # black knight on g8
for i in range(1, 9):
    game.append(Figure(NAMES['pawn'], BLACK_PAWN_MOVES, (7, i), 'B'))   # black pawns

# simple visualization
board = [[' '] * 8 for _ in range(8)]
for figure in game:
    row, col = figure.pos
    board[row-1][col-1] = figure.name

for row in board:
    print(''.join(row))