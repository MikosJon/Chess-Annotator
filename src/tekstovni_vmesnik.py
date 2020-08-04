from random import choice

from model import Game
from definicije import *

class CLI:
    def __init__(self):
        self.game = Game()

    def run(self):
        print('-----------------------------------------------')
        print(self.game.printable_state())
        print()
        while True:
            try:
                color = 'Beli' if self.game.current_color == Color.White else 'Črni'
                notation = input(f'{color} ima potezo (Vnesi notacijo): ')
                self.game.make_move_from_notation(notation)
            except ValueError as err:
                message = err.args[0]
                if message == 'Not enough info':
                    print('Preveč figur lahko opravi to potezo!')
                elif message == 'Illegal move':
                    print('Ilegalna poteza!')
                elif message == 'Wrong notation':
                    print('Napačna notacija')
                else:
                    print('Nepricakovana napaka!')
                    raise
            except KeyboardInterrupt:
                raise
            except:
                print('Nepricakovana napaka!')
                raise
            else:
                if self.game.game_state == GameState.White:
                    print('Beli zmaga! 1 - 0')
                    break
                elif self.game.game_state == GameState.Black:
                    print('Črni zmaga! 0 - 1')
                    break
                elif self.game.game_state == GameState.Draw:
                    print('Pat! 1/2 - 1/2')
                    break
            finally:
                print()
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()

    def run_to_crash(self):
        while True:
            self.__init__()
            self.one_game()

    def one_game(self):
        i = 2
        while True:
            all_legal_moves = self.game.all_legal_moves(self.game.current_color)
            notations = []
            for move, notation_info in all_legal_moves:
                figure = self.game.get_figure_by_pos(move.start)
                target = move.target
                notations.append(to_figurine_notation(figure, target, notation_info))
            legal_move_notations = ' '.join(sorted(notations))

            move, notation_info = choice(all_legal_moves)

            fig_notation = to_figurine_notation(self.game.get_figure_by_pos(move.start), move.target, notation_info)
            self.game.make_move_from_notation(fig_notation)

            print(fig_notation, str(i // 2))
            print('Vse možne poteze:', legal_move_notations)
            print(self.game.printable_state())
            print()

            if self.game.game_state == GameState.White:
                print('Beli zmaga! 1 - 0')
                break
            elif self.game.game_state == GameState.Black:
                print('Črni zmaga! 0 - 1')
                break
            elif self.game.game_state == GameState.Draw:
                print('Pat! 1/2 - 1/2')
                break

            i += 1


vmesnik = CLI()
# vmesnik.run_to_crash()
vmesnik.one_game()
# vmesnik.run()