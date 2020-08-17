import bottle
from src.model import Game
from src.definicije import *
import os

game = Game()

moves = []
current_move_number = 0
last_played = Color.Black
game_end = None

for filename in os.listdir():
    if filename.endswith('PGN'):
        break
else:
    os.mkdir('PGN')
    # os.mkdir('PGN/saved')

try:
    os.remove('PGN/current.pgn')
except:
    pass

def get_next_move_idx():
    idx = 2 * current_move_number
    if last_played == Color.White:
        idx -= 1
    return idx

@bottle.get('/')
def main():
    args = {'game': game, 'moves': moves, 'move_num': current_move_number, 'last_col': last_played}
    return bottle.template('index.html', args=args)

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.post('/make_move')
def make_move():
    global last_played, current_move_number, game_end
    notation = bottle.request.forms.fmove
    annotation = bottle.request.forms.fanno
    text = bottle.request.forms.ftext
    try:
        game.make_move_from_notation(notation)
    except ValueError as err:
        pass
    else:
        moves.append((*game.moves[-1], annotation, text))
        current_move_number = game.full_move_number
        if game.current_color == Color.White:
            current_move_number -= 1
        last_played = game.last_move.color
        # write_to_current(anno_value, text) TODO: export PGN button, save button
        if game.game_state != GameState.Normal:
            game_end = game.game_state
    bottle.redirect('/')

@bottle.post('/update_move')
def update_move():
    global current_move_number, last_played
    anno = bottle.request.forms.fanno
    text = bottle.request.forms.ftext

    idx = get_next_move_idx()
    move = moves[idx]
    updated_move = (move[0], move[1], anno, text)
    moves[idx] = updated_move

    game.make_move(move[0])
    current_move_number = game.full_move_number
    if game.current_color == Color.White:
        current_move_number -= 1
    last_played = game.last_move.color

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
    global last_played, current_move_number
    next_move = moves[get_next_move_idx()]
    game.make_move(next_move[0])
    if last_played == Color.Black:
        current_move_number += 1
    last_played = other_color(last_played)
    bottle.redirect('/')

@bottle.post('/to_last')
def to_last():
    global last_played, current_move_number
    for move, _, _, _ in moves[get_next_move_idx():]:
        game.make_move(move)
    last_played = game.last_move.color
    if last_played == Color.Black:
        current_move_number = game.full_move_number - 1
    else:
        current_move_number = game.full_move_number
    bottle.redirect('/')

@bottle.post('/remove_from_now')
def remove_from_now():
    global moves
    moves = moves[:get_next_move_idx()]
    bottle.redirect('/')

@bottle.post('/export_pgn')
def export_pgn():
    with open('PGN/current.pgn', 'w') as f:
        for idx, (move, notation_info, anno, text) in enumerate(moves):
            alg_notation = to_algebraic_notation(move, notation_info)
            if idx == 0:
                f.write('1.')
            else:
                f.write(' ' + str(idx + 1) + '.')
            f.write(f' {alg_notation}')
            if anno != '0':
                f.write(f'${anno}')
            if text:
                f.write(f' {{{text}}}')

        if game_end == GameState.Draw:
            f.write(' 1/2-1/2')
        elif game_end == GameState.White:
            f.write(' 1-0')
        elif game_end == GameState.Black:
            f.write(' 0-1')
        else:
            f.write(' *')
    return bottle.static_file('current.pgn', root='PGN', download=True)

bottle.run(debug=True, reloader=True)