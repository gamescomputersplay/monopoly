""" Config file for monopoly simulation """
from dataclasses import dataclass
from typing import FrozenSet

HERO = "Hero"
PLAYER_2 = "Alice"
PLAYER_3 = "Bob"
PLAYER_4 = "Charly"


@dataclass(frozen=True)
class GameMechanics:
    # Houses and hotel available for development
    available_houses = 36
    available_hotels = 12
    salary = 200  # Passing Go salary
    luxury_tax = 100
    # Income tax (cash or share of net worth)
    income_tax = 200
    income_tax_percentage = .1
    mortgage_value = 0.5  # how much cash a player gets for mortgaging a property (Default is 0.5)
    mortgage_fee = 0.1  # The extra a player needs to pay to unmortgage (Default is 0.1)
    exit_jail_fine = 50  # Fine to get out of jail without rolling doubles
    free_parking_money = False  # Controversial house rule to collect fines on Free Parking and give to whoever lands there
    # Dice settings
    dice_count = 2
    dice_sides = 6
    

@dataclass(frozen=True)
class SimulationSettings:
    n_games: int = 1_000  # Number of games to simulate
    n_moves: int = 1000  # Max Number of moves per game
    seed: int = 0  # Random seed to start simulation with
    multi_process: int = 4  # Number of parallel processes to use in the simulation
    
    # Cash that will be considered cannot go bankrupt. See this paper that estimates the probability that the game
    # will last forever. https://www.researchgate.net/publication
    # /224123876_Estimating_the_probability_that_the_game_of_Monopoly_never_ends
    never_bankrupt_cash: int = 5000


@dataclass(frozen=True)
class StandardPlayerSettings:
    unspendable_cash: int = 200  # Amount of money the player wants to keep unspent (money safety pillow)
    ignore_property_groups: FrozenSet[str] = frozenset()  # Group of properties do not buy, i.e.{"RED", "GREEN"}
    
    is_willing_to_make_trades: bool = True
    # agree to trades if the value difference is within these limits:
    trade_max_diff_absolute: int = 200  # More expensive - less expensive
    trade_max_diff_relative: float = 2.0  # More expensive / less expensive


@dataclass(frozen=True)
class HeroPlayerSettings(StandardPlayerSettings):
    """ here you can change the settings of the hero (the Experimental Player) """
    # ignore_property_groups: FrozenSet[str] = frozenset({"GREEN"})


@dataclass(frozen=True)
class GameSettings:
    """ Setting for the game (rules and player list) """
    mechanics: GameMechanics = GameMechanics()  # the rules of the game
    
    # Players and their behavior settings
    players_list = [
        (HERO, HeroPlayerSettings),
        (PLAYER_2, StandardPlayerSettings),
        (PLAYER_3, StandardPlayerSettings),
        (PLAYER_4, StandardPlayerSettings),
    ]
    
    # Randomly shuffle the order of players each game
    shuffle_players = True
    
    # Initial money (a single integer if it is the same for everybody or a dict of player names and cash)
    # for example, either starting_money = 1500 or a dictionary with player names as keys and int values
    starting_money = {
        HERO: 1500,
        PLAYER_2: 1500,
        PLAYER_3: 1500,
        PLAYER_4: 1500
    }
    
    # Initial properties (a dictionary with player names as keys and a list of property numbers as values)
    # Property numbers correspond to indices in `board.cells`
    starting_properties = {
        HERO: [],
        PLAYER_2: [],
        PLAYER_3: [],
        PLAYER_4: []
    }
    