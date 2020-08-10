# import sys
# from src.tekstovni_vmesnik import CLI

# sys.stdin.reconfigure(encoding='utf-8')
# vmesnik = CLI()
# vmesnik.run_to_crash()
# vmesnik.one_game()
# vmesnik.main_loop()

import bottle
from src.model import Game

game = Game()

@bottle.get('/')
def main():
    return bottle.template('index.html', game=game)

@bottle.get('/static/<filename>')
def static_file(filename):
    return bottle.static_file(filename, root='static')

@bottle.post('/make_move')
def handle_move():
    notation = bottle.request.forms.get('fmove')
    game.make_move_from_notation(notation)
    bottle.redirect('/')

bottle.run(debug=True, reloader=True)