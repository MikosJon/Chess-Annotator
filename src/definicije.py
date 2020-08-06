from enum import Enum, auto
from dataclasses import dataclass
import re

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
    captured = None

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

class GameState(Enum):
    Normal = auto()
    Draw = auto()
    White = auto()
    Black = auto()

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

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

KING_MOVES       = {(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)}
ROOK_MOVES       = {(0, x) for x in range(-7, 8) if x != 0} | {(x, 0) for x in range(-7, 8) if x != 0}
BISHOP_MOVES     = {(x, x) for x in range(-7, 8) if x != 0} | {(x, -x) for x in range(-7, 8) if x != 0}
QUEEN_MOVES      = ROOK_MOVES | BISHOP_MOVES
KNIGHT_MOVES     = {(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)}
WHITE_PAWN_MOVES = {(1, -1), (1, 0), (2, 0), (1, 1)}
BLACK_PAWN_MOVES = {(-1, -1), (-1, 0), (-2, 0), (-1, 1)}

PROMOTION_MOVES = {
    Name.Queen:  QUEEN_MOVES,
    Name.Rook:   ROOK_MOVES,
    Name.Bishop: BISHOP_MOVES,
    Name.Knight: KNIGHT_MOVES
}
PROMOTION_PIECES = {Name.Queen, Name.Rook, Name.Bishop, Name.Knight}

TO_FEN = {
    (Name.King, Color.White)   : 'K',
    (Name.Queen, Color.White)  : 'Q',
    (Name.Rook, Color.White)   : 'R',
    (Name.Bishop, Color.White) : 'B',
    (Name.Knight, Color.White) : 'N',
    (Name.Pawn, Color.White)   : 'P',

    (Name.King, Color.Black)   : 'k',
    (Name.Queen, Color.Black)  : 'q',
    (Name.Rook, Color.Black)   : 'r',
    (Name.Bishop, Color.Black) : 'b',
    (Name.Knight, Color.Black) : 'n',
    (Name.Pawn, Color.Black)   : 'p'
}

FROM_NOTATION = {
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
    '\u265F': (Name.Pawn, Color.Black),

    'K': (Name.King, None),
    'Q': (Name.Queen, None),
    'R': (Name.Rook, None),
    'B': (Name.Bishop, None),
    'N': (Name.Knight, None)
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

R_PIECE = r'(?P<name>[KQRBN]|[\u2654-\u2658\u265A-\u265E])(?P<file>[a-h])?(?P<rank>[1-8])?(?P<captures>x)?(?P<target>[a-h][1-8])(?P<extra>[+#])?(?P<promo_piece>)(?P<castling>)(?P<long_castle>)'
R_PAWN = r'(?P<name>[\u2659\u265F])?((?P<file>[a-h])(?P<captures>x))?(?P<target>[a-h][1-8])(=(?P<promo_piece>[KQRBN]|[\u2654-\u265F]))?(?P<extra>[+#])?(?P<rank>)(?P<castling>)(?P<long_castle>)'
R_CASTLING = r'(?P<castling>O-O(?P<long_castle>-O)?(?P<extra>[+#])?)(?P<name>)(?P<file>)(?P<rank>)(?P<captures>)(?P<target>)(?P<promo_piece>)'

def parse_notation(notation):
    if m := re.fullmatch(R_PIECE, notation):
        return m
    elif m := re.fullmatch(R_PAWN, notation):
        return m
    elif m := re.fullmatch(R_CASTLING, notation):
        return m

def to_figurine_notation(move, notation_info):
    out = ''
    if move.piece == Name.Pawn:
        if notation_info.captures:
            out += 'abcdefgh'[move.start[1] - 1]
            out += 'x'
    elif move.castling:
        if move.target[1] == 7:
            out += 'O-O'
        else:
            out += 'O-O-O'

        if notation_info.check and not notation_info.mate:
            out += '+'
        if notation_info.mate:
            out += '#'

        return out
    else:
        if move.color == Color.White:
            out += TO_WHITE_PIECE[move.piece]
        else:
            out += TO_BLACK_PIECE[move.piece]
        if not notation_info.unique:
            if not notation_info.file:
                out += 'abcdefgh'[move.start[1] - 1]
            elif not notation_info.rank:
                out += str(move.start[0])
            else:
                out += 'abcdefgh'[move.start[1] - 1] + str(move.start[0])
        if notation_info.captures:
            out += 'x'

    out += pos_to_square(move.target)

    if notation_info.promotion is not None:
        out += '='
        if move.color == Color.White:
            out += TO_WHITE_PIECE[notation_info.promotion]
        else:
            out += TO_BLACK_PIECE[notation_info.promotion]

    if notation_info.check and not notation_info.mate:
        out += '+'
    if notation_info.mate:
        out += '#'

    return out