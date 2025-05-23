""" Functions to analyze the results of the simulation """

import pandas as pd

from monopoly.log_settings import LogSettings
from settings import SimulationSettings, GameSettings


class Analyzer:
    """ Functions to analyze games after the simulation is finished
    data is read from the bankruptcies.tsv log file
    """

    def __init__(self):
        self.df = pd.read_csv(LogSettings.BANKRUPTCIES_PATH, sep='\t')

    def run_all(self):
        """ Run all analysis functions """
        self.remaining_players()
        self.game_length()
        self.winning_rate()

    def remaining_players(self):
        """ number of games that had a clear winner, how many players remain at the end
        """
        grouped = self.df.groupby('game_number').size().reset_index(name='Losers')
        result = grouped['Losers'].value_counts().reset_index()
        result.columns = ['Losers', 'count']

        # {remaining players: games}
        remaining_players = {len(GameSettings.players_list) - row['Losers']: row['count'] for index, row in
                             result.iterrows()}
        # Add games with no losers (all players remained)
        remaining_players[len(GameSettings.players_list)] = \
            SimulationSettings.n_games - sum(remaining_players.values())

        # Games with a clear winner (just a single player remains)
        clear_winner = 0
        if 1 in remaining_players:
            clear_winner = remaining_players[1]
        print(f"Games that had clear winner: {clear_winner} / {SimulationSettings.n_games} " +
              f"({100 * clear_winner / SimulationSettings.n_games:.1f}%)")

        # Number of players by the end of simulation
        print(f"Number of remaining players after: {SimulationSettings.n_moves} turns:")
        for remaining, count in sorted(remaining_players.items()):
            print(f"  - {remaining}: {count} ({count * 100 / SimulationSettings.n_games:.1f}%)")

    def game_length(self):
        """ Median game length (for all finite games)
        """
        # Calculate median game length, which is the highest bankruptcy turn within a game
        grouped = self.df.groupby('game_number')
        filtered_groups = grouped.filter(lambda x: len(x) == len(GameSettings.players_list) - 1)
        lengths_df = filtered_groups.groupby('game_number')['turn'].max().reset_index()
        lengths = sorted(lengths_df["turn"].tolist())
        all_lengths = lengths + [SimulationSettings.n_moves
                                 for _ in range(SimulationSettings.n_games - len(lengths))]
        if lengths:
            print(f"Median game length (for finished games): {lengths[len(lengths) // 2]}")
        print(f"Median game length (for all games): {all_lengths[len(all_lengths) // 2]}")

        # Calculate average survival time (for those who goes bankrupt)
        survival_average = lengths_df["turn"].mean()
        print(f"Average survival time (for bankrupt players): {survival_average:.1f} turns")

    def winning_rate(self):
        """ Display winning (survival) rate of players
        """
        loses_counts = self.df.groupby('player_bankrupt').size().reset_index(name='count')

        # {player: games_survived}
        loses_dict = {row['player_bankrupt']: row['count'] for index, row in loses_counts.iterrows()}
        print("Players' survival rate:")

        for player in GameSettings.players_list:
            player_name = player[0]
            loses = loses_dict.get(player_name, 0)
            survivals = SimulationSettings.n_games - loses

            survival_rate = survivals / SimulationSettings.n_games
            margin = 1.96 * (survival_rate * (1 - survival_rate) / SimulationSettings.n_games) ** 0.5
            print(f"  - {player_name}: {survivals} " +
                  f"({survival_rate * 100:.1f} "
                  f"+- {margin * 100:.1f}%)")
