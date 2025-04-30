""" Function, that wraps one game of monopoly:
1. setting up the board,
2. players
3. making moves by all players
"""

from settings import SimulationSettings, GameSettings, LogSettings

from classes.player import Player, BANKRUPT
from classes.board import Board
from classes.dice import Dice
from classes.log import Log


# Assign properties to players
def assign_property(player, property, board):
    property.owner = player
    player.owned.append(property)
    board.recalculate_monopoly_multipliers(property)
    player.update_lists_of_properties_to_trade(board)


def monopoly_game(data_for_simulation):
    """ Simulation of one game.
    For convenience to set up a multi-thread,
    parameters are packed into a tuple: (game_number, game_seed):
    - "game number" is here to print out in the game log
    - "game_seed" to initialize random generator for the game
    """
    game_number, game_seed = data_for_simulation
    board, dice, log, datalog = setup_game(game_number, game_seed)
    
    # Set up players with their behavior settings, starting money and properties.
    players = setup_players(board, dice)
    
    # Play for the required number of turns
    for turn_n in range(1, SimulationSettings.n_moves + 1):
        log.add(f"\n== GAME {game_number} Turn {turn_n} ===")
        
        alive_players_counter = count_alive_players_and_log_state(board, log, players)
        
        board.log_board_state(log)
        log.add("")
        
        # If there are less than 2 alive players, end the game
        # (0 alive is quite unlikely, but possible):
        if alive_players_counter < 2:
            log.add(f"Only {alive_players_counter} alive player remains, game over")
            break
        
        # Players make their moves
        for player in players:
            # result will be "bankrupt" if player goes bankrupt
            result = player.make_a_move(board, players, dice, log)
            if result == BANKRUPT:
                datalog.add(f"{game_number}\t{player}\t{turn_n}")
    
    # Last thing to log in the game log: the final state of the board
    board.log_current_map(log)
    log.save()
    datalog.save()


def setup_players(board, dice):
    players = [Player(player_name, player_setting)
               for player_name, player_setting in GameSettings.players_list]
    
    if GameSettings.shuffle_players:
        dice.shuffle(players)     # dice has a thread-safe copy of random.shuffle
        
    # Set up players starting money according to the game settings:
    # Supports either a dict (per-player), or single value
    starting_money = GameSettings.starting_money
    if isinstance(starting_money, dict):
        for idx, player in enumerate(players):
            player.money = starting_money.get(idx, 0)  # default to 0 if not specified
    # If starting money is a single value, assign it to all players
    else:
        for player in players:
            player.money = starting_money
            
    # set up players initial properties
    for player_index, property_indices in GameSettings.starting_properties.items():
        for cell_index in property_indices:
            assign_property(players[player_index], board.cells[cell_index], board)
            
    return players


def setup_game(game_number, game_seed):
    log = Log(LogSettings.game_log_file, disabled=not LogSettings.keep_game_log)
    # First line in the game log: game number and seed
    log.add(f"\n\n= GAME {game_number} of {SimulationSettings.n_games} " +
            f"(seed = {game_seed}) =")
    # Initialize data log
    datalog = Log(LogSettings.data_log_file)
    # Initialize the board (plots, chance, community chest etc.)
    board = Board(GameSettings)
    # Set up dice (it creates a separate random generator with initial "game_seed",
    # to have thread-safe shuffling and dice throws)
    dice = Dice(game_seed, GameSettings.dice_count, GameSettings.dice_sides, log)
    # Shuffle chance and community chest cards
    # (using thread-safe random generator)
    dice.shuffle(board.chance.cards)
    dice.shuffle(board.chest.cards)
    return board, dice, log, datalog


def count_alive_players_and_log_state(board, log, players):
    """ Current player's position, money and net worth, looks like this:
         For example: Player 'Hero': $1220 (net $1320), at 21 (E1 Kentucky Avenue)"""
    alive_players_counter = 0
    for player_n, player in enumerate(players):
        if not player.is_bankrupt:
            alive_players_counter += 1
            
            log.add(f"- {player.name}: " +
                    f"${int(player.money)} (net ${player.net_worth()}), " +
                    f"at {player.position} ({board.cells[player.position].name})")
        else:
            log.add(f"- Player {player_n}, '{player.name}': Bankrupt")
    return alive_players_counter
