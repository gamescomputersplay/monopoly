''' Config file for monopoly simulation
'''

class SimulationConfig():
    # Simulation settings

    # Number of moves to simulate
    # (if there are more than one player alive after then,
    # the game is considered to have no winner)
    n_moves = 10

    # Number of games to simulate
    n_simulations = 5

    # Random seed to start simulation with
    seed = 0
