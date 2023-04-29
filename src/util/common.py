import string
import progressbar

from .configs import OUT_WIDTH

def player_names(num):
    alphabet = list(string.ascii_uppercase)
    return alphabet[num - 1]

# https://stackoverflow.com/a/28150307/10629176
def get_vars(module):
    return {key: value for key, value in module.__dict__.items() if not (key.startswith('__') or key.startswith('_'))}

def pbwrapper(iterable, max_value):
    """Returns a progress bar iterable with widgets"""
    widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.ETA()]
    progress = progressbar.ProgressBar(widgets=widgets, term_width=OUT_WIDTH, maxval=max_value)
    return progress(iterable)

def isGameOver(players):
    """Check if there are more then 1 player left in the game"""
    alive = 0
    for player in players:
        if not player.isBankrupt:
            alive += 1
    if alive > 1:
        return False
    else:
        return True