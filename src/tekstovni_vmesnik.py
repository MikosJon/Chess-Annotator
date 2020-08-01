from random import choice

from model import Game
from definicije import *

class CLI:
    def __init__(self):
        self.game = Game()
        self.current_color = Color.White

    def run(self):
        print('-----------------------------------------------')
        print(self.game.printable_state())
        print()
        while True:
            if self.game.is_stalemate(self.current_color):
                print('Pat!', '1/2 - 1/2')
                break

            try:
                color = 'Beli' if self.current_color == Color.White else 'Črni'
                notation = input(f'{color} ima potezo (Vnesi notacijo): ')
                self.game.make_move_from_notation(notation, self.current_color)
            except ValueError as err:
                message = err.args[0]
                if message == 'Not enough info':
                    print('Preveč figur lahko opravi to potezo!')
                elif message == 'Illegal move':
                    print('Ilegalna poteza!')
                else:
                    print('Nepricakovana napaka!')
                    raise
            except:
                print('Nepricakovana napaka!')
                raise
            else:
                if self.game.is_mate(other_color(self.current_color)):
                    result = '1 - 0' if self.current_color == Color.White else '0 - 1'
                    print(f'{color} zmaga!', result)
                    break
                self.current_color = other_color(self.current_color)
            finally:
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()


vmesnik = CLI()
vmesnik.run()