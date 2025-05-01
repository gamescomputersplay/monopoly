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

    master_rng = random.Random(config.seed)
    data_for_simulation = [(i + 1, master_rng.getrandbits(32)) for i in range(config.n_games)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(monopoly_game, data_for_simulation), total=len(data_for_simulation)))

    analyzer = Analyzer()
    analyzer.run_all()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
