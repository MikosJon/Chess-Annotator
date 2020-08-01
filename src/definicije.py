from enum import Enum, auto
from dataclasses import dataclass

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
    rank = None
    file = None
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

KING_MOVES       = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (0, -2), (0, 2)]
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

def to_figurine_notation(figure, target, move_info):
    out = ''
    if figure.name == Name.Pawn:
        if move_info.captures:
            out += figure.file
            out += 'x'
    elif figure.name == Name.King and abs(figure.position[1] - target[1]) == 2:
        if target[1] == 7:
            out += 'O-O'
        else:
            out += 'O-O-O'

        if move_info.check and not move_info.mate:
            out += '+'
        if move_info.mate:
            out += '#'

        return out
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

def deconstruct_notation(notation, color=None):
    move = Move()
    notation = notation.replace('+', '')
    notation = notation.replace('#', '')

    if 'O' in notation:
        move.castling = True
        move.piece = Name.King
        move.color = color
        if notation.count('O') == 2:
            if color == Color.White:
                move.target = (1, 7)
            else:
                move.target = (8, 7)
        else:
            if color == Color.White:
                move.target = (1, 3)
            else:
                move.target = (8, 3)

        return move

    if '=' in notation:
        promo_notation = notation[-1]
        notation = notation[:-2]
    else:
        promo_notation = None

    move.target = square_to_pos(notation[-2:])

    if notation[0] in ALGEBRAIC_NAMES:
        if color is None:
            raise ValueError('Missing color!')
        move.color = color

        if promo_notation:
            move.promo_piece = FROM_ALGEBRAIC[promo_notation]
        else:
            move.promo_piece = None

        if notation[0] not in ALGEBRAIC_NAMES:
            move.piece = Name.Pawn
            position_info = notation[:-2]
        else:
            move.piece = FROM_ALGEBRAIC[notation[0]]
            position_info = notation[1:-2]

        position_info = position_info.replace('x', '')

        if len(position_info) == 1:
            if position_info in 'abcdefgh':
                move.file = position_info
            else:
                move.rank = int(position_info)
        elif len(position_info) == 2:
            move.file = position_info[0]
            move.rank = int(position_info[1])

    else:
        if notation[0].isascii():
            piece = Name.Pawn
        else:
            piece, color = FROM_FIGURINE[notation[0]]
        move.piece = piece
        move.color = color

        if promo_notation:
            move.promo_piece = FROM_FIGURINE[promo_notation][0]
        else:
            move.promo_piece = None

        if move.piece == Name.Pawn:
            position_info = notation[:-2]
        else:
            position_info = notation[1:-2]

        position_info = position_info.replace('x', '')

        if len(position_info) == 1:
            if position_info in 'abcdefgh':
                move.file = position_info
            else:
                move.rank = int(position_info)
        elif len(position_info) == 2:
            move.file = position_info[0]
            move.rank = int(position_info[1])

    return move