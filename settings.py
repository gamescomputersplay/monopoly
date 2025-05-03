""" Config file for monopoly simulation
"""
HERO = "Hero"
player2 = "Alice"
player3 = "Bob"
player4 = "Charly"


class SimulationSettings:
    # Number of moves to simulate
    # (if there are more than one player alive after then,
    # the game is considered to have no winner)
    n_moves = 1000

    # Number of games to simulate
    n_games = 5

    # Random seed to start simulation with
    seed = 0

    # Number of parallel processes to use in the simulation
    multi_process = 4

    # Cash that will be considered cannot go bankrupt, see this paper that estimates the probability that the game will last forever.
    # https://www.researchgate.net/publication/224123876_Estimating_the_probability_that_the_game_of_Monopoly_never_ends
    never_bankrupt_cash = 5000


class StandardPlayerSettings:
    # Amount of money the standard player wants to keep unspent (money safety pillow)
    unspendable_cash = 200

    # Group of properties that the player refuses to buy (a set, as there may be several)
    ignore_property_groups = {}

    # Willing to participate in trades
    participates_in_trades = True

    # Only agree to trade if the value difference is within these limits
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
        (HERO, HeroPlayerSettingsSettings),
        (player2, StandardPlayerSettings),
        (player3, StandardPlayerSettings),
        (player4, StandardPlayerSettings),
    ]

    # Randomly shuffle the order of players each game
    shuffle_players = True

    # Initial money (a single integer if it is the same for everybody or a dict of player names and cash)
    # for example, either starting_money = 1500 or a dictionary with player names as keys and int values
    starting_money = {
        HERO: 1500,
        player2: 1500,
        player3: 1500,
        player4: 1500
    }

    # Initial properties (a dictionary with player names as keys and a list of property numbers as values)
    # Property numbers correspond to indices in `board.cells`
    starting_properties = {
        HERO: [],
        player2: [],
        player3: [],
        player4: []
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
