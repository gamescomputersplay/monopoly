''' Main file to run monopoly simulation
'''

import random
import concurrent.futures

from tqdm import tqdm

from settings import SimulationSettings, GameSettings, LogSettings

from classes.analize import Analyzer
from classes.player import Player
from classes.board import Board
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
    log = Log(LogSettings.game_log_file, disabled=not LogSettings.keep_game_log)

    log.add(f"\n\n= GAME {game_number} of {SimulationSettings.n_games} " +
            f"(seed = {game_seed}) =")

    datalog = Log(LogSettings.data_log_file)

    # Initiate the board
    board = Board(GameSettings)

    # Set up dice (create a separate random generator with initial "game_seed",
    # to make it thread-safe)
    dice = Dice(game_seed, GameSettings.dice_count, GameSettings.dice_sides, log)

    # Set up players with their behaviour settings
    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]

    if GameSettings.shuffle_players:
        # dice has a thread-safe copy of random.shuffle
        dice.shuffle(players)

    # Set up players starting money accouding to the game settings
    if isinstance(GameSettings.starting_money, list):
        for player, starting_money in zip(players, GameSettings.starting_money):
            player.money = starting_money
    else:
        for player in players:
            player.money = GameSettings.starting_money

    # Play for the required number of turns
    for turn_n in range(1, SimulationSettings.n_moves + 1):

        # Log a start a turn
        # Log all the players and their current position/money
        # Also, count alive players
        alive = 0
        log.add(f"\n== GAME {game_number} Turn {turn_n} ===")
        for player_n, player in enumerate(players):
            if not player.is_bankrupt:
                alive += 1
                log.add(f"- Player '{player.name}': " +
                        f"${player.money} (net {player.net_worth()}), at {player.position} ({board.b[player.position].name})")
            else:
                log.add(f"- Player {player_n}, '{player.name}': Bankrupt")

        # If there are less than 2 alive players
        # (I guess 0 alive is possible but quite unlikely)
        # End the game
        if alive < 2:
            log.add("Only 1 player remains, game over")
            break

        # Players make their moves
        for player in players:
            result = player.make_a_move(board, players, dice, log)
            # Keep track of when each player got bankrupt
            if result == "bankrupt":
                datalog.add(f"{game_number}\t{player}\t{turn_n}")

    board.log_curent_state(log)

    # Save the logs
    log.save()
    datalog.save()

    return None


def run_simulation(config):
    ''' Run the simulation
    In: Simulation parateters (number of games, seed etc)
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
        list(tqdm(executor.map(one_game, data_for_simulation), total=len(data_for_simulation)))

    # Print analysis of the simulation
    analysis = Analyzer()
    analysis.remaining_players()
    analysis.median_gamelength()
    analysis.winning_rate()


if __name__ == "__main__":
    run_simulation(SimulationSettings)
