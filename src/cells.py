import random
from .util.configs import BANK_NAME


class Cell:
    """Generic Cell Class, base for other classes"""

    def __init__(self, name, log):
        self.name = name
        self.log = log
        self.group = ""

    def action(self, player, board):
        pass


class LuxuryTax(Cell):
    """Pay Luxury Tax cell (#38)"""

    def action(self, player, board):
        player.take_money(board.game_conf.luxury_tax, board, BANK_NAME)
        self.log.write(
            player.name + " pays Luxury Tax $" + str(board.game_conf.luxury_tax), 3
        )


class PropertyTax(Cell):
    """Pay Property Tax cell (200 or 10%) (#4)"""

    def action(self, player, board):
        toPay = min(board.game_conf.property_tax, player.net_worth(board) // 10)
        self.log.write(player.name + " pays Property Tax $" + str(toPay), 3)
        player.take_money(toPay, board, BANK_NAME)


class GoToJail(Cell):
    """Go to Jail (#30)"""

    def action(self, player, board):
        player.move_to(10)
        player.in_jail = True
        self.log.write(player.name + " goes to jail from Go To Jail ", 3)


class Chance(Cell):
    """Chance cards"""

    def action(self, player, board):
        # Get the card
        chanceCard = board.chanceCards.pop(0)

        # Actions for various cards

        # 0: Advance to St.Charle
        if chanceCard == 0:
            self.log.write(player.name + " gets chance card: Advance to St.Charle's", 3)
            if player.position >= 11:
                player.add_money(board.game_conf.salary)
                self.log.write(
                    player.name + " gets salary: $" + str(board.game_conf.salary), 3
                )
            player.position = 11
            self.log.write(player.name + " goes to " + str(board.b[11].name), 3)
            board.action(player, player.position)

        # 1: Get Out Of Jail Free
        elif chanceCard == 1:
            self.log.write(player.name + " gets chance card: Get Out Of Jail Free", 3)
            player.has_jail_card_chance = True

        # 2: Take a ride on the Reading
        elif chanceCard == 2:
            self.log.write(
                player.name + " gets chance card: Take a ride on the Reading", 3
            )
            if player.position >= 5:
                player.add_money(board.game_conf.salary)
                self.log.write(
                    player.name + " gets salary: $" + str(board.game_conf.salary), 3
                )
            player.position = 5
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )
            board.action(player, player.position)

        # 3: Move to the nearest railroad and pay double
        elif chanceCard == 3:
            self.log.write(
                player.name
                + " gets chance card: Move to the nearest railroad and pay double",
                3,
            )
            # Don't get salary, even if you pass GO (card doesnt say to do it)
            # Dont move is already on a rail.
            # Also, I assue advance means you should go to the nearest in fron of you, not behind
            player.position = (
                (player.position + 4) // 10 * 10 + 5
            ) % 40  # nearest railroad
            # twice for double rent, if needed
            board.action(player, player.position, special="from_chance")

        # 4: Advance to Illinois Avenue
        elif chanceCard == 4:
            self.log.write(
                player.name + " gets chance card: Advance to Illinois Avenue", 3
            )
            if player.position >= 24:
                player.add_money(board.game_conf.salary)
                self.log.write(
                    player.name + " gets salary: $" + str(board.game_conf.salary), 3
                )
            player.position = 24
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )
            board.action(player, player.position)

        # 5: Make general repairs to your property
        elif chanceCard == 5:
            self.log.write(
                player.name
                + " gets chance card: Make general repairs to your property",
                3,
            )
            player.make_repairs(board, "chance")

        # 6: Advance to GO
        elif chanceCard == 6:
            self.log.write(player.name + " gets chance card: Advance to GO", 3)
            player.add_money(board.game_conf.salary)
            self.log.write(
                player.name + " gets salary: $" + str(board.game_conf.salary), 3
            )
            player.position = 0
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )

        # 7: Bank pays you dividend $50
        elif chanceCard == 7:
            self.log.write(
                player.name + " gets chance card: Bank pays you dividend $50", 3
            )
            player.add_money(50)

        # 8: Pay poor tax $15
        elif chanceCard == 8:
            self.log.write(player.name + " gets chance card: Pay poor tax $15", 3)
            player.take_money(15, board, BANK_NAME)

        # 9: Advance to the nearest Utility and pay 10x dice
        elif chanceCard == 9:
            self.log.write(
                player.name
                + " gets chance card: Advance to the nearest Utility and pay 10x dice",
                3,
            )
            if player.position > 12 and player.position <= 28:
                player.position = 28
            else:
                player.position = 12
            board.action(player, player.position, special="from_chance")

        # 10: Go Directly to Jail
        elif chanceCard == 10:
            self.log.write(player.name + " gets chance card: Go Directly to Jail", 3)
            player.move_to(10)
            player.in_jail = True
            self.log.write(player.name + " goes to jail on Chance card", 3)

        # 11: You've been elected chairman. Pay each player $50
        elif chanceCard == 11:
            self.log.write(
                player.name
                + " gets chance card: You've been elected chairman. Pay each player $50",
                3,
            )
            for other_player in board.players:
                if other_player != player and not other_player.is_bankrupt:
                    player.take_money(50, board, BANK_NAME)
                    other_player.add_money(50)

        # 12: Advance to BoardWalk
        elif chanceCard == 12:
            self.log.write(player.name + " gets chance card: Advance to BoardWalk", 3)
            player.position = 39
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )
            board.action(player, player.position)

        # 13: Go back 3 spaces
        elif chanceCard == 13:
            self.log.write(player.name + " gets chance card: Go back 3 spaces", 3)
            player.position -= 3
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )
            board.action(player, player.position)

        # 14: Your building loan matures. Receive $150.
        elif chanceCard == 14:
            self.log.write(
                player.name
                + " gets chance card: Your building loan matures. Receive $150",
                3,
            )
            player.add_money(150)

        # 15: You have won a crossword competition. Collect $100
        elif chanceCard == 15:
            self.log.write(
                player.name
                + " gets chance card: You have won a crossword competition. Collect $100",
                3,
            )
            player.add_money(100)

        # Put the card back
        if chanceCard != 1:  # except GOOJF card
            board.chanceCards.append(chanceCard)


class Community(Cell):
    """Community Chest cards"""

    def action(self, player, board):
        # Get the card
        communityCard = board.communityCards.pop(0)

        # Actions for various cards

        # 0: Pay school tax $150
        if communityCard == 0:
            self.log.write(player.name + " gets community card: Pay school tax $150", 3)
            player.take_money(150, board, BANK_NAME)

        # 1: Opera night: collect $50 from each player
        if communityCard == 1:
            self.log.write(
                player.name + " Opera night: collect $50 from each player", 3
            )
            for other_player in board.players:
                if other_player != player and not other_player.is_bankrupt:
                    player.add_money(50)
                    other_player.take_money(50, board, BANK_NAME)

        # 2: You inherit $100
        if communityCard == 2:
            self.log.write(player.name + " gets community card: You inherit $100", 3)
            player.add_money(100)

        # 3: Pay hospital $100
        if communityCard == 3:
            self.log.write(player.name + " gets community card: Pay hospital $100", 3)
            player.take_money(100, board, BANK_NAME)

        # 4: Income tax refund $20
        if communityCard == 4:
            self.log.write(
                player.name + " gets community card: Income tax refund $20", 3
            )
            player.add_money(20)

        # 5: Go Directly to Jail
        elif communityCard == 5:
            self.log.write(player.name + " gets community card: Go Directly to Jail", 3)
            player.move_to(10)
            player.in_jail = True
            self.log.write(player.name + " goes to jail on Community card", 3)

        # 6: Get Out Of Jail Free
        elif communityCard == 6:
            self.log.write(
                player.name + " gets community card: Get Out Of Jail Free", 3
            )
            player.has_jail_card_community = True

        # 7: Second prize in beauty contest $10
        if communityCard == 7:
            self.log.write(
                player.name
                + " gets community card: Second prize in beauty contest $10",
                3,
            )
            player.add_money(10)

        # 8: You are assigned for street repairs
        elif communityCard == 8:
            self.log.write(
                player.name
                + " gets community card: You are assigned for street repairs",
                3,
            )
            player.make_repairs(board, "community")

        # 9: Bank error in your favour: $200
        if communityCard == 9:
            self.log.write(
                player.name + " gets community card: Bank error in your favour: $200", 3
            )
            player.add_money(200)

        # 10: Advance to GO
        elif communityCard == 10:
            self.log.write(player.name + " gets community card: Advance to GO", 3)
            player.add_money(board.game_conf.salary)
            self.log.write(
                player.name + " gets salary: $" + str(board.game_conf.salary), 3
            )
            player.position = 0
            self.log.write(
                player.name + " goes to " + str(board.b[player.position].name), 3
            )

        # 11: X-Mas fund matured: $100
        if communityCard == 11:
            self.log.write(
                player.name + " gets community card: X-Mas fund matured: $100", 3
            )
            player.add_money(100)

        # 12: Doctor's fee $50
        if communityCard == 12:
            self.log.write(player.name + " gets community card: Doctor's fee $50", 3)
            player.take_money(50, board, BANK_NAME)

        # 13: From sale of stock you get $45
        if communityCard == 13:
            self.log.write(
                player.name + " gets community card: From sale of stock you get $45", 3
            )
            player.add_money(45)

        # 14: Receive for services $25
        if communityCard == 14:
            self.log.write(
                player.name + " gets community card: Receive for services $25", 3
            )
            player.add_money(25)

        # 15: Life insurance matures, collect $100
        if communityCard == 15:
            self.log.write(
                player.name
                + " gets community card: Life insurance matures, collect $100",
                3,
            )
            player.add_money(100)

        # Put the card back
        if communityCard != 6:  # except GOOJF card
            board.communityCards.append(communityCard)


class Property(Cell):
    """Property Class (for Properties, Rails, Utilities)"""

    def __init__(self, name, cost_base, rent_base, cost_house, rent_house, group, log):
        self.name = name
        self.cost_base = cost_base
        self.rent_base = rent_base
        self.cost_house = cost_house
        self.rent_house = rent_house
        self.group = group
        self.log = log
        self.owner = ""
        self.isMortgaged = False
        self.isMonopoly = False
        self.hasHouses = 0

    def action(self, player, rent, board):
        """Player ended on a property"""

        # it's their property or mortgaged - do nothing
        if self.owner == player or self.isMortgaged:
            self.log.write("No rent this time", 3)
            return

        # Property up for sale
        elif self.owner == "":
            if player.wants_to_buy(self.cost_base, self.cost_base, self.group, board):
                self.log.write(
                    player.name
                    + " buys property "
                    + self.name
                    + " for $"
                    + str(self.cost_base),
                    3,
                )
                player.take_money(self.cost_base, board, BANK_NAME)
                self.owner = player
                board.recalculateAfterPropertyChange()
            else:
                current_auction_price = 10
                while True:
                    players_who_want_the_property = []
                    for board_player in board.players:
                        if board_player.wants_to_buy(
                            self.cost_base, current_auction_price, self.group, board
                        ):
                            players_who_want_the_property.append(board_player)
                    if len(players_who_want_the_property) == 1:
                        player_money_str = ""
                        for board_player in board.players:
                            player_money_str += (
                                board_player.name
                                + ": "
                                + str(board_player.money)
                                + ", "
                            )

                        self.log.write(
                            players_who_want_the_property[0].name
                            + " buys property "
                            + self.name
                            + " for $"
                            + str(current_auction_price),
                            3,
                        )
                        players_who_want_the_property[0].take_money(
                            self.cost_base, board, BANK_NAME
                        )
                        self.owner = players_who_want_the_property[0]
                        board.recalculateAfterPropertyChange()
                        # print(player_money_str)
                        # print(players_who_want_the_property[0].name + " buys property " +
                        #                self.name + " for $" + str(current_auction_price) + " valued at $" +
                        #                str(self.cost_base))
                        break
                    elif len(players_who_want_the_property) == 0:
                        self.log.write("property for auction, but nobody wanted it", 3)
                        break
                    else:
                        current_auction_price += 5
            return

        # someone else's property - pay the rent
        else:
            amount_taken = player.take_money(rent, board, self.owner)
            self.owner.add_money(amount_taken)
            self.log.write(
                player.name + " pays the rent $" + str(rent) + " to " + self.owner.name,
                3,
            )

    # mortgage the plot to the player / or sell the house
    def mortgage(self, player, board):
        """Sell hotel"""
        if self.hasHouses == 5:
            player.add_money(self.cost_house * 5 // 2)
            self.hasHouses = 0
            board.nHotels -= 1
            self.log.write(player.name + " sells hotel on " + self.name, 3)
        # Sell one house
        elif self.hasHouses > 0:
            player.add_money(self.cost_house // 2)
            self.hasHouses -= 1
            board.nHouses -= 1
            self.log.write(player.name + " sells house on " + self.name, 3)
        # Mortgage
        else:
            self.isMortgaged = True
            player.add_money(self.cost_base // 2)
            # log name of the plot and money player need to pay to get it back
            player.has_mortgages.append((self, int((self.cost_base // 2) * 1.1)))
            self.log.write(player.name + " mortgages " + self.name, 3)

    # unmortgage thr plot

    def unmortgage(self, player, board):
        # print (player.has_mortgages)
        for mortgage in player.has_mortgages:
            if mortgage[0] == self:
                thisMortgage = mortgage
        self.isMortgaged = False
        player.take_money(thisMortgage[1], board, BANK_NAME)
        player.has_mortgages.remove(thisMortgage)
        self.log.write(player.name + " unmortgages " + self.name, 3)
