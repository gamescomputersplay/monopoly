# Copyright (C) 2021 Games Computers Play <https://github.com/gamescomputersplay> and nopeless and VikVelev
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Monopoly Simulator
# Videos with some research using this simulator:
# https://www.youtube.com/watch?v=6EJrZeN0jNI
# https://www.youtube.com/watch?v=Dx1ofZHGUtI

import random
import math
import time
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np
import progressbar
from statistics import mean

from src.util import *
from src.util.configs import OUT_WIDTH
from src import Board, Player


sim_conf = SimulationConfig()
log = Log()

# simulate one game
def one_game(run_number):

    game_rules = GameRulesConfig()
    player_behaviours = PlayerBehaviourConfig(0)

    # create players
    players = []
    # names = ["pl"+str(i) for i in range(nPlayers)]
    names = [player_names(i + 1) for i in range(sim_conf.n_players)]
    
    if sim_conf.shuffle_players:
        random.shuffle(names)
    
    for i in range(sim_conf.n_players):
        
        if game_rules.starting_money_per_player is None:
            starting_money = game_rules.starting_money
        else:
            starting_money = game_rules.starting_money_per_player[i]

        players.append(Player(names[i], starting_money, player_behaviours, sim_conf, log))
            
    # create board
    game_board = Board(players, game_rules, log)

    #  net_worth history first point
    if sim_conf.write_mode == WriteMode.NET_WORTH:
        net_worth_string = ""
        for player in players:
            net_worth_string += str(player.net_worth(game_board))
            if player != players[-1]:
                net_worth_string += "\t"
        log.write(net_worth_string, data=True)

    last_turn = None
    # game
    for i in range(sim_conf.n_moves):
        
        last_turn = i - 1

        if is_game_over(players):
            if sim_conf.write_mode == WriteMode.GAME_LENGTH:
                log.write(str(last_turn), data=True)
            
            break

        log.write("TURN "+str(i+1), 1)
        for player in players:
            if player.money > 0:
                log.write(f"{f'{player.name}: ':8} ${player.money} | position:"+str(player.position), 2)

        for player in players:
            if not is_game_over(players):  # Only continue if 2 or more players
                # returns True if player has to go again
                while player.make_a_move(game_board):
                    pass

        # track net_worth history of the game
        if sim_conf.write_mode == WriteMode.NET_WORTH:
            net_worth_string = "\n"
            for player in players:
                net_worth_string += str(player.net_worth(game_board))
                if player != players[-1]:
                    net_worth_string += "\t"
                
            log.write(net_worth_string, data=True)

    # tests
    # for player in players:
    # player.three_way_trade(gameBoard)

    # return final scores
    results = [players[i].get_money() for i in range(sim_conf.n_players)]

    # if it is an only simulation, print map and final score
    if sim_conf.n_simulations == 1 and sim_conf.show_map:
        game_board.printMap()

    if sim_conf.n_simulations == 1 and sim_conf.show_result:
        print(results)
    return results, last_turn, log.get_data()


def run_simulation(parallel=False):
    """run multiple game simulations"""
    results = []
    local_log = Log()

    with Pool(processes=sim_conf.num_threads) as pool:

        if sim_conf.show_progress_bar:
            widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.ETA()]
            pbar = progressbar.ProgressBar(widgets=widgets, term_width=OUT_WIDTH, maxval=sim_conf.n_simulations)
            pbar.start()

        results = []
        game_lengths = []
        i = 0
        tracking_winners = [0]*sim_conf.n_players
        
        if parallel:
            for game_result in pbwrapper(pool.imap(one_game, range(sim_conf.n_simulations)), sim_conf.n_simulations):
                if sim_conf.show_progress_bar:
                    pbar.update(i + 1)
                    i += 1
                results.append(game_result)

                # determine winner, and calculate average game length
                ending_net_worth, last_turn, _ = game_result
                if (last_turn != sim_conf.n_simulations - 2):
                    game_lengths.append(last_turn)
                
                winner_result_map = list(enumerate(ending_net_worth))
                winner_result_map = sorted(list(winner_result_map), reverse=True, key=lambda x: x[1])

                if (winner_result_map[1][1] < 0):
                    tracking_winners[winner_result_map[0][0]] += 1
            
                # write remaining players in a data log
                if sim_conf.write_mode == WriteMode.REMAINING_PLAYERS:
                    rem_players = sum([1 for r in result[-1] if r > 0])
                    local_log.write(str(rem_players), data=True)
        else:
            for i in pbwrapper(range(sim_conf.n_simulations), sim_conf.n_simulations):
            
                local_log.write("=" * 10 + " GAME " + str(i+1) + " " + "=" * 10 + "\n")
            
                # remaining players - add to the results list
                game_result = one_game(i)
                results.append(game_result)

                # determine winner
                ending_net_worth, last_turn, _ = game_result
                if (last_turn != sim_conf.n_simulations - 2):
                    game_lengths.append(last_turn)
                
                winner_result_map = list(enumerate(ending_net_worth))
                winner_result_map = sorted(list(winner_result_map), reverse=True, key=lambda x: x[1])

                if (winner_result_map[1][1] < 0):
                    tracking_winners[winner_result_map[0][0]] += 1
            
                # write remaining players in a data log
                if sim_conf.write_mode == WriteMode.REMAINING_PLAYERS:
                    rem_players = sum([1 for r in result[-1] if r > 0])
                    local_log.write(str(rem_players), data=True)

        if sim_conf.show_progress_bar:
            pbar.finish()
        
        print(f"Winners distribution (A, B, C, D ...) across {len(game_lengths)} games that finished:")
        print(tracking_winners)

        print(f"Average game length: {mean(game_lengths)} (excluding games that did not finish).")

    return results


if __name__ == "__main__":

    print("="*OUT_WIDTH)
    t = time.time()

    if sim_conf.seed != None:
        random.seed(sim_conf.seed)
    else:
        random.seed()

    print("Players:", sim_conf.n_players, " Turns:", sim_conf.n_moves,
          " Games:", sim_conf.n_simulations, " Seed:", sim_conf.seed)

    results_and_metrics = run_simulation(parallel=True)
    results = []
    metric_str = ""
    for result, game_length, metrics in results_and_metrics:
        results.append(result)
        metric_str += '\t'.join(metrics) + "\n"

    with open('data.txt', 'w') as f:
        f.write(metric_str)

    # analyze_results(results, sim_conf)
    # analyze_data()

    print("Done in {:.2f}s".format(time.time()-t))
