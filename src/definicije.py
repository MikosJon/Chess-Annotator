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

TO_ANNOTATION = {
    '0': '',
    '1': '!',
    '2': '?',
    '3': '!!',
    '4': '??',
    '5': '!?',
    '6': '?!'
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

FROM_FIGURINE_TO_ALGEBRAIC = {
    '\u2654': 'K',
    '\u2655': 'Q',
    '\u2656': 'R',
    '\u2657': 'B',
    '\u2658': 'N',
    '\u2659': '',

    '\u265A': 'K',
    '\u265B': 'Q',
    '\u265C': 'R',
    '\u265D': 'B',
    '\u265E': 'N',
    '\u265F': ''
}

PGN_COUNTRY_CODES = {
    'Afganistan': 'AFG',
    'Albanija': 'ALB',
    'Alžirija': 'ALG',
    'Andora': 'AND',
    'Angola': 'ANG',
    'Antigva in Barbuda': 'ANT',
    'Argentina': 'ARG',
    'Armenija': 'ARM',
    'Aruba': 'ARU',
    'Ameriška Samoa': 'ASA',
    'Avstralija': 'AUS',
    'Avstrija': 'AUT',
    'Azerbajdžan': 'AZE',
    'Bahami': 'BAH',
    'Bangladeš': 'BAN',
    'Barbados': 'BAR',
    'Burundi': 'BDI',
    'Belgija': 'BEL',
    'Benin': 'BEN',
    'Bermuda': 'BER',
    'Butan': 'BHU',
    'Bosna in Hercegovina': 'BIH',
    'Belize': 'BIZ',
    'Belorusija': 'BLR',
    'Bolivija': 'BOL',
    'Bocvana': 'BOT',
    'Brazilija': 'BRA',
    'Bahrajn': 'BRN',
    'Brunei': 'BRU',
    'Bulgarija': 'BUL',
    'Burkina Faso': 'BUR',
    'Srednjeafriška republika': 'CAF',
    'Kambodija': 'CAM',
    'Kanada': 'CAN',
    'Kajmanski otoki': 'CAY',
    'Zahodni Kongo': 'CGO',
    'Čad': 'CHA',
    'Čile': 'CHI',
    'Kitajska': 'CHN',
    'Slonokoščena obala': 'CIV',
    'Kamerun': 'CMR',
    'Demokratična republika Kongo': 'COD',
    'Cookovi otoki': 'COK',
    'Kolumbija': 'COL',
    'Komori': 'COM',
    'Zelenortski otoki': 'CPV',
    'Kostarika': 'CRC',
    'Hrvaška': 'CRO',
    'Kuba': 'CUB',
    'Ciper': 'CYP',
    'Češka': 'CZE',
    'Danska': 'DEN',
    'Džibuti': 'DJI',
    'Dominika': 'DMA',
    'Dominikanska republika': 'DOM',
    'Ekvador': 'ECU',
    'Egipt': 'EGY',
    'Eritreja': 'ERI',
    'Republika Salvador': 'ESA',
    'Španija': 'ESP',
    'Estonija': 'EST',
    'Etiopija': 'ETH',
    'Fidži': 'FIJ',
    'Finska': 'FIN',
    'Francija': 'FRA',
    'Federativne države Mikronezije': 'FSM',
    'Gabon': 'GAB',
    'Gambija': 'GAM',
    'Združeno kraljestvo Velike Britanije in Irske': 'GBR',
    'Gvineja Bissau': 'GBS',
    'Gruzija': 'GEO',
    'Ekvatorialna Gvineja': 'GEQ',
    'Nemčija': 'GER',
    'Gana': 'GHA',
    'Grčija': 'GRE',
    'Grenada': 'GRN',
    'Gvatemala': 'GUA',
    'Gvineja': 'GUI',
    'Gvam': 'GUM',
    'Gvajana': 'GUY',
    'Haiti': 'HAI',
    'Hong Kong': 'HKG',
    'Honduras': 'HON',
    'Madžarska': 'HUN',
    'Indonezija': 'INA',
    'Indija': 'IND',
    'Iran': 'IRI',
    'Irska': 'IRL',
    'Irak': 'IRQ',
    'Islandija': 'ISL',
    'Izrael': 'ISR',
    'Ameriški Deviški otoki': 'ISV',
    'Italija': 'ITA',
    'Britanski Deviški otoki': 'IVB',
    'Jamajka': 'JAM',
    'Jordanija': 'JOR',
    'Japonska': 'JPN',
    'Kazahstan': 'KAZ',
    'Kenija': 'KEN',
    'Kirgizistan': 'KGZ',
    'Kiribati': 'KIR',
    'Južna Koreja': 'KOR',
    'Kosovo': 'KOS',
    'Saudova Arabija': 'KSA',
    'Kuvajt': 'KUW',
    'Laos': 'LAO',
    'Latvija': 'LAT',
    'Libija': 'LBA',
    'Lebanon': 'LBN',
    'Liberija': 'LBR',
    'Saint Lucia': 'LCA',
    'Lesoto': 'LES',
    'Lihtenštajn': 'LIE',
    'Litva': 'LTU',
    'Luksemburg': 'LUX',
    'Madagaskar': 'MAD',
    'Moroko': 'MAR',
    'Malezija': 'MAS',
    'Malavi': 'MAW',
    'Moldova': 'MDA',
    'Maldivi': 'MDV',
    'Mehika': 'MEX',
    'Mongolija': 'MGL',
    'Marshallovi otoki': 'MHL',
    'Severna Makedonija': 'MKD',
    'Mali': 'MLI',
    'Malta': 'MLT',
    'Črna Gora': 'MNE',
    'Monako': 'MON',
    'Mozambik': 'MOZ',
    'Mavricij': 'MRI',
    'Mavretanija': 'MTN',
    'Mjanmar': 'MYA',
    'Namibija': 'NAM',
    'Nikaragva': 'NCA',
    'Nizozemska': 'NED',
    'Nepal': 'NEP',
    'Nigerija': 'NGR',
    'Niger': 'NIG',
    'Norveška': 'NOR',
    'Nauru': 'NRU',
    'Nova Zelandija': 'NZL',
    'Oman': 'OMA',
    'Pakistan': 'PAK',
    'Panama': 'PAN',
    'Paragvaj': 'PAR',
    'Peru': 'PER',
    'Filipini': 'PHI',
    'Palestina': 'PLE',
    'Palau': 'PLW',
    'Papua Nova Gvineja': 'PNG',
    'Poljska': 'POL',
    'Portugalska': 'POR',
    'Severna Koreja': 'PRK',
    'Portoriko': 'PUR',
    'Katar': 'QAT',
    'Romunija':'ROU',
    'Republika Južna Afrika': 'RSA',
    'Rusija': 'RUS',
    'Ruanda': 'RWA',
    'Samoa': 'SAM',
    'Senegal': 'SEN',
    'Sejšeli': 'SEY',
    'Singapor': 'SGP',
    'Saint Kitts in Nevis': 'SKN',
    'Sierra Leone': 'SLE',
    'Slovenija': 'SLO',
    'San Marino': 'SMR',
    'Salomonovi otoki': 'SOL',
    'Somalija': 'SOM',
    'Srbija': 'SRB',
    'Šri Lanka': 'SRI',
    'Južni Sudan': 'SSD',
    'Sao Tome in Principe': 'STP',
    'Sudan': 'SUD',
    'Švica': 'SUI',
    'Surinam': 'SUR',
    'Slovaška': 'SVK',
    'Švedska': 'SWE',
    'Esvatini': 'SWZ',
    'Tanzanija': 'TAN',
    'Tonga': 'TGA',
    'Tajska': 'THA',
    'Tadžikistan': 'TJK',
    'Turkmenistan': 'TKM',
    'Vzhodni Timor': 'TLS',
    'Togo': 'TOG',
    'Tajvan': 'TPE',
    'Trinidad in Tobago': 'TTO',
    'Tunizija': 'TUN',
    'Turčija': 'TUR',
    'Tuvalu': 'TUV',
    'Združeni Arabski Emirati': 'UAE',
    'Uganda': 'UGA',
    'Ukrajina': 'UKR',
    'Urugvaj': 'URU',
    'Združene države Amerike': 'USA',
    'Uzbekistan': 'UZB',
    'Vanuatu': 'VAN',
    'Venezuela': 'VEN',
    'Sveti Vincent in Grenadini': 'VIN',
    'Jemen': 'YEM',
    'Zambija': 'ZAM',
    'Zimbabve': 'ZIM',
    'Macao': 'MAC',
    'Ferski otoki': 'FRO',
    'Nizozemski Antili': 'AHO',
    'Avstralazija': 'ANZ',
    'Bohemija': 'BOH',
    'Zahodna Nemčija': 'FRG',
    'Vzhodna Nemčija': 'GDR',
    'Rusko kraljestvo': 'RU1',
    'Srbija in Črna Gora': 'SCG',
    'Češkoslovaška': 'TCH',
    'Sovjetska Zveza': 'URS',
    'Jugoslavija': 'YUG'
}

def other_color(color):
    if color == Color.White:
        return Color.Black
    return Color.White

def pos_to_square(position):
    row, col = position
    return 'abcdefgh'[col - 1] + str(row)

def square_to_pos(square):
    return (int(square[-1]), 'abcdefgh'.index(square[-2]) + 1)

R_PIECE = r'(?P<name>[KQRBN]|[\u2654-\u2658\u265A-\u265E])(?P<file>[a-h])?(?P<rank>[1-8])?'\
          r'(?P<captures>x)?(?P<target>[a-h][1-8])(?P<extra>[+#])?(?P<promo_piece>)(?P<castling>)(?P<long_castle>)'

R_PAWN = r'(?P<name>[\u2659\u265F])?((?P<file>[a-h])(?P<captures>x))?(?P<target>[a-h][1-8])'\
         r'(=(?P<promo_piece>[KQRBN]|[\u2654-\u265F]))?(?P<extra>[+#])?(?P<rank>)(?P<castling>)(?P<long_castle>)'

R_CASTLING = r'(?P<castling>O-O(?P<long_castle>-O)?(?P<extra>[+#])?)(?P<name>)(?P<file>)'\
             r'(?P<rank>)(?P<captures>)(?P<target>)(?P<promo_piece>)'

def parse_notation(notation):
    if (m := re.fullmatch(R_PIECE, notation)):
        return m
    elif (m := re.fullmatch(R_PAWN, notation)):
        return m
    elif (m := re.fullmatch(R_CASTLING, notation)):
        return m

def to_figurine_notation(move, notation_info, *, anno='0'):
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

        out += TO_ANNOTATION.get(anno, '')
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

    out += TO_ANNOTATION.get(anno, '')
    return out

def to_algebraic_notation(move, notation_info, *, anno='0'):
    algebraic = ''
    for char in to_figurine_notation(move, notation_info, anno=anno):
        algebraic += FROM_FIGURINE_TO_ALGEBRAIC.get(char, char)
    return algebraic
