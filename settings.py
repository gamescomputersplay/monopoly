''' Config file for monopoly simulation
'''

class SimulationSettings():
    ''' Simulation settings
    '''

    # Number of moves to simulate
    # (if there are more than one player alive after then,
    # the game is considered to have no winner)
    n_moves = 1000

    # Number of games to simulate
    n_games = 1000

    # Random seed to start simulation with
    seed = 0

    # Number of parallel processes to use in the simulation
    multi_process = 4

class LogSettings:
    ''' Settings for logging
    '''
    # Detailed log about all that is going on in th game:
    # movements, purchases, rent, cards, etc
    # Note that it takes about 5Mb per one 1000-turn game.
    # Might want to turn it off for large simulations
    keep_game_log = False
    game_log_file = "gamelog.txt"

    # Log that keeps information about on which turn which player went bunkrupt
    # Base info for all simulation analysis
    data_log_file = "datalog.txt"

class StandardPlayer:
    ''' Settings for a Standard Player
    '''
    # Amount of money player wants to keep unspent (money safety pillow)
    unspendable_cash = 200

    # Group of properties, player refuse to buy (set, as there may be several)
    ignore_property_groups = {}

    # Willing to participate in trades
    participates_in_trades = True

    # Only agree to trade if value difference is within these limits
    # (Asolute and relative)
    trade_max_diff_abs = 200 # More expensive - less espensive
    trade_max_diff_rel = 2 # More expensive / less espensive

class ExperimentPlayer(StandardPlayer):
    ''' Changed settings for the Experiement Player
    '''

class GameSettings():
    ''' Setting for the game (rules + player list)
    '''
    # Dice settings
    dice_count = 2
    dice_sides = 6

    # Initial money (a single integer if it is same
    # for everybody or a list of values for individual values)
    starting_money = 1500
    # starting_money = [1370, 1460, 1540, 1630]

    # Game mechanics settings
    salary = 200

    # Players and their behaviour settings
    players_list = [
        ("Experiment", ExperimentPlayer),
        ("Standard 1", StandardPlayer),
        ("Standard 2", StandardPlayer),
        ("Standard 3", StandardPlayer),
    ]

    # Randomly shuffle order of players each game
    shuffle_players = True

    # Mortgage value: how much cash player get's for mortgaging a property
    # Default is 0.5
    mortgage_value = 0.5
    # Mortgage fee is an extra they need to pay to unmortgage
    # Default is 0.1
    mortgage_fee = 0.1
