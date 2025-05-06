""" Function that wraps one game of monopoly:
1. Setting up the board,
2. Players
3. Making moves by all players
"""
from typing import Tuple

from monopoly.core.move_result import MoveResult
from monopoly.core.board import Board
from monopoly.core.dice import Dice
from monopoly.core.game_utils import assign_property, _check_end_conditions, log_players_and_board_state
from monopoly.core.player import Player
from monopoly.log import Log
from monopoly.log_settings import LogSettings
from settings import SimulationSettings, GameSettings, GameMechanics


def monopoly_game(game_number_and_seeds: Tuple[int,int]) -> None:
    """ Simulation of one game.
    For convenience to set up a multi-thread,
    parameters are packed into a tuple: (game_number, game_seed):
    - "game number" is here to print out in the game log
    - "game_seed" to initialize random generator for the game
    """
    game_number, game_seed = game_number_and_seeds
    board, dice, events_log, bankruptcies_log = setup_game(game_number, game_seed)

    # Set up players with their behavior settings, starting money and properties.
    players = setup_players(board, dice)

    # Play the game until:
    # 1. Win: Only 1 player did not bankrupt
    # 2. Several survivors: All non-bankrupt players have more cash than `never_bankrupt_cash`
    # 3. Turn limit reached
    for turn_n in range(1, SimulationSettings.n_moves + 1):
        events_log.add(f"\n== GAME {game_number} Turn {turn_n} ===")
        log_players_and_board_state(board, events_log, players)
        board.log_board_state(events_log)
        events_log.add("")

        if _check_end_conditions(players, events_log, game_number, turn_n):
            break

        # Players make their moves
        for player in players:
            if player.is_bankrupt:
                continue
            move_result = player.make_a_move(board, players, dice, events_log)
            if move_result == MoveResult.BANKRUPT:
                bankruptcies_log.add(f"{game_number}\t{player}\t{turn_n}")

    # log the final game state
    board.log_current_map(events_log)
    events_log.save()
    if bankruptcies_log.content:
        bankruptcies_log.save()


def setup_players(board, dice):
    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]

    if GameSettings.shuffle_players:
        dice.shuffle(players)  # dice has a thread-safe copy of random.shuffle

    # Set up players starting money according to the game settings:
    # Supports either a dict (money per-player) or single value
    starting_money = GameSettings.starting_money
    if isinstance(starting_money, dict):
        for player in players:
            player.money = starting_money.get(player.name, 0)
    # If starting money is a single value, assign it to all players
    else:
        for player in players:
            player.money = starting_money

    # set up players' initial properties
    for player in players:
        property_indices = GameSettings.starting_properties.get(player.name, [])
        for cell_index in property_indices:
            assign_property(player, board.cells[cell_index], board)

    return players


def setup_game(game_number, game_seed):
    events_log = Log(LogSettings.EVENTS_LOG_PATH, disabled=not LogSettings.KEEP_GAME_LOG)
    events_log.add(f"= GAME {game_number} of {SimulationSettings.n_games} (seed = {game_seed}) =")

    bankruptcies_log = Log(LogSettings.BANKRUPTCIES_PATH)

    # Initialize the board (plots, chance, community chest etc.)
    board = Board(GameSettings)
    dice = Dice(game_seed, GameMechanics.dice_count, GameMechanics.dice_sides, events_log)
    dice.shuffle(board.chance.cards)
    dice.shuffle(board.chest.cards)
    return board, dice, events_log, bankruptcies_log
