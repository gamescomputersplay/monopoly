''' Main file to run monopoly simulation
'''

import random
import time
import concurrent.futures

from tqdm import tqdm

from settings import SimulationSettings, GameSettings

from classes.player import Player
from classes.board import Board
from classes.dice import Dice
from classes.log import Log


def one_game(data_for_simulation):
    ''' Simulation of one game
    For convenience to set up a multi-thread, all data packed into a tuple:
    - game number (to dicplay it in the log)
    - seed to intialize the log
    - log handle
    '''
    game_number, game_seed, log = data_for_simulation

    log.add(f"\n\n= GAME {game_number} of {SimulationSettings.n_simulations} (seed = {game_seed}) =")

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

    log.save()
    time.sleep(.2)

    return None


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

    # Initiate
    log = Log()

    # Pre-generate seeds (to have simulation multi-thread safe)
    data_for_simulation = [
        (i + 1, random.random(), log)
        for i in range(config.n_simulations)]

    # Simulate each game with multithreading
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(one_game, data_for_simulation), total=len(data_for_simulation)))


if __name__ == "__main__":

    run_simulation(SimulationSettings)
