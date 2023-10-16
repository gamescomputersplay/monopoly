''' Main file to run monopoly simulation
'''

import random
import time

from tqdm import tqdm

from config import SimulationConfig
from log import Log

def one_game(game_number, game_seed):
    ''' Simulation of one game
    '''

    log = Log()
    log.add(f"=== GAME {game_number} (seed = {game_seed}) ===")

    time.sleep(.1)

    log.save()


def run_simulation(config):
    ''' Run the simulation
    In: Simulation parateters (number of games, seed etc)
    '''

    # Empty the log file
    log = Log()
    log.reset()

    # Initiate RNG with the seed in config
    if config.seed is not None:
        random.seed(config.seed)

    # Pre-generate seeds (to have simulation multi-thread safe)
    seeds = [random.random() for _ in range(config.n_simulations)]

    # Use TQDM to show a progress bar
    # We'll be iterating through the list of seeds, numbering games from 1
    iterator = tqdm(enumerate(seeds, start=1), smoothing=False, leave=False)

    for game_number, game_seed in iterator:
        one_game(game_number, game_seed)

if __name__ == "__main__":

    run_simulation(SimulationConfig)
