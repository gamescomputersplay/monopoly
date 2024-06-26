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

    # Empty the log file
    log = Log(LogSettings.game_log_file)
    log.reset()
    log.save()

    # Empty and prepare headers for the data output
    datalog = Log(LogSettings.data_log_file)
    datalog.reset()
    datalog.add("game_number\tplayer\tturn")
    datalog.save()

    # Initiate RNG with the seed in config
    if config.seed is not None:
        random.seed(config.seed)

    # Pre-generate game seeds (to have simulation multi-thread safe)
    data_for_simulation = [
        (i + 1, random.random())
        for i in range(config.n_games)]

    # Simulate each game with multi-processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(monopoly_game, data_for_simulation), total=len(data_for_simulation)))

    # Print analysis of the simulation
    analysis = Analyzer()
    analysis.remaining_players()
    analysis.median_game_length()
    analysis.winning_rate()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
