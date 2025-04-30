import random
import concurrent.futures

from tqdm import tqdm

from monopoly.core.game import monopoly_game
from settings import SimulationSettings
from monopoly.log_settings import LogSettings
from monopoly.log import Log
from monopoly.analytics import Analyzer


def run_simulation(config):
    detailed_log = Log(LogSettings.DETAILED_LOG_PATH)
    detailed_log.reset()

    bankruptcies_log = Log(LogSettings.BANKRUPTCIES_PATH)
    bankruptcies_log.reset("game_number\tplayer_bankrupt\tturn")

    # Initiate an overall random generator with the seed from a config file
    if config.seed is not None:
        random.seed(config.seed)

    # With that overall random generator, pre-generate
    # game seeds (to have simulation multi-thread safe).
    # `data_for_simulation` is a list of tuples: (game_number, game_seed)
    # it is packed together to be able to use multi-threading
    data_for_simulation = [(i + 1, random.randint(0, 2 ** 32 - 1)) for i in range(config.n_games)]

    # Simulate each game with multiprocessing
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(monopoly_game, data_for_simulation), total=len(data_for_simulation)))

    # Print analysis of the simulation (data is read from the bankruptcies_log file)
    analysis = Analyzer()
    analysis.remaining_players()
    analysis.game_length()
    analysis.winning_rate()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
