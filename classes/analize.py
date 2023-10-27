''' Functions to analyze the results of the simulation
'''

from settings import SimulationSettings, GameSettings, LogSettings

import pandas as pd

class Analyzer:
    ''' Functions to analized games after the simulation
    '''

    def __init__(self):
        self.df = pd.read_csv(LogSettings.data_log_file, sep='\t')

    def game_length(self):
        ''' Display results about how long the game was:
        How many finished, how many are still going, median length etc 
        '''
        grouped = self.df.groupby('game_number').size().reset_index(name='Loses Count')
        result = grouped['Loses Count'].value_counts().reset_index()
        filtered_result = result[result['Loses Count'] == len(GameSettings.players_list) - 1]
        games_that_ended = filtered_result.iloc[0]["count"]
        print(f"Games that had clear winner: {games_that_ended} / {SimulationSettings.n_games} " +
              f"({100 * games_that_ended / SimulationSettings.n_games:.1f}%)")
