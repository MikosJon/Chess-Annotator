from enum import Enum, auto
from dataclasses import dataclass

@dataclass
class NotationInfo:
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
    promo_piece = None
    en_passant = False
    castling = False

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

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

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

def other_color(color):
    if color == Color.White:
        return Color.Black
    return Color.White

def pos_to_square(position):
    row, col = position
    return 'abcdefgh'[col - 1] + str(row)

def square_to_pos(square):
    return (int(square[-1]), 'abcdefgh'.index(square[-2]) + 1)

def to_figurine_notation(figure, target, notation_info):
    out = ''
    if figure.name == Name.Pawn:
        if notation_info.captures:
            out += figure.file
            out += 'x'
    elif figure.name == Name.King and abs(figure.position[1] - target[1]) == 2:
        if target[1] == 7:
            out += 'O-O'
        else:
            out += 'O-O-O'

        if notation_info.check and not notation_info.mate:
            out += '+'
        if notation_info.mate:
            out += '#'

        return out
    else:
        out += figure.as_piece()
        if not notation_info.unique:
            if not notation_info.file:
                out += figure.file
            elif not notation_info.rank:
                out += str(figure.rank)
            else:
                out += figure.file + str(figure.rank)
        if notation_info.captures:
            out += 'x'

    out += pos_to_square(target)

    if notation_info.promotion is not None:
        out += '='
        if figure.color == Color.White:
            out += TO_WHITE_PIECE[notation_info.promotion]
        else:
            out += TO_BLACK_PIECE[notation_info.promotion]

    if notation_info.check and not notation_info.mate:
        out += '+'
    if notation_info.mate:
        out += '#'

    return out
