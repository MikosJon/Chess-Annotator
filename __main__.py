import bottle
from src.model import Game
from src.definicije import *
import os

game = Game()

moves = []
current_move_number = 0
last_played = Color.Black

for filename in os.listdir():
    if filename.endswith('PGN'):
        break
else:
    os.mkdir('PGN')
    os.mkdir('PGN/saved')

try:
    os.remove('PGN/current.pgn')
except:
    pass

def write_to_current(anno, text):
    with open('PGN/current.pgn', 'a') as f:
        alg_notation = to_algebraic_notation(game.last_move, game.last_notation_info)
        if game.current_color == Color.Black:
            if game.full_move_number != 1:
                f.write(f' {game.full_move_number}.')
            else:
                f.write(f'{game.full_move_number}.')
        f.write(f' {alg_notation}')
        if anno != '0':
            f.write(f'${anno}')
        if text:
            f.write(f' {{{text}}}')

        if game.game_state == GameState.Draw:
            f.write(' 1/2-1/2')
        elif game.game_state == GameState.White:
            f.write(' 1-0')
        elif game.game_state == GameState.Black:
            f.write(' 0-1')

@bottle.get('/')
def main():
    return bottle.template('index.html', game=game, move_num=current_move_number, last_col=last_played)

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.post('/make_move')
def make_move():
    global current_move_number, last_played
    notation = bottle.request.forms.fmove
    anno_value = bottle.request.forms.fanno
    text = bottle.request.forms.ftext
    try:
        game.make_move_from_notation(notation, anno_value)
    except ValueError as err:
        pass

    moves.append(game.moves[-1])
    current_move_number = game.full_move_number
    if game.current_color == Color.White:
        current_move_number -= 1
    last_played = game.last_move.color
    write_to_current(anno_value, text)
    bottle.redirect('/')

@bottle.post('/to_first')
def to_first():
    global last_played, current_move_number, game
    last_played = Color.Black
    current_move_number = 0
    game = Game()
    bottle.redirect('/')

@bottle.post('/previous_move')
def previous_move():
    global last_played, current_move_number
    if last_played == Color.White:
        current_move_number -= 1
    last_played = other_color(last_played)
    game.undo_last_move()
    bottle.redirect('/')

@bottle.post('/next_move')
def next_move():
    global last_played, current_move_number, game, moves
    idx = 2 * current_move_number
    if last_played == Color.White:
        idx -= 1
    next_move = moves[idx]
    game.make_move(next_move[0], next_move[2])
    if last_played == Color.Black:
        current_move_number += 1
    last_played = other_color(last_played)
    bottle.redirect('/')

@bottle.post('/to_last')
def to_last():
    global last_played, current_move_number
    last_played = game.last_move.color
    current_move_number = game.full_move_number
    bottle.redirect('/')

@bottle.post('/remove_from_now')
def remove_from_now():
    bottle.redirect('/')

bottle.run(debug=True, reloader=True)