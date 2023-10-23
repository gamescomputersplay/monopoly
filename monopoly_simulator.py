''' Main file to run monopoly simulation
'''

import random
import concurrent.futures

from tqdm import tqdm

from settings import SimulationSettings, GameSettings

from classes.player import Player
from classes.board import Board, Property
from classes.dice import Dice
from classes.log import Log


def one_game(data_for_simulation):
    ''' Simulation of one game
    For convenience to set up a multi-thread, all data packed into a tuple:
    - game number (to dicplay it in the log)
    - seed to intialize the log
    '''
    game_number, game_seed = data_for_simulation

    # Initialize log
    log = Log()

    log.add(f"\n\n= GAME {game_number} of {SimulationSettings.n_simulations} " +
            f"(seed = {game_seed}) =")

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

    # Set up dice (create a separate random generator with initial "game_seed",
    # to make it thread-safe)
    dice = Dice(game_seed, GameSettings.dice_count, GameSettings.dice_sides, log)

    # Play for the required number of turns
    for turn_n in range(1, SimulationSettings.n_moves + 1):

        # Log a start a turn
        # Log all the players and their current position/money
        log.add(f"\n== GAME {game_number} Turn {turn_n} ===")
        for player_n, player in enumerate(players):
            log.add(f"- Player {player_n}, '{player.name}': " +
                    f"${player.money}, at {player.position} ({board.b[player.position].name})")

        # Players make their moves
        for player in players:
            player.make_a_move(board, players, dice, log)

    # Save the log
    log.save()

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

    # Pre-generate game seeds (to have simulation multi-thread safe)
    data_for_simulation = [
        (i + 1, random.random())
        for i in range(config.n_simulations)]

    # Simulate each game with multi-processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.multi_process) as executor:
        list(tqdm(executor.map(one_game, data_for_simulation), total=len(data_for_simulation)))


if __name__ == "__main__":
    run_simulation(SimulationSettings)
