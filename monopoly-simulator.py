''' Main file to run monopoly simulation
'''

import random
import time

from tqdm import tqdm

from settings import SimulationSettings, GameSettings

from classes.log import Log
from classes.player import Player
from classes.board import Board

def one_game(game_number, game_seed):
    ''' Simulation of one game
    '''

    log = Log()
    log.add(f"\n\n= GAME {game_number} (seed = {game_seed}) =")

    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]

    board = Board(GameSettings)

    for turn_n in range(1, SimulationSettings.n_moves + 1):

        # Start a turn
        log.add(f"\n== Turn {turn_n} ===")

        # Log all the players and their current position/money
        for player_n, player in enumerate(players):
            log.add(f"- Player {player_n}, '{player.name}', " +
                    f"${player.money}, at {player.position} ({board.b[player.position].name})")

        for player in players:
            player.make_a_move(board, players, log)

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

    run_simulation(SimulationSettings)
