import bottle
import os
import hashlib

from src.model import Game
from src.definicije import *

class User:
    def __init__(self, uname, key, salt):
        self.username = uname
        self.key = key
        self.salt = salt
        self.setup_game()

    def setup_game(self):
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

def get_current_user():
    username = bottle.request.get_cookie('username', secret=SECRET)
    if username is None:
        bottle.redirect('/login')
    return USERS[username]

@bottle.get('/')
def main():
    return bottle.redirect('/analysis')

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.get('/login')
def login():
    return bottle.template('login.html')

@bottle.post('/login')
def login():
    username = bottle.request.forms.flogin_username
    user = USERS.get(username, None)
    if user is None:
        bottle.redirect('/login')

    password = bottle.request.forms.fpassword
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
    username = bottle.request.forms.fregister_username
    if username in USERS:
        bottle.redirect('/login')
    password1 = bottle.request.forms.fpassword1
    password2 = bottle.request.forms.fpassword2

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
    user = User(username, key, salt)
    USERS[username] = user
    user.store_login_info()
    bottle.response.set_cookie('username', user.username, path='/', secret=SECRET)
    bottle.redirect('/')

@bottle.get('/logout')
def logout():
    bottle.response.delete_cookie('username', path='/')
    bottle.redirect('/login')

@bottle.get('/analysis')
def analysis():
    user = get_current_user()
    args = {}
    args['game'] = user.game
    args['moves'] = user.moves
    args['move_num'] = user.current_move_number
    args['last_color'] = user.last_played
    args['username'] = user.username
    return bottle.template('analysis.html', args=args, login=False)

@bottle.post('/make_move')
def make_move():
    user = get_current_user()
    notation = bottle.request.forms.fmove
    annotation = bottle.request.forms.fanno
    text = bottle.request.forms.ftext
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
    bottle.redirect('/')

@bottle.post('/update_move')
def update_move():
    user = get_current_user()
    anno = bottle.request.forms.fanno
    text = bottle.request.forms.ftext

    idx = user.next_move_idx()
    move = user.moves[idx]
    updated_move = (move[0], move[1], anno, text)
    user.moves[idx] = updated_move

    user.game.make_move(move[0])
    user.current_move_number = user.game.full_move_number
    if user.game.current_color == Color.White:
        user.current_move_number -= 1
    user.last_played = user.game.last_move.color

    bottle.redirect('/')

@bottle.post('/to_first')
def to_first():
    user = get_current_user()
    user.last_played = Color.Black
    user.current_move_number = 0
    user.game = Game()
    bottle.redirect('/')

@bottle.post('/previous_move')
def previous_move():
    user = get_current_user()
    if user.last_played == Color.White:
        user.current_move_number -= 1
    user.last_played = other_color(user.last_played)
    user.game.undo_last_move()
    bottle.redirect('/')

@bottle.post('/next_move')
def next_move():
    user = get_current_user()
    next_move = user.moves[user.next_move_idx()]
    user.game.make_move(next_move[0])
    if user.last_played == Color.Black:
        user.current_move_number += 1
    user.last_played = other_color(user.last_played)
    bottle.redirect('/')

@bottle.post('/to_last')
def to_last():
    user = get_current_user()
    for move, _, _, _ in user.moves[user.next_move_idx():]:
        user.game.make_move(move)
    user.last_played = user.game.last_move.color
    if user.last_played == Color.Black:
        user.current_move_number = user.game.full_move_number - 1
    else:
        user.current_move_number = user.game.full_move_number
    bottle.redirect('/')

@bottle.post('/remove_from_now')
def remove_from_now():
    user = get_current_user()
    user.moves = user.moves[:user.next_move_idx()]
    bottle.redirect('/')

@bottle.post('/export_pgn')
def export_pgn():
    user = get_current_user()
    with open(os.path.join(USERS_DIR, user.username, 'current.pgn'), 'w') as f:
        for idx, (move, notation_info, anno, text) in enumerate(user.moves):
            alg_notation = to_algebraic_notation(move, notation_info)
            if idx == 0:
                f.write('1.')
            elif move.color == Color.White:
                f.write(' ' + str(idx // 2 + 1) + '.')
            f.write(f' {alg_notation}')
            if anno != '0':
                f.write(f'${anno}')
            if text:
                f.write(f' {{{text}}}')

        if user.game_end == GameState.Draw:
            f.write(' 1/2-1/2')
        elif user.game_end == GameState.White:
            f.write(' 1-0')
        elif user.game_end == GameState.Black:
            f.write(' 0-1')
        else:
            f.write(' *')
    return bottle.static_file('current.pgn', root=os.path.join(USERS_DIR, user.username), download=True)

bottle.run(debug=True, reloader=True)