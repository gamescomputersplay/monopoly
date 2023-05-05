from .cells import Property
from .util.configs import *
import random

BANK_NAME = "BANK"


class Player:
    """Player class"""

    def __init__(self, name, starting_money, behaviour, simulation_conf, log):
        self.name = name
        self.log = log
        self.position = 0
        self.money = starting_money
        self.consequent_doubles = 0
        self.in_jail = False
        self.days_in_jail = 0
        self.has_jail_card_chance = False
        self.has_jail_card_community = False
        self.is_bankrupt = False
        self.has_mortgages = []
        self.plots_wanted = []
        self.plots_offered = []
        self.plots_to_build = []
        self.cash_limit = behaviour.unspendable_cash
        self.behaviour = behaviour
        self.sim_conf = simulation_conf

    def __str__(self):
        return (
            "Player: "
            + self.name
            + ". Position: "
            + str(self.position)
            + ". Money: $"
            + str(self.money)
        )

    def get_money(self):
        return self.money

    def get_name(self):
        return self.name

    # add money (salary, receive rent etc)
    def add_money(self, amount):
        self.money += amount

    # subtract money (pay reny, buy property etc)
    def take_money(self, amount, board, action_origin):
        amount_taken = min(self.money, amount)
        self.money -= amount
        final_account_balance = self.money
        self.check_bankruptcy(board, action_origin)
        if self.is_bankrupt:
            amount_taken += self.money - final_account_balance
        else:
            amount_taken = amount
        return amount_taken

    # subtract money (pay reny, buy property etc)
    def move_to(self, position):
        self.position = position
        self.log.write(self.name + " moves to cell " + str(position), 3)

    # make a move procedure

    def make_a_move(self, board):
        goAgain = False

        # Only proceed if player is alive (not bankrupt)
        if self.is_bankrupt:
            return

        # to track the popular cells to land
        if self.sim_conf.write_mode == WriteMode.CELL_HEATMAP:
            self.log.write(str(self.position), data=True)

        self.log.write("Player " + self.name + " goes:", 2)

        # non-board actions: Trade, unmortgage, build
        # repay mortgage if you have X times more cashe than mortgage    cost
        while self.repay_mortgage(board):
            board.recalculateAfterPropertyChange()

        # build houses while you have pare cash
        while board.improveProperty(self, board, self.money - self.cash_limit):
            pass

        # Calculate property player wants to get and ready to give away
        if self.behaviour.refuse_to_trade:
            pass  # Experiement: do not trade
        elif not self.behaviour.refuse_to_trade:
            #  Make a trade
            if (
                not self.two_way_trade(board)
                and self.sim_conf.n_players >= 3
                and self.behaviour.three_way_trade
            ):
                self.three_way_trade(board)

        # roll dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self.log.write(
            self.name
            + " rolls "
            + str(dice1)
            + " and "
            + str(dice2)
            + " = "
            + str(dice1 + dice2),
            3,
        )

        # doubles
        if dice1 == dice2 and not self.in_jail:
            goAgain = True  # go again if doubles
            self.consequent_doubles += 1
            self.log.write(
                "it's a number " + str(self.consequent_doubles) + " double in a row", 3
            )
            if self.consequent_doubles == 3:  # but go to jail if 3 times in a row
                self.in_jail = True
                self.log.write(self.name + " goes to jail on consequtive doubles", 3)
                self.move_to(10)
                self.consequent_doubles = 0
                return False
        else:
            self.consequent_doubles = 0  # reset doubles counter

        # Jail situation:
        # Stay unless you roll doubles
        if self.in_jail:
            if self.has_jail_card_chance:
                self.has_jail_card_chance = False
                board.chanceCards.append(1)  # return the card
                self.log.write(
                    self.name + " uses the Chance GOOJF card to get out of jail", 3
                )
            elif self.has_jail_card_community:
                self.has_jail_card_community = False
                board.communityCards.append(6)  # return the card
                self.log.write(
                    self.name + " uses the Community GOOJF card to get out of jail", 3
                )
            elif dice1 != dice2:
                self.days_in_jail += 1
                if self.days_in_jail < 3:
                    self.log.write(self.name + " spends this turn in jail", 3)
                    return False  # skip turn in jail
                else:
                    self.take_money(
                        board.game_conf.jail_fine, board, BANK_NAME
                    )  # get out on fine
                    self.days_in_jail = 0
                    self.log.write(self.name + " pays fine and gets out of jail", 3)
            else:  # get out of jail on doubles
                self.log.write(self.name + " rolls double and gets out of jail", 3)
                self.days_in_jail = 0
                goAgain = False
        self.in_jail = False

        # move the piece
        self.position += dice1 + dice2

        # correction of the position if landed on GO or overshoot GO
        if self.position >= 40:
            # calculate correct cell
            self.position = self.position - 40
            # get salary for passing GO
            self.add_money(board.game_conf.salary)
            self.log.write(
                self.name + " gets salary: $" + str(board.game_conf.salary), 3
            )

        self.log.write(
            self.name
            + " moves to cell "
            + str(self.position)
            + ": "
            + board.b[self.position].name
            + (
                " (" + board.b[self.position].owner.name + ")"
                if type(board.b[self.position]) == Property
                and board.b[self.position].owner != ""
                else ""
            ),
            3,
        )

        # perform action of the cell player ended on
        board.action(self, self.position)

        if goAgain:
            self.log.write(self.name + " will go again now", 3)
            return True  # make a move again
        return False  # no extra move

    # get the cheapest mortgage property (name, price)

    def cheapest_mortgage(self):
        cheapest = False
        for mortgage in self.has_mortgages:
            if not cheapest or mortgage[1] < cheapest[1]:
                cheapest = mortgage
        return cheapest

    # Chance card make general repairs: 25/house 100/hotel
    def make_repairs(self, board, repairtype):
        repairCost = 0
        if repairtype == "chance":
            perHouse, perHotel = 25, 100
        else:
            perHouse, perHotel = 40, 115
        self.log.write(
            "Repair cost: $"
            + str(perHouse)
            + " per house, $"
            + str(perHotel)
            + " per hotel",
            3,
        )

        for plot in board.b:
            if type(plot) == Property and plot.owner == self:
                if plot.hasHouses == 5:
                    repairCost += perHotel
                else:
                    repairCost += plot.hasHouses * perHouse
        self.take_money(repairCost, board, BANK_NAME)
        self.log.write(self.name + " pays total repair costs $" + str(repairCost), 3)

    # check if player has negative money
    # if so, start selling stuff and mortgage plots
    # if that's not enough, player bankrupt

    def check_bankruptcy(self, board, bankrupter):
        if self.money < 0:
            self.log.write(self.name + " doesn't have enough cash", 3)
            while self.money < 0:
                worstAsset = board.choosePropertyToMortgageDowngrade(self)
                if worstAsset == False:
                    self.is_bankrupt = True
                    if (
                        bankrupter == BANK_NAME
                        or board.game_conf.bankruptcy_goes_to_bank
                    ):
                        board.sellAll(self)
                        self.log.write(
                            "The bank bankrupted "
                            + self.name
                            + ". Their property is back on the board",
                            3,
                        )
                    elif bankrupter == "noone":
                        self.log.write("that shouldn't have happened...", 3)
                    else:
                        board.sellAll(self, bankrupter)
                        self.log.write(
                            self.name
                            + " is now bankrupt. "
                            + bankrupter.name
                            + " bankrupted them",
                            3,
                        )
                    board.recalculateAfterPropertyChange()

                    # to track players who lost
                    if self.sim_conf.write_mode == WriteMode.LOSERS:
                        self.log.write(self.name, data=True)

                    # to track cells to land one last time
                    if self.sim_conf.write_mode == WriteMode.CELL_HEATMAP:
                        self.log.write(str(self.position), data=True)

                    return
                else:
                    board.b[worstAsset].mortgage(self, board)
                    board.recalculateAfterPropertyChange()

    # Calculate net worth of a player (for property tax)
    def net_worth(self, board):
        worth = self.money
        for plot in board.b:
            if type(plot) == Property and plot.owner == self:
                if plot.isMortgaged:
                    worth += plot.cost_base // 2
                else:
                    worth += plot.cost_base
                    worth += plot.cost_house * plot.hasHouses
        return worth

    # Behaviours

    # if there is a mortgage with pay less then current money // behaveUnmortgageCoeff
    # repay the mortgage
    def repay_mortgage(self, board):
        cheapest = self.cheapest_mortgage()
        if cheapest and self.money > cheapest[1] * self.behaviour.unmortgage_coeff:
            cheapest[0].unmortgage(self, board)
            return True
        return False

    # does player want to buy a property
    def wants_to_buy(self, base_cost, cost, group, board):
        if self.name == "exp" and group == expRefuseProperty:
            self.log.write(
                self.name + " refuses to buy " + expRefuseProperty + " property", 3
            )
            return False

        # If a player already has a property then they
        # are willing to pay up to double the value of
        # the property in an auction in order to have
        # that property. Otherwise they are only
        # willing to pay up to the bank value of the
        # property.
        groups = {}
        for plot in board.b:
            if plot.group == group:
                if plot.group in groups:
                    groups[plot.group][0] += 1
                else:
                    groups[plot.group] = [1, 0]
                if plot.owner == self:
                    groups[plot.group][1] += 1
        if groups[group][1] >= 1:
            if self.money > cost + self.cash_limit and cost <= base_cost * 2:
                return True
            else:
                return False
        else:
            if self.money > cost + self.cash_limit and cost <= base_cost:
                return True
            else:
                return False

    # Look for and perform a two-way trade
    def two_way_trade(self, board):
        trade_happened = False
        for IWant in self.plots_wanted[::-1]:
            ownerOfWanted = board.b[IWant].owner
            if ownerOfWanted == "":
                continue
            # Find a match betwee what I want / they want / I have / they have
            for TheyWant in ownerOfWanted.plots_wanted[::-1]:
                if (
                    TheyWant in self.plots_offered
                    and board.b[IWant].group != board.b[TheyWant].group
                ):  # prevent exchanging in groups of 2
                    self.log.write(
                        "Trade match: "
                        + self.name
                        + " wants "
                        + board.b[IWant].name
                        + ", and "
                        + ownerOfWanted.name
                        + " wants "
                        + board.b[TheyWant].name,
                        3,
                    )

                    # Compensate that one plot is cheaper than another one
                    if board.b[IWant].cost_base < board.b[TheyWant].cost_base:
                        cheaperOne, expensiveOne = IWant, TheyWant
                    else:
                        cheaperOne, expensiveOne = TheyWant, IWant
                    priceDiff = (
                        board.b[expensiveOne].cost_base - board.b[cheaperOne].cost_base
                    )
                    self.log.write("Price difference is $" + str(priceDiff), 3)

                    # make sure they they can pay the money
                    if (
                        board.b[cheaperOne].owner.money - priceDiff
                        >= board.b[cheaperOne].owner.cash_limit
                    ):
                        self.log.write(
                            "We have a deal. Money and property changed hands", 3
                        )
                        # Money and property change hands
                        board.b[cheaperOne].owner.take_money(priceDiff, board, "noone")
                        board.b[expensiveOne].owner.add_money(priceDiff)
                        board.b[cheaperOne].owner, board.b[expensiveOne].owner = (
                            board.b[expensiveOne].owner,
                            board.b[cheaperOne].owner,
                        )
                        trade_happened = True

                        # recalculated wanted and offered plots
                        board.recalculateAfterPropertyChange()
        return trade_happened

    def three_way_trade(self, board):
        """Look for and perform a three-way trade"""
        trade_happened = False
        for wanted1 in self.plots_wanted[::-1]:
            first_owner_of_wanted = board.b[wanted1].owner
            if first_owner_of_wanted == "":
                continue
            for wanted2 in first_owner_of_wanted.plots_wanted[::-1]:
                second_owner_of_wanted = board.b[wanted2].owner
                if second_owner_of_wanted == "":
                    continue
                for wanted3 in second_owner_of_wanted.plots_wanted[::-1]:
                    if wanted3 in self.plots_offered:
                        # check we have property from 3 groups
                        # otherwise someone can give and take brown or indigo at the same time
                        check_diff_group = set()
                        check_diff_group.add(board.b[wanted1].group)
                        check_diff_group.add(board.b[wanted2].group)
                        check_diff_group.add(board.b[wanted3].group)
                        if len(check_diff_group) < 3:
                            continue

                        topay1 = board.b[wanted1].cost_base - board.b[wanted3].cost_base
                        topay2 = board.b[wanted2].cost_base - board.b[wanted1].cost_base
                        topay3 = board.b[wanted3].cost_base - board.b[wanted2].cost_base
                        if (
                            self.money - topay1 > self.cash_limit
                            and first_owner_of_wanted.money - topay2
                            > first_owner_of_wanted.cash_limit
                            and first_owner_of_wanted.money - topay3
                            > second_owner_of_wanted.cash_limit
                        ):
                            self.log.write("Three way trade: ", 3)
                            self.log.write(
                                self.name
                                + " gives "
                                + board.b[wanted3].name
                                + " and $"
                                + str(topay1)
                                + " for "
                                + board.b[wanted1].name,
                                4,
                            )
                            self.log.write(
                                first_owner_of_wanted.name
                                + " gives "
                                + board.b[wanted1].name
                                + " and $"
                                + str(topay2)
                                + " for "
                                + board.b[wanted2].name,
                                4,
                            )
                            self.log.write(
                                second_owner_of_wanted.name
                                + " gives "
                                + board.b[wanted2].name
                                + " and $"
                                + str(topay3)
                                + " for "
                                + board.b[wanted3].name,
                                4,
                            )
                            # Money and property change hands
                            board.b[wanted1].owner = self
                            board.b[wanted2].owner = first_owner_of_wanted
                            board.b[wanted3].owner = second_owner_of_wanted
                            self.take_money(
                                topay1, board, "noone"
                            )  # guaranteed to have enough money
                            first_owner_of_wanted.take_money(topay2, board, "noone")
                            second_owner_of_wanted.take_money(topay3, board, "noone")
                            tradeHappened = True
                            # recalculated wanted and offered plots
                            board.recalculateAfterPropertyChange()
        return trade_happened
