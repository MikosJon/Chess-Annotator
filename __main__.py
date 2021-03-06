import bottle
import os
import re
import hashlib

from unicodedata import normalize

from src.model import Game
from src.definicije import *

class User:
    def __init__(self, username, key, salt):
        self.username = username
        self.key = key
        self.salt = salt
        self.setup_game()

    def setup_game(self):
        self.current_file = ''
        self.game = Game()

        self.moves = []
        self.current_move_number = 0
        self.last_played = Color.Black
        self.game_end = None

    def store_login_info(self):
        with open(os.path.join(USERS_DIR, self.username, 'login_info'), 'ab') as f:
            f.write(self.key)
            f.write(self.salt)

    def next_move_idx(self):
        idx = 2 * self.current_move_number
        if self.last_played == Color.White:
            idx -= 1
        return idx

USERS_DIR = 'Users'
SAVED_GAMES_DIR = 'saved'
TEMP_PGN_NAME = 'current.pgn'

USERS = {}
SECRET = 'DO YOU WISH FOR A NEW WORLD?'

KEY_SIZE = 128
SALT_SIZE = 32

if not os.path.isdir(USERS_DIR):
    os.mkdir(USERS_DIR)

for user_dir in os.listdir(USERS_DIR):
    with open(os.path.join(USERS_DIR, user_dir, 'login_info'), 'rb') as f:
        username = user_dir
        key = f.read(KEY_SIZE)
        salt = f.read(SALT_SIZE)
        USERS[username] = User(username, key, salt)

def sanitize_filename(fname):   # spremenjena verzija metode v bottle.FileUpload
    fname = normalize('NFKD', fname).encode('ASCII', 'ignore').decode('ASCII')
    fname = os.path.basename(fname.replace('\\', os.path.sep))
    fname = re.sub(r'[^a-zA-Z0-9-_.\s]', '', fname).strip()
    fname = re.sub(r'[-\s]+', '-', fname).strip('.-')
    return fname[:255] or None

def get_current_user():
    username = bottle.request.get_cookie('username', secret=SECRET)
    if username is None:
        bottle.redirect('/login')
    return USERS[username]

@bottle.get('/')
def main():
    bottle.redirect('/user')

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.get('/login')
def login():
    return bottle.template('login.html')

@bottle.post('/login')
def login():
    username = bottle.request.forms.login_username
    user = USERS.get(username, None)
    if user is None:
        bottle.redirect('/login')

    password = bottle.request.forms.password
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        user.salt,
        100000,
        dklen=KEY_SIZE
    )
    if key != user.key:
        bottle.redirect('/login')

    user.setup_game()
    bottle.response.set_cookie('username', user.username, path='/', secret=SECRET)
    bottle.redirect('/')

@bottle.post('/register')
def register():
    username = bottle.request.forms.register_username
    if username in USERS:
        bottle.redirect('/login')
    password1 = bottle.request.forms.password1
    password2 = bottle.request.forms.password2

    if password1 != password2:
        bottle.redirect('/login')
    salt = os.urandom(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password1.encode('utf-8'),
        salt,
        100000,
        dklen=KEY_SIZE
    )
    os.mkdir(os.path.join(USERS_DIR, username))
    os.mkdir(os.path.join(USERS_DIR, username, SAVED_GAMES_DIR))

    user = User(username, key, salt)
    USERS[username] = user
    user.store_login_info()

    bottle.response.set_cookie('username', user.username, path='/', secret=SECRET)
    bottle.redirect('/')

@bottle.get('/logout')
def logout():
    bottle.response.delete_cookie('username', path='/')
    bottle.redirect('/login')

@bottle.get('/user')
def user():
    user = get_current_user()
    names = os.listdir(os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR))
    return bottle.template('user.html', filenames=names, user=user)

@bottle.get('/analysis')
def analysis():
    return bottle.template('analysis.html', user=get_current_user())

@bottle.post('/make_move')
def make_move():
    '''
        Preberemo dobljeno notacijo in poskušamo opraviti željeno potezo.
        Če je bila notacija ustrezna, nastavimo trenutno stanje vmesnika.
    '''
    user = get_current_user()
    notation = bottle.request.forms.move
    annotation = bottle.request.forms.anno
    text = bottle.request.forms.text

    text.replace('{', '')
    text.replace('}', '')
    try:
        user.game.make_move_from_notation(notation)
    except ValueError as err:
        pass
    else:
        user.moves.append((*user.game.moves[-1], annotation, text))

        user.current_move_number = user.game.full_move_number
        if user.game.current_color == Color.White:
            user.current_move_number -= 1

        user.last_played = user.game.last_move.color
        if user.game.game_state != GameState.Normal:
            user.game_end = user.game.game_state

    bottle.redirect('/analysis')

@bottle.post('/update_move')
def update_move():
    '''
        Preberemo podatke in posodobimo shranjeno potezo.
    '''
    user = get_current_user()
    anno = bottle.request.forms.anno
    text = bottle.request.forms.text

    idx = user.next_move_idx()
    move = user.moves[idx]
    updated_move = (move[0], move[1], anno, text)
    user.moves[idx] = updated_move

    user.game.make_move(move[0])
    user.current_move_number = user.game.full_move_number
    if user.game.current_color == Color.White:
        user.current_move_number -= 1
    user.last_played = user.game.last_move.color

    bottle.redirect('/analysis')

@bottle.post('/to_first')
def to_first():
    '''
        Spremenimo stanje vmesnika, da prikažemo začetno pozicijo.
    '''
    user = get_current_user()
    user.last_played = Color.Black
    user.current_move_number = 0
    user.game = Game()

    bottle.redirect('/analysis')

@bottle.post('/previous_move')
def previous_move():
    '''
        Spremenimo stanje vmesnika, da prikažemo prejšno pozicijo.
    '''
    user = get_current_user()
    user.game.undo_last_move()
    if user.last_played == Color.White:
        user.current_move_number -= 1
    user.last_played = other_color(user.last_played)
    bottle.redirect('/analysis')

@bottle.post('/next_move')
def next_move():
    '''
        Spremenimo stanje vmesnika, da prikažemo naslednjo pozicijo.
    '''
    user = get_current_user()
    next_move = user.moves[user.next_move_idx()]
    user.game.make_move(next_move[0])
    if user.last_played == Color.Black:
        user.current_move_number += 1
    user.last_played = other_color(user.last_played)
    bottle.redirect('/analysis')

@bottle.post('/to_last')
def to_last():
    '''
        Spremenimo stanje vmesnika, da prikažemo zadnjo pozicijo.
    '''
    user = get_current_user()
    for move, _, _, _ in user.moves[user.next_move_idx():]:
        user.game.make_move(move)
    user.last_played = user.game.last_move.color
    if user.last_played == Color.Black:
        user.current_move_number = user.game.full_move_number - 1
    else:
        user.current_move_number = user.game.full_move_number
    bottle.redirect('/analysis')

@bottle.post('/remove_from_now')
def remove_from_now():
    '''
        Odstranimo vse nadaljne opravljene poteze in shranjene pozicije iz spomina.
    '''
    user = get_current_user()
    user.moves = user.moves[:user.next_move_idx()]
    user.game_end = user.game.game_state
    bottle.redirect('/analysis')

@bottle.post('/new_game')
def new_game():
    user = get_current_user()
    user.setup_game()
    bottle.redirect('/analysis')

@bottle.post('/save_moves')
def save_moves():
    '''
        Preberemo novo ime datoteke in ga spremenimo, da je primerno za shranjevanje na disk.
        Nato zapišemo poteze po PGN standardu (pri čemer nimamo zapisanih nobenih značk,
        ki jih standard dopušča).
    '''
    user = get_current_user()
    result = bottle.request.forms.result
    filename = sanitize_filename(bottle.request.forms.filename)
    overwrite = bool(bottle.request.forms.overwrite)

    filepath = os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR, filename)
    if not overwrite and os.path.exists(filepath):
        bottle.redirect('/analysis')

    with open(filepath, 'w') as f:
        for idx, (move, notation_info, anno, text) in enumerate(user.moves):
            alg_notation = to_algebraic_notation(move, notation_info)
            if idx == 0:
                f.write('1.')
            elif move.color == Color.White:
                f.write(f' {idx // 2 + 1}.')
            f.write(f' {alg_notation}')
            if anno != '0':
                f.write(f'${anno}')
            if text:
                f.write(f' {{{text}}}')
        f.write(' ' + result)

    user.current_file = filename
    bottle.redirect('/analysis')

@bottle.post('/export_pgn')
def export_pgn():
    '''
        Preberemo podatke in zapišemo vseh 7 potrebnih značk za dolgoročno shranjevanje PGN datotek
        ter opravljene poteze. Vse sledi PGN standardu. Nato datoteko izvozimo uporabniku.
    '''
    user = get_current_user()

    event = bottle.request.forms.event
    city = bottle.request.forms.city
    region = bottle.request.forms.region
    country = PGN_COUNTRY_CODES[bottle.request.forms.country]

    date = bottle.request.forms.date
    event_round = bottle.request.forms.event_round

    white_name = bottle.request.forms.white_name
    white_surname = bottle.request.forms.white_surname
    black_name = bottle.request.forms.black_name
    black_surname = bottle.request.forms.black_surname

    result = bottle.request.forms.result

    root_path = os.path.join(USERS_DIR, user.username)
    with open(os.path.join(root_path, TEMP_PGN_NAME ), 'w') as f:
        f.write(f'[Event "{event}"]\n')
        f.write(f'[Site "{city}, {region} {country}"]\n')
        f.write(f'[Date "{date}"]\n')
        f.write(f'[Round "{event_round}"]\n')
        f.write(f'[White "{white_surname}, {white_name}"]\n')
        f.write(f'[Black "{black_surname}, {black_name}"]\n')
        f.write(f'[Result "{result}"]\n\n')

        for idx, (move, notation_info, anno, text) in enumerate(user.moves):
            alg_notation = to_algebraic_notation(move, notation_info)
            if idx == 0:
                f.write('1.')
            elif move.color == Color.White:
                f.write(f' {idx // 2 + 1}.')
            f.write(f' {alg_notation}')
            if anno != '0':
                f.write(f'${anno}')
            if text:
                f.write(f' {{{text}}}')
        if result != '*':
            f.write(f' {result}')

    return bottle.static_file(TEMP_PGN_NAME , root=root_path, download=True)

@bottle.post('/rename')
def rename():
    user = get_current_user()
    old_filename = bottle.request.forms.old_filename
    new_filename = sanitize_filename(bottle.request.forms.new_filename)

    old_filepath = os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR, old_filename)
    new_filepath = os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR, new_filename)

    os.rename(old_filepath, new_filepath)
    bottle.redirect('/user')

@bottle.post('/launch')
def launch():
    '''
        Preberemo izbrano datoteko s shranjenimi potezami in jih prikažemo v vmesniku.
    '''
    user = get_current_user()
    filename = bottle.request.forms.filename

    user.setup_game()
    filepath = os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR, filename)
    with open(filepath, 'r') as f:
        in_comment = False
        notation = ''
        anno = '0'
        text = ''

        for line in f:
            for token in line.split():
                if in_comment:
                    if token.endswith('}'):
                        in_comment = False
                        text += f' {token[:-1]}'
                    else:
                        text += f' {token}'
                    move, notation_info, annotation, _ = user.moves[-1]
                    user.moves[-1] = (move, notation_info, annotation, text)
                else:
                    if token.startswith('{'):
                        in_comment = True
                        text = token[1:]
                        continue
                    if token in {'*', '1-0', '0-1', '1/2-1/2'} or token.endswith('.'):
                        continue

                    if '$' in token:
                        notation, anno = token.split('$')
                    else:
                        notation = token
                        anno = '0'
                    user.game.make_move_from_notation(notation)
                    user.moves.append((*user.game.moves[-1], anno, ''))

    user.game_end = user.game.game_state
    user.current_file = filename
    to_first()

@bottle.post('/download')
def download():
    '''
        Izbrano datoteko s potezami izvozimo uporabniku.
    '''
    user = get_current_user()
    filename = bottle.request.forms.filename

    root_path = os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR)
    return bottle.static_file(filename , root=root_path, download=True)

@bottle.post('/remove')
def remove():
    '''
        Izbrano datoteko s potezami odstranimo z diska.
    '''
    user = get_current_user()
    filename = bottle.request.forms.filename

    os.remove(os.path.join(USERS_DIR, user.username, SAVED_GAMES_DIR, filename))
    bottle.redirect('/user')

bottle.run()