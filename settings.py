""" Config file for monopoly simulation
"""


class SimulationSettings:
    # Number of moves to simulate
    # (if there are more than one player alive after then,
    # the game is considered to have no winner)
    n_moves = 1000

    # Number of games to simulate
    n_games = 10000

    # Random seed to start simulation with
    seed = 0

    # Number of parallel processes to use in the simulation
    multi_process = 4


class LogSettings:
    # Detailed log about all that is going on in the game:
    # movements, purchases, rent, cards, etc.
    # Note that it takes about 5Mb per one 1000-turn game.
    # Might want to turn it off for large simulations
    keep_game_log = True
    game_log_file = "gamelog.txt"

    # Log that keeps information about on which turn which player went bankrupt
    # Base info for all simulation analysis
    data_log_file = "datalog.txt"


class StandardPlayerSettings:
    # Amount of money player wants to keep unspent (money safety pillow)
    unspendable_cash = 200

    # Group of properties that the player refuses to buy (a set, as there may be several)
    ignore_property_groups = {}

    # Willing to participate in trades
    participates_in_trades = True

    # Only agree to trade if value difference is within these limits
    # (Absolute and relative)
    trade_max_diff_abs = 200  # More expensive - less expensive
    trade_max_diff_rel = 2  # More expensive / less expensive


class HeroPlayerSettingsSettings(StandardPlayerSettings):
    """ here you can change the settings of the hero (the Experimental Player)
    """


class GameSettings:
    """ Setting for the game (rules and player list)
    """
    # Dice settings
    dice_count = 2
    dice_sides = 6

    # Players and their behavior settings
    players_list = [
        ("Hero", HeroPlayerSettingsSettings),
        ("Alice", StandardPlayerSettings),
        # ("BoB", StandardPlayerSettings),
        # ("Charly", StandardPlayerSettings),
    ]

    # Randomly shuffle order of players each game
    shuffle_players = False

    # Initial money (a single integer if it is the same for everybody or a list of values for individual values)
    # for example, either starting_money = 1500, or starting_money = [1600,1500,1400,1300]
    starting_money = [1200, 200]

    # Initial properties (a dictionary with player position (0,1,2,3) as keys and list of property numbers as values)
    # Property numbers correspond to indices in `board.cells`
    # Maroons (a.k.a. Pinks): 11 = St. Charles Place, 13 = States Avenue, 14 = Virginia Avenue
    # Greens: 31 = Pacific Avenue, 32 = North Carolina Avenue, 34 = Pennsylvania Avenue
    starting_properties = {
        0: [11, 13, 14],  # hero gets the Pinks: C1 St. Charles Place", "C2 States Avenue", "C3 Virginia Avenue
        1: [31, 32, 34]  # opp gets the Greens: G1 Pacific Avenue", "G2 North Carolina Avenue", "G3 Pennsylvania Avenue
    }

    # Houses and hotel available for development
    available_houses = 36
    available_hotels = 12

    # Game mechanics settings

    # Passing Go salary
    salary = 200

    # Luxury tax
    luxury_tax = 100

    # Income tax (cash or share of net worth)
    income_tax = 200
    income_tax_percentage = .1

    # Mortgage value: how much cash a player gets for mortgaging a property
    # Default is 0.5
    mortgage_value = 0.5
    # The Mortgage fee is an extra they need to pay to unmortgage
    # Default is 0.1
    mortgage_fee = 0.1

    # Fine to get out of jail without rolling doubles
    exit_jail_fine = 50

    # Controversial house rule to collect fines on
    # Free Parking and give to whoever lands there
    free_parking_money = False
