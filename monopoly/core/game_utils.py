from typing import List

from monopoly.core.player import Player
from monopoly.log import Log
from settings import SimulationSettings


def assign_property(player, property_to_assign, board):
    """ Assigns a property to a player and updates the board state and check if a multiplier needs to be updated."""
    property_to_assign.owner = player
    player.owned.append(property_to_assign)
    board.recalculate_monopoly_multipliers(property_to_assign)
    player.update_lists_of_properties_to_trade(board)


def _check_end_conditions(players: List[Player], log: Log, game_number, turn_n) -> bool:
    """
    Return True when:
      1) fewer than 2 players remain, or
      2) all rich: all non-bankrupt players have > never_bankrupt_cash.
    Logs the reason before returning.
    """
    alive = [p for p in players if not p.is_bankrupt]
    n_alive = len(alive)

    # 1) fewer than 2 players left
    if n_alive < 2:
        log.add(f"Only {n_alive} alive player remains, game over")
        return True

    # 2) everyone is above the never_bankrupt_cash threshold
    threshold = SimulationSettings.never_bankrupt_cash
    if all(p.money > threshold for p in alive):
        log.add(f"== All Rich ==: GAME {game_number}, Turn {turn_n}: all non-bankrupt players have more than {threshold}$, this game will never end")
        return True
    return False


def log_players_and_board_state(board, log, players):
    """ Current player's position, money and net worth, looks like this:
         For example: Player 'Hero': $1220 (net $1320), at 21 (E1 Kentucky Avenue)"""
    for player_n, player in enumerate(players):
        if not player.is_bankrupt:

            log.add(f"- {player.name}: " +
                    f"${int(player.money)} (net ${player.net_worth()}), " +
                    f"at position {player.position} ({board.cells[player.position].name})")
        else:
            log.add(f"- Player {player_n}, '{player.name}': Bankrupt")
