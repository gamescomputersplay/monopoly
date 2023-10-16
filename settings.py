''' Config file for monopoly simulation
'''

class SimulationSettings():
    ''' Simulation settings
    '''

    # Number of moves to simulate
    # (if there are more than one player alive after then,
    # the game is considered to have no winner)
    n_moves = 10

    # Number of games to simulate
    n_simulations = 5

    # Random seed to start simulation with
    seed = 0

class StandardPlayer:
    ''' Settings for a Standard Player
    '''
    unspendable_cash = 500

class ExperimentPlayer(StandardPlayer):
    ''' Changed settings for the Experiement Player
    '''
    unspendable_cash = 0

class GameSettings():
    ''' Setting for the game (rules + player list)
    '''
    # Dice settings
    dice_count = 2
    dice_sides = 6

    # Game mechanics settings
    salary = 200

    # Players and their behaviour settings
    players_list = [
        ("Standard 1", StandardPlayer),
        ("Standard 2", StandardPlayer),
        ("Standard 3", StandardPlayer),
        ("Experimental", ExperimentPlayer),
    ]
