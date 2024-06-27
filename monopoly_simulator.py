''' Main file to run monopoly simulation
'''

import random
import concurrent.futures

from tqdm import tqdm

from settings import SimulationSettings, LogSettings

from classes.analyze import Analyzer
from classes.log import Log
from classes.game import monopoly_game


def run_simulation(config):
    ''' Run the simulation
    In: Simulation parameters (number of games, seed etc)
    '''

    # Empty the game log file (list of all player actions)
    log = Log(LogSettings.game_log_file)
    log.reset()

    # Empty the data log (list of bankruptcy turns for each player)
    datalog = Log(LogSettings.data_log_file)
    datalog.reset("game_number\tplayer\tturn")

    # Initiate overall random generator with the seed from config file
    if config.seed is not None:
        random.seed(config.seed)

    # With that overall random generator, pre-generate
    # game seeds (to have simulation multi-thread safe).
    # data_for_simulation is a list of tuples: (game_number, game_seed)
    # it is packed together to be able to use multi-threading
    data_for_simulation = [
        (i + 1, random.random())
        for i in range(config.n_games)]

    # Simulate each game with multi-processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(monopoly_game, data_for_simulation), total=len(data_for_simulation)))

    # Print analysis of the simulation (data is read from datalog file)
    analysis = Analyzer()
    analysis.remaining_players()
    analysis.game_length()
    analysis.winning_rate()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
