import random
import concurrent.futures

from tqdm import tqdm

from monopoly.core.game import monopoly_game
from settings import SimulationSettings
from monopoly.log_settings import LogSettings
from monopoly.log import Log
from monopoly.analytics import Analyzer


def run_simulation(config):
    events_log = Log(LogSettings.EVENTS_LOG_PATH)
    events_log.reset("Events log")
    bankruptcies_log = Log(LogSettings.BANKRUPTCIES_PATH)
    bankruptcies_log.reset("game_number\tplayer_bankrupt\tturn")

    # Initiate an overall random generator with the seed from the settings.py file
    if config.seed is not None:
        random.seed(config.seed)

    # With that overall random generator, pre-generate game seeds
    # `data_for_simulation` is a list of tuples: (game_number, game_seed)
    data_for_simulation = [(i + 1, random.randint(0, 2 ** 32 - 1)) for i in range(config.n_games)]

    # Simulate each game with multiprocessing
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(monopoly_game, data_for_simulation), total=len(data_for_simulation)))

    # Print analysis of the simulation (data is read from the bankruptcies_log file)
    analyzer = Analyzer()
    analyzer.remaining_players()
    analyzer.game_length()
    analyzer.winning_rate()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
