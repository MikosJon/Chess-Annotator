import sys
from src.tekstovni_vmesnik import CLI

sys.stdin.reconfigure(encoding='utf-8')
vmesnik = CLI()
# vmesnik.run_to_crash()
# vmesnik.one_game()
vmesnik.main_loop()