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
            except KeyboardInterrupt:
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
                print()
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()

    def run_to_crash(self):
        while True:
            self.__init__()
            self.one_game(200)

    def one_game(self, num_moves):
        for _ in range(num_moves):
            all_legal_moves = self.game.all_legal_moves(self.current_color)
            notations = []
            for move, notation_info in all_legal_moves:
                figure = self.game.get_figure_by_pos(move.start)
                target = move.target
                notations.append(to_figurine_notation(figure, target, notation_info))
            legal_move_notations = ' '.join(sorted(notations))

            if len(all_legal_moves) == 0:
                print('Pat')
                break

            move, notation_info = choice(all_legal_moves)

            fig_notation = to_figurine_notation(self.game.get_figure_by_pos(move.start), move.target, notation_info)
            notation = ''
            for char in fig_notation:
                if char in FROM_FIGURINE:
                    notation += TO_ALGEBRAIC.get(FROM_FIGURINE[char][0], '')
                else:
                    notation += char
            self.game.make_move_from_notation(notation, self.current_color)

            print(fig_notation)
            print('Vse možne poteze:', legal_move_notations)
            print(self.game.printable_state())
            print()

            if '#' in notation:
                barva = 'Beli' if self.current_color == Color.White else 'Črni'
                print('Konec igre!', barva, 'zmaga!')
                break

            self.current_color = other_color(self.current_color)


vmesnik = CLI()
vmesnik.one_game(200)