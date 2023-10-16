''' Main file to run monopoly simulation
'''

import random
import time

from tqdm import tqdm

from settings import SimulationSettings, GameSettings

from classes.player import Player
from classes.board import Board
from classes.dice import Dice
from classes.log import Log


def one_game(game_seed, log):
    ''' Simulation of one game
    '''

    # Set up players with their behaviour settings
    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]

    # Set up players starting money accouding to the game settings
    if isinstance(GameSettings.starting_money, list):
        for player, starting_money in zip(players, GameSettings.starting_money):
            player.money = starting_money
    else:
        for player in players:
            player.money = GameSettings.starting_money

    # Initiate the board
    board = Board(GameSettings)

    # Set up dice (create a separate rnadom generator with specific seed,
    # to make it thread-safe)
    dice = Dice(game_seed, GameSettings.dice_count, GameSettings.dice_sides)

    for turn_n in range(1, SimulationSettings.n_moves + 1):

        # Start a turn
        log.add(f"\n== Turn {turn_n} ===")

        # Log all the players and their current position/money
        for player_n, player in enumerate(players):
            log.add(f"- Player {player_n}, '{player.name}': " +
                    f"${player.money}, at {player.position} ({board.b[player.position].name})")

        # Players make their moves
        for player in players:
            player.make_a_move(board, players, dice, log)

    time.sleep(.2)


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
    iterator = tqdm(seeds, smoothing=False, leave=False)

    # Simulate each game
    for game_number, game_seed in enumerate(iterator, start = 1):

        log = Log()
        log.add(f"\n\n= GAME {game_number} of {config.n_simulations} (seed = {game_seed}) =")

        one_game(game_seed, log)

        log.save()


if __name__ == "__main__":

    run_simulation(SimulationSettings)
