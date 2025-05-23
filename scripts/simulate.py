import random
from typing import Type

from tqdm.contrib.concurrent import process_map

from monopoly.analytics import Analyzer
from monopoly.core.game import monopoly_game
from monopoly.log_settings import LogSettings
from settings import SimulationSettings


def run_simulation(config: Type[SimulationSettings]) -> None:
    """Simulate N games in parallel, then print an analysis."""
    LogSettings.init_logs()

    master_rng = random.Random(config.seed)
    game_seed_pairs = [(i + 1, master_rng.getrandbits(32)) for i in range(config.n_games)]

    process_map(
        monopoly_game,
        game_seed_pairs,
        max_workers=config.multi_process,
        total=config.n_games,
        desc="Simulating Monopoly games",
    )

    Analyzer().run_all()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
