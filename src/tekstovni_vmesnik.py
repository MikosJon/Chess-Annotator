from random import choice
from functools import partial
import os

from src.model import Game
from src.definicije import *

class CLI:
    def __init__(self):
        self.game = Game()
        if os.getcwd().endswith('Chess-Annotator'):
            os.chdir('PGN')
        else:
            os.chdir('Chess-Annotator/PGN')

        with open('movetext.txt', 'w') as f:
            pass

    def main_loop(self):
        while True:
            while True:
                print('Proti komu bi rad igral?')
                print('1 - sebi')
                print('2 - naključnemu računalniku')
                opponent = input('-> ')
                print()
                if opponent in '12':
                    break
            if opponent == '1':
                self.run_game(self.vs_yourself)
            else:
                while True:
                    print('Izberi barvo figur, s katerimi želiš igrati')
                    print('1 - bele')
                    print('2 - črne')
                    print('3 - naključne')
                    color = input('-> ')
                    print()
                    if color in '123':
                        break
                if color == '1':
                    self.run_game(partial(self.vs_random_cpu, Color.White))
                elif color == '2':
                    self.run_game(partial(self.vs_random_cpu, Color.Black))
                else:
                    self.run_game(partial(self.vs_random_cpu, choice([Color.White, Color.Black])))
            while True:
                print('Želiš igrati še enkrat [Yy/Nn]? ')
                replay = input('-> ')
                if replay in 'YyNn':
                    break
            if replay.upper() == 'N':
                break
            else:
                print()
                self.__init__()

    def inquire_draw(self):
        while True:
            print('Lahko razglasiš pat [Yy/Nn]:')
            draw = input('-> ')
            if draw in 'YNyn':
                break
        if draw.upper() == 'Y':
            self.game.game_state = GameState.Draw

    def vs_yourself(self):
        color = 'Beli' if self.game.current_color == Color.White else 'Črni'

        if self.game.claimable_draw:
            self.inquire_draw()

        else:
            print(f'{color} ima potezo (Vnesi notacijo): ')
            notation = input('-> ')
            print(notation, '| Poteza #' + str(self.game.full_move_number))
            self.game.make_move_from_notation(notation)
            print('-----------------------------------------------')
            print(self.game.printable_state())
            print()

            with open('movetext.txt', 'a', encoding='utf-8') as f:
                if self.game.current_color == Color.Black:
                    if self.game.full_move_number == 1:
                        f.write(str(self.game.full_move_number) + '.')
                    else:
                        f.write(' ' + str(self.game.full_move_number) + '.')
                f.write(' ' + to_algebraic_notation(self.game.last_move, self.game.last_notation_info))

        if self.game.claimable_draw:
            self.inquire_draw()

    def vs_random_cpu(self, player_color):
        if self.game.current_color == player_color:
            if self.game.claimable_draw:
                self.inquire_draw()

            else:
                print('Si na potezi (Vnesi notacijo): ')
                notation = input('-> ')
                print(notation, '| Poteza #' + str(self.game.full_move_number))

                self.game.make_move_from_notation(notation)
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()

                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    if self.game.current_color == Color.Black:
                        if self.game.full_move_number == 1:
                            f.write(str(self.game.full_move_number) + '.')
                        else:
                            f.write(' ' + str(self.game.full_move_number) + '.')
                    f.write(' ' + to_algebraic_notation(self.game.last_move, self.game.last_notation_info))

            if self.game.claimable_draw:
                self.inquire_draw()
        else:
            all_legal_moves = list*self.game.all_legal_moves(self.game.current_color)()
            move, notation_info = choice(all_legal_moves)

            if self.game.claimable_draw:
                self.game.game_state = GameState.Draw
            else:
                fig_notation = to_figurine_notation(move, notation_info)
                print(fig_notation, '| Poteza #' + str(self.game.full_move_number))
                self.game.make_move(move)
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()

                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    if self.game.current_color == Color.Black:
                        if self.game.full_move_number == 1:
                            f.write(str(self.game.full_move_number) + '.')
                        else:
                            f.write(' ' + str(self.game.full_move_number) + '.')
                    f.write(' ' + to_algebraic_notation(self.game.last_move, self.game.last_notation_info))

            if self.game.claimable_draw:
                self.game.game_state = GameState.Draw

    def annotation_handler(self):
        while True:
            print('Dodaj anotacije? [Yy/Nn]')
            anno = input('-> ')
            if anno in 'YyNn':
                break
        if anno.upper() == 'Y':
            while True:
                print('0 preskoči')
                print('1 dobra poteza ("!")')
                print('2 slaba poteza ("?")')
                print('3 zelo dobra poteza ("!!")')
                print('4 zelo slaba poteza ("??")')
                print('5 zanimiva poteza ("!?")')
                print('6 vprašljiva poteza ("?!")')

                sign = input('-> ')
                if sign in '123456':
                    with open('movetext.txt', 'a', encoding='utf-8') as f:
                        f.write(f'${sign}')
                    break
                elif sign == '0':
                    break

        while True:
            print('Dodaj tekst? [Yy/Nn]')
            text = input('-> ')
            if text in 'YyNn':
                break
        if text.upper() == 'Y':
            print('Vnesi tekst (\u21B5 konča vnos):')
            comment = input('-> ')
            if comment:
                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    f.write(f' {{{comment}}}')

    def run_game(self, move_handler):
        print('-----------------------------------------------')
        print(self.game.printable_state())
        print()
        while True:
            try:
                move_handler()
                self.annotation_handler()
            except ValueError as err:
                message = err.args[0]
                if message == 'Not enough info':
                    print('Preveč figur lahko opravi to potezo!')
                elif message == 'Illegal move':
                    print('Ilegalna poteza!')
                elif message == 'Wrong notation':
                    print('Napačna notacija')
                else:
                    print('Nepričakovana napaka!')
                    raise
            except KeyboardInterrupt:
                raise
            except:
                print('Nepričakovana napaka!')
                raise
            else:
                if self.game.game_state == GameState.White:
                    print('Beli zmaga! 1 - 0')
                    with open('movetext.txt', 'a', encoding='utf-8') as f:
                        f.write(' 1-0')
                    break
                elif self.game.game_state == GameState.Black:
                    print('Črni zmaga! 0 - 1')
                    with open('movetext.txt', 'a', encoding='utf-8') as f:
                        f.write(' 0-1')
                    break
                elif self.game.game_state == GameState.Draw:
                    print('Pat! 1/2 - 1/2')
                    with open('movetext.txt', 'a', encoding='utf-8') as f:
                        f.write(' 1/2-1/2')
                    break
            finally:
                print('-----------------------------------------------')
                print(self.game.printable_state())
                print()

    def run_to_crash(self):
        while True:
            self.__init__()
            self.one_game()

    def one_game(self):
        while True:
            all_legal_moves = list(self.game.all_legal_moves(self.game.current_color))
            notations = []
            for move, notation_info in all_legal_moves:
                notations.append(to_figurine_notation(move, notation_info))
            legal_move_notations = ' '.join(sorted(notations))

            move, notation_info = choice(all_legal_moves)

            if self.game.claimable_draw:
                self.game.game_state = GameState.Draw
            else:
                fig_notation = to_figurine_notation(move, notation_info)
                print(fig_notation, '| Poteza #' + str(self.game.full_move_number))
                self.game.make_move(move)

            if self.game.claimable_draw:
                self.game.game_state = GameState.Draw

            print('Vse možne poteze:', legal_move_notations)

            print(self.game.printable_state())
            print()
            print(self.game.generate_FEN())
            print()

            if self.game.game_state == GameState.White:
                print('Beli zmaga! 1 - 0')
                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    f.write(' 1-0')
                break
            elif self.game.game_state == GameState.Black:
                print('Črni zmaga! 0 - 1')
                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    f.write(' 0-1')
                break
            elif self.game.game_state == GameState.Draw:
                print('Pat! 1/2 - 1/2')
                with open('movetext.txt', 'a', encoding='utf-8') as f:
                    f.write(' 1/2-1/2')
                break

if __name__ == '__main__':
    raise DeprecationWarning("We don't do that here anymore.")