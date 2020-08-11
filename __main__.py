import bottle
from src.model import Game
from src.definicije import *
import os

game = Game()

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
    return bottle.template('index.html', game=game)

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.post('/make_move')
def handle_move():
    notation = bottle.request.forms.fmove
    anno_value = bottle.request.forms.fanno
    text = bottle.request.forms.ftext
    try:
        game.make_move_from_notation(notation, anno_value)
    except ValueError as err:
        pass
    write_to_current(anno_value, text)
    bottle.redirect('/')

bottle.run(debug=True, reloader=True)