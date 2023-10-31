''' Functions to analyze the results of the simulation
'''

from settings import SimulationSettings, GameSettings, LogSettings

import pandas as pd

class Analyzer:
    ''' Functions to analized games after the simulation
    '''

    def __init__(self):
        self.df = pd.read_csv(LogSettings.data_log_file, sep='\t')

    def remaining_players(self):
        ''' How many games had clear winner, how many players remain in tha end
        '''
        grouped = self.df.groupby('game_number').size().reset_index(name='Losers')
        result = grouped['Losers'].value_counts().reset_index()

        # {remaining players: games}
        remaining_players = {len(GameSettings.players_list) - row['Losers']: row['count']
                             for index, row in result.iterrows()}
        # Add games with no losers (all players remained)
        remaining_players[len(GameSettings.players_list)] = \
            SimulationSettings.n_games - sum(remaining_players.values())

        # Games with clear winner (1 player remains)
        clear_winner = remaining_players[1]
        print(f"Games that had clear winner: {clear_winner} / {SimulationSettings.n_games} " +
               f"({100 * clear_winner / SimulationSettings.n_games:.1f}%)")

        # Number of players by the end of simulation
        print(f"Number of remaining players after: {SimulationSettings.n_moves} turns:")
        for remaining, count in sorted(remaining_players.items()):
            print(f"  - {remaining}: {count} ({count * 100 / SimulationSettings.n_games:.1f}%)")

    def median_gamelength(self):
        ''' Median gamelength (for all an dfinite games)
        '''
        grouped = self.df.groupby('game_number')
        filtered_groups = grouped.filter(lambda x: len(x) == len(GameSettings.players_list) - 1)
        lengths_df = filtered_groups.groupby('game_number')['turn'].max().reset_index()
        lengths = lengths_df["turn"].tolist()
        all_lengths = lengths + [SimulationSettings.n_moves for _ in range(SimulationSettings.n_games - len(lengths))]
        if lengths:
            print(f"Median game length (for finished games): {lengths[len(lengths)//2]}")
        print(f"Median game length (for all games): {all_lengths[len(all_lengths)//2]}")
