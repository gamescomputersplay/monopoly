from enum import Enum

OUT_WIDTH = 80
BANK_NAME = "BANK"


class MonopolyConfig:
    pass


class WriteMode(Enum):
    # Various raw data to output (to data.txt file)
    NONE = 1
    POPULAR_CELLS = 2
    GAME_LENGTH = 3  # Length of the game
    CELL_HEATMAP = 4  # Cells to land
    LOSERS = 5  # Who lost
    NET_WORTH = 6  # Monetary history of a game
    REMAINING_PLAYERS = 7


class SimulationConfig(MonopolyConfig):
    # simulation settings
    n_players = 4
    n_moves = 1000
    n_simulations = 1000
    seed = None  #
    shuffle_players = True
    real_time = False  # Allow step by step execution via space/enter key
    num_threads = 16
    # reporting settings
    show_progress_bar = True
    show_map = True  # only for 1 game: show final board map
    show_result = True  # only for 1 game: show final money score
    show_rem_players = True
    write_log = True  # write log with game events (log.txt file)
    write_mode = WriteMode.NET_WORTH


class GameRulesConfig(MonopolyConfig):
    # some game rules
    salary = 200
    luxury_tax = 100
    property_tax = 200
    jail_fine = 50
    house_limit = 32
    hotel_limit = 12
    allow_unequal_development = False  # default = False
    bankruptcy_goes_to_bank = False
    starting_money = 1500
    starting_money_per_player = None
    # starting_money_per_player = [1500, 1500, 1500, 1500]  # [1370, 1460, 1540, 1630] # None to disable


class PlayerBehaviourConfig(MonopolyConfig):
    # players behaviour settings
    def __init__(self, id):
        self.id = id

    build_expensive = False
    build_cheapest = False
    refuse_property = ""  # refuse to buy this group
    build_only_three_houses = False
    unspendable_cash = 0  # unspendable money
    unmortgage_coeff = 3  # repay mortgage if you have times this cash
    refuse_to_trade = False  # willing to trade property
    three_way_trade = True  # willing to trade property three-way
    build_randomly = False
