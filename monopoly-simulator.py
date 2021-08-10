# Copyright (C) 2021 Games Computers Play <https://github.com/gamescomputersplay> and nopeless
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Monopoly Simulator

import random
import math
import time
import matplotlib.pyplot as plt
import numpy as np
import progressbar

# simulation settings
nPlayers = 4
nMoves = 1000
nSimulations = 1000
seed = ""  # "" for none
shufflePlayers = True

# some game rules
settingStartingMoney = 1500
settingsSalary = 200
settingsLuxuryTax = 75
settingsPropertyTax = 200
settingJailFine = 50
settingHouseLimit = 32
settingHotelLimit = 12
settingsAllowUnEqualDevelopment = False  # default = False

# players behaviour settings
behaveUnspendableCash = 0  # Money I want to will have left after buying stuff
behaveUnmortgageCoeff = 3  # repay mortgage if you have times this cash
behaveDoTrade = True  # willing to trade property
behaveDoThreeWayTrade = True  # willing to trade property three-way
behaveBuildCheapest = False
behaveBuildRandom = False

# experimental settings
# for a player named exp:
expRefuseTrade = False  # refuse to trade property
expRefuseProperty = ""  # refuse to buy this group
expHouseBuildLimit = 100  # limit houses built
expUnspendableCash = 0  # unspendable money
expBuildCheapest = False
expBuildExpensive = False
expBuildThree = False

# reporting settings
OUT_WIDTH = 80
showProgressBar = True
showMap = False  # only for 1 game: show final board map
showResult = True  # only for 1 game: show final money score
showRemPlayers = True
writeLog = False  # write log with game events (log.txt file)

# Various raw data to output (to data.txt file)
# writeData = "none"
# writeData = "popularCells" # Cells to land
# writeData = "lastTurn" # Length of the game
writeData = "losersNames"  # Who lost
# writeData = "netWorth" # history of a game
# writeData = "remainingPlayers"


class Log:

    def __init__(self):
        self.datafs = open("data.txt", "w")
        self.fs = open("log.txt", "w")

    def close(self):
        self.datafs.close()
        self.fs.close()

    def write(self, text, level=0, data=False):
        if data and writeData:
            self.datafs.write(text+"\n")
            return
        if writeLog:
            if level < 2:
                self.fs.write("\n"*(2-level))
            self.fs.write("\t"*level+text+"\n")


class Player:
    """Player class"""

    def __init__(self, name):
        self.name = name
        self.position = 0
        self.money = settingStartingMoney
        self.consequentDoubles = 0
        self.inJail = False
        self.daysInJail = 0
        self.hasJailCardChance = False
        self.hasJailCardCommunity = False
        self.isBankrupt = False
        self.hasMortgages = []
        self.plotsWanted = []
        self.plotsOffered = []
        self.plotsToBuild = []
        self.cashLimit = expUnspendableCash if name == "exp" else behaveUnspendableCash

    def __str__(self):
        return "Player: "+self.name + \
               ". Position: "+str(self.position) + \
               ". Money: $"+str(self.money)

    # some getters and setters

    def getMoney(self):
        return self.money

    def getName(self):
        return self.name

    # add money (salary, receive rent etc)
    def addMoney(self, amount):
        self.money += amount

    # subtract money (pay reny, buy property etc)
    def takeMoney(self, amount):
        self.money -= amount

    # subtract money (pay reny, buy property etc)
    def moveTo(self, position):
        self.position = position
        log.write(self.name+" moves to cell "+str(position), 3)

    # make a move procedure

    def makeAMove(self, board):

        goAgain = False

        # Only proceed if player is alive (not bankrupt)
        if self.isBankrupt:
            return

        # to track the popular cells to land
        if writeData == "popularCells":
            log.write(str(self.position), data=True)

        log.write("Player "+self.name+" goes:", 2)

        # non-board actions: Trade, unmortgage, build
        # repay mortgage if you have X times more cashe than mortgage cost
        while self.repayMortgage():
            board.recalculateAfterPropertyChange()

        # build houses while you have pare cash
        while board.improveProperty(self, self.money-self.cashLimit):
            pass

        # Calculate property player wants to get and ready to give away
        if expRefuseTrade and self.name == "exp":
            pass  # Experiement: do not trade
        elif behaveDoTrade:
            #  Make a trade
            if not self.twoWayTrade(board) and nPlayers >= 3 and behaveDoThreeWayTrade:
                self.threeWayTrade(board)

        # roll dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        log.write(self.name+" rolls "+str(dice1)+" and " +
                  str(dice2)+" = "+str(dice1+dice2), 3)

        # doubles
        if dice1 == dice2 and not self.inJail:
            goAgain = True  # go again if doubles
            self.consequentDoubles += 1
            log.write("it's a number " +
                      str(self.consequentDoubles) + " double in a row", 3)
            if self.consequentDoubles == 3:  # but go to jail if 3 times in a row
                self.inJail = True
                log.write(self.name+" goes to jail on consequtive doubles", 3)
                self.moveTo(10)
                self.consequentDoubles = 0
                return False
        else:
            self.consequentDoubles = 0  # reset doubles counter

        # Jail situation:
        # Stay unless you roll doubles
        if self.inJail:
            if self.hasJailCardChance:
                self.hasJailCardChance = False
                board.chanceCards.append(1)  # return the card
                log.write(
                    self.name+" uses the Chance GOOJF card to get out of jail", 3)
            elif self.hasJailCardCommunity:
                self.hasJailCardCommunity = False
                board.communityCards.append(6)  # return the card
                log.write(
                    self.name+" uses the Community GOOJF card to get out of jail", 3)
            elif dice1 != dice2:
                self.daysInJail += 1
                if self.daysInJail < 3:
                    log.write(self.name+" spends this turn in jail", 3)
                    return False  # skip turn in jail
                else:
                    self.takeMoney(settingJailFine)  # get out on fine
                    self.daysInJail = 0
                    log.write(self.name+" pays fine and gets out of jail", 3)
            else:  # get out of jail on doubles
                log.write(self.name+" rolls double and gets out of jail", 3)
                self.daysInJail = 0
                goAgain = False
        self.inJail = False

        # move the piece
        self.position += dice1+dice2

        # correction of the position if landed on GO or overshoot GO
        if self.position >= 40:
            # calculate correct cell
            self.position = self.position - 40
            # get salary for passing GO
            self.addMoney(settingsSalary)
            log.write(self.name+" gets salary: $"+str(settingsSalary), 3)

        log.write(self.name+" moves to cell "+str(self.position) + ": "+board.b[self.position].name +
                  (" ("+board.b[self.position].owner.name+")" if type(board.b[self.position]) == Property and board.b[self.position].owner != "" else ""), 3)

        # perform action of the cell player ended on
        board.action(self, self.position)

        # check if bankrupt after the action
        self.checkBankrupcy(board)

        if goAgain:
            log.write(self.name+" will go again now", 3)
            return True  # make a move again
        return False  # no extra move

    # get the cheapest mortgage property (name, price)

    def cheapestMotgage(self):
        cheapest = False
        for mortgage in self.hasMortgages:
            if not cheapest or mortgage[1] < cheapest[1]:
                cheapest = mortgage
        return cheapest

    # Chance card make general repairs: 25/house 100/hotel
    def makeRepairs(self, board, repairtype):
        repairCost = 0
        if repairtype == "chance":
            perHouse, perHotel = 25, 100
        else:
            perHouse, perHotel = 40, 115
        log.write("Repair cost: $"+str(perHouse) +
                  " per house, $"+str(perHotel)+" per hotel", 3)

        for plot in board.b:
            if type(plot) == Property and plot.owner == self:
                if plot.hasHouses == 5:
                    repairCost += perHotel
                else:
                    repairCost += plot.hasHouses*perHouse
        self.takeMoney(repairCost)
        log.write(self.name+" pays total repair costs $"+str(repairCost), 3)

    # check if player has negative money
    # if so, start selling stuff and mortgage plots
    # if that's not enough, player bankrupt

    def checkBankrupcy(self, board):
        if self.money < 0:
            log.write(self.name+" doesn't have enough cash", 3)
            while self.money < 0:
                worstAsset = board.choosePropertyToMortgageDowngrade(self)
                if worstAsset == False:
                    self.isBankrupt = True
                    board.sellAll(self)
                    board.recalculateAfterPropertyChange()
                    log.write(
                        self.name+" is now bankrupt. Their property is back on board.", 3)

                    # to track players who lost
                    if writeData == "losersNames":
                        log.write(self.name, data=True)

                    # to track cells to land one last time
                    if writeData == "popularCells":
                        log.write(str(self.position), data=True)

                    return
                else:
                    board.b[worstAsset].mortgage(self, board)
                    board.recalculateAfterPropertyChange()

    # Calculate net worth of a player (for property tax)
    def netWorth(self, board):
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
    def repayMortgage(self):
        cheapest = self.cheapestMotgage()
        if cheapest and self.money > cheapest[1] * behaveUnmortgageCoeff:
            cheapest[0].unmortgage(self)
            return True
        return False

    # does player want to buy a property
    def wantsToBuy(self, cost, group):

        if self.name == "exp" and group == expRefuseProperty:
            log.write(self.name+" refuses to buy " +
                      expRefuseProperty+" property", 3)
            return False
        if self.money > cost + self.cashLimit:  # leave some money just in case
            return True
        else:
            return False

    # Look for and perform a two-way trade
    def twoWayTrade(self, board):
        tradeHappened = False
        for IWant in self.plotsWanted[::-1]:
            ownerOfWanted = board.b[IWant].owner
            if ownerOfWanted == "":
                continue
            # Find a match betwee what I want / they want / I have / they have
            for TheyWant in ownerOfWanted.plotsWanted[::-1]:
                if TheyWant in self.plotsOffered \
                   and board.b[IWant].group != board.b[TheyWant].group:  # prevent exchanging in groups of 2
                    log.write("Trade match: " + self.name + " wants " + board.b[IWant].name +
                              ", and " + ownerOfWanted.name + " wants " + board.b[TheyWant].name, 3)

                    # Compensate that one plot is cheaper than another one
                    if board.b[IWant].cost_base < board.b[TheyWant].cost_base:
                        cheaperOne, expensiveOne = IWant, TheyWant
                    else:
                        cheaperOne, expensiveOne = TheyWant, IWant
                    priceDiff = board.b[expensiveOne].cost_base - \
                        board.b[cheaperOne].cost_base
                    log.write("Price difference is $" + str(priceDiff), 3)

                    # make sure they they can pay the money
                    if board.b[cheaperOne].owner.money - priceDiff >= board.b[cheaperOne].owner.cashLimit:
                        log.write(
                            "We have a deal. Money and property changed hands", 3)
                        # Money and property change hands
                        board.b[cheaperOne].owner.takeMoney(priceDiff)
                        board.b[expensiveOne].owner.addMoney(priceDiff)
                        board.b[cheaperOne].owner, board.b[expensiveOne].owner = \
                            board.b[expensiveOne].owner, board.b[cheaperOne].owner
                        tradeHappened = True

                        # recalculated wanted and offered plots
                        board.recalculateAfterPropertyChange()
        return tradeHappened

    def threeWayTrade(self, board):
        """Look for and perform a three-way trade"""
        tradeHappened = False
        for wanted1 in self.plotsWanted[::-1]:
            ownerOfWanted1 = board.b[wanted1].owner
            if ownerOfWanted1 == "":
                continue
            for wanted2 in ownerOfWanted1.plotsWanted[::-1]:
                ownerOfWanted2 = board.b[wanted2].owner
                if ownerOfWanted2 == "":
                    continue
                for wanted3 in ownerOfWanted2.plotsWanted[::-1]:
                    if wanted3 in self.plotsOffered:

                        # check we have property from 3 groups
                        # otherwise someone can give and take brown or indigo at the same time
                        checkDiffGroup = set()
                        checkDiffGroup.add(board.b[wanted1].group)
                        checkDiffGroup.add(board.b[wanted2].group)
                        checkDiffGroup.add(board.b[wanted3].group)
                        if len(checkDiffGroup) < 3:
                            continue

                        topay1 = board.b[wanted1].cost_base - \
                            board.b[wanted3].cost_base
                        topay2 = board.b[wanted2].cost_base - \
                            board.b[wanted1].cost_base
                        topay3 = board.b[wanted3].cost_base - \
                            board.b[wanted2].cost_base
                        if self.money-topay1 > self.cashLimit and \
                           ownerOfWanted1.money-topay2 > ownerOfWanted1.cashLimit and \
                           ownerOfWanted2.money-topay3 > ownerOfWanted2.cashLimit:
                            log.write("Tree way trade: ", 3)
                            log.write(self.name + " gives " + board.b[wanted3].name + " and $" + str(
                                topay1) + " for " + board.b[wanted1].name, 4)
                            log.write(ownerOfWanted1.name + " gives " + board.b[wanted1].name + " and $" + str(
                                topay2) + " for " + board.b[wanted2].name, 4)
                            log.write(ownerOfWanted2.name + " gives " + board.b[wanted2].name + " and $" + str(
                                topay3) + " for " + board.b[wanted3].name, 4)
                            # Money and property change hands
                            board.b[wanted1].owner = self
                            board.b[wanted2].owner = ownerOfWanted1
                            board.b[wanted3].owner = ownerOfWanted2
                            self.takeMoney(topay1)
                            ownerOfWanted1.takeMoney(topay2)
                            ownerOfWanted2.takeMoney(topay3)
                            tradeHappened = True
                            # recalculated wanted and offered plots
                            board.recalculateAfterPropertyChange()


class Cell:
    """Generic Cell Class, base for other classes"""

    def __init__(self, name):
        self.name = name
        self.group = ""

    def action(self, player):
        pass


class LuxuryTax(Cell):
    """Pay Luxury Tax cell (#38)"""

    def action(self, player):
        player.takeMoney(settingsLuxuryTax)
        log.write(player.name+" pays Luxury Tax $"+str(settingsLuxuryTax), 3)


class PropertyTax(Cell):
    """Pay Property Tax cell (200 or 10%) (#4)"""

    def action(self, player, board):
        toPay = min(settingsPropertyTax, player.netWorth(board)//10)
        log.write(player.name+" pays Property Tax $"+str(toPay), 3)
        player.takeMoney(toPay)


class GoToJail(Cell):
    """Go to Jail (#30)"""

    def action(self, player):
        player.moveTo(10)
        player.inJail = True
        log.write(player.name+" goes to jail from Go To Jail ", 3)


class Chance(Cell):
    """Chance cards"""

    def action(self, player, board):

        # Get the card
        chanceCard = board.chanceCards.pop(0)

        # Actions for various cards

        # 0: Advance to St.Charle
        if chanceCard == 0:
            log.write(player.name+" gets chance card: Advance to St.Charle's", 3)
            if player.position >= 11:
                player.addMoney(settingsSalary)
                log.write(player.name+" gets salary: $"+str(settingsSalary), 3)
            player.position = 11
            log.write(player.name+" goes to "+str(board.b[11].name), 3)
            board.action(player, player.position)

        # 1: Get Out Of Jail Free
        elif chanceCard == 1:
            log.write(player.name+" gets chance card: Get Out Of Jail Free", 3)
            player.hasJailCardChance = True

        # 2: Take a ride on the Reading
        elif chanceCard == 2:
            log.write(
                player.name+" gets chance card: Take a ride on the Reading", 3)
            if player.position >= 5:
                player.addMoney(settingsSalary)
                log.write(player.name+" gets salary: $"+str(settingsSalary), 3)
            player.position = 5
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 3: Move to the nearest railroad and pay double
        elif chanceCard == 3:
            log.write(
                player.name+" gets chance card: Move to the nearest railroad and pay double", 3)
            # Don't get salary, even if you pass GO (card doesnt say to do it)
            # Dont move is already on a rail.
            # Also, I assue advance means you should go to the nearest in fron of you, not behind
            player.position = ((player.position+4)//10*10 +
                               5) % 40  # nearest railroad
            # twice for double rent, if needed
            board.action(player, player.position, special="from_chance")

        # 4: Advance to Illinois Avenue
        elif chanceCard == 4:
            log.write(
                player.name+" gets chance card: Advance to Illinois Avenue", 3)
            if player.position >= 24:
                player.addMoney(settingsSalary)
                log.write(player.name+" gets salary: $"+str(settingsSalary), 3)
            player.position = 24
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 5: Make general repairs to your property
        elif chanceCard == 5:
            log.write(
                player.name+" gets chance card: Make general repairs to your property", 3)
            player.makeRepairs(board, "chance")

        # 6: Advance to GO
        elif chanceCard == 6:
            log.write(player.name+" gets chance card: Advance to GO", 3)
            player.addMoney(settingsSalary)
            log.write(player.name+" gets salary: $"+str(settingsSalary), 3)
            player.position = 0
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)

        # 7: Bank pays you dividend $50
        elif chanceCard == 7:
            log.write(
                player.name+" gets chance card: Bank pays you dividend $50", 3)
            player.addMoney(50)

        # 8: Pay poor tax $15
        elif chanceCard == 8:
            log.write(player.name+" gets chance card: Pay poor tax $15", 3)
            player.takeMoney(15)

        # 9: Advance to the nearest Utility and pay 10x dice
        elif chanceCard == 9:
            log.write(
                player.name+" gets chance card: Advance to the nearest Utility and pay 10x dice", 3)
            if player.position > 12 and player.position <= 28:
                player.position = 28
            else:
                player.position = 12
            board.action(player, player.position, special="from_chance")

        # 10: Go Directly to Jail
        elif chanceCard == 10:
            log.write(player.name+" gets chance card: Go Directly to Jail", 3)
            player.moveTo(10)
            player.inJail = True
            log.write(player.name+" goes to jail on Chance card", 3)

        # 11: You've been elected chairman. Pay each player $50
        elif chanceCard == 11:
            log.write(
                player.name+" gets chance card: You've been elected chairman. Pay each player $50", 3)
            for other_player in board.players:
                if other_player != player and not other_player.isBankrupt:
                    player.takeMoney(50)
                    other_player.addMoney(50)

        # 12: Advance to BoardWalk
        elif chanceCard == 12:
            log.write(player.name+" gets chance card: Advance to BoardWalk", 3)
            player.position = 39
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 13: Go back 3 spaces
        elif chanceCard == 13:
            log.write(player.name+" gets chance card: Go back 3 spaces", 3)
            player.position -= 3
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 14: Your building loan matures. Receive $150.
        elif chanceCard == 14:
            log.write(
                player.name+" gets chance card: Your building loan matures. Receive $150", 3)
            player.addMoney(150)

        # 15: You have won a crossword competition. Collect $100
        elif chanceCard == 15:
            log.write(
                player.name+" gets chance card: You have won a crossword competition. Collect $100", 3)
            player.addMoney(100)

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
            log.write(player.name+" gets community card: Pay school tax $150", 3)
            player.takeMoney(150)

        # 1: Opera night: collect $50 from each player
        if communityCard == 1:
            log.write(player.name+" Opera night: collect $50 from each player", 3)
            for other_player in board.players:
                if other_player != player and not other_player.isBankrupt:
                    player.addMoney(50)
                    other_player.takeMoney(50)
                    other_player.checkBankrupcy(board)

        # 2: You inherit $100
        if communityCard == 2:
            log.write(player.name+" gets community card: You inherit $100", 3)
            player.addMoney(100)

        # 3: Pay hospital $100
        if communityCard == 3:
            log.write(player.name+" gets community card: Pay hospital $100", 3)
            player.takeMoney(100)

        # 4: Income tax refund $20
        if communityCard == 4:
            log.write(
                player.name+" gets community card: Income tax refund $20", 3)
            player.addMoney(20)

        # 5: Go Directly to Jail
        elif communityCard == 5:
            log.write(player.name+" gets community card: Go Directly to Jail", 3)
            player.moveTo(10)
            player.inJail = True
            log.write(player.name+" goes to jail on Community card", 3)

        # 6: Get Out Of Jail Free
        elif communityCard == 6:
            log.write(player.name+" gets community card: Get Out Of Jail Free", 3)
            player.hasJailCardCommunity = True

        # 7: Second prize in beauty contest $10
        if communityCard == 7:
            log.write(
                player.name+" gets community card: Second prize in beauty contest $10", 3)
            player.addMoney(10)

        # 8: You are assigned for street repairs
        elif communityCard == 8:
            log.write(
                player.name+" gets community card: You are assigned for street repairs", 3)
            player.makeRepairs(board, "community")

        # 9: Bank error in your favour: $200
        if communityCard == 9:
            log.write(
                player.name+" gets community card: Bank error in your favour: $200", 3)
            player.addMoney(200)

        # 10: Advance to GO
        elif communityCard == 10:
            log.write(player.name+" gets community card: Advance to GO", 3)
            player.addMoney(settingsSalary)
            log.write(player.name+" gets salary: $"+str(settingsSalary), 3)
            player.position = 0
            log.write(player.name+" goes to " +
                      str(board.b[player.position].name), 3)

        # 11: X-Mas fund matured: $100
        if communityCard == 11:
            log.write(
                player.name+" gets community card: X-Mas fund matured: $100", 3)
            player.addMoney(100)

        # 12: Doctor's fee $50
        if communityCard == 12:
            log.write(player.name+" gets community card: Doctor's fee $50", 3)
            player.takeMoney(50)

        # 13: From sale of stock you get $45
        if communityCard == 13:
            log.write(
                player.name+" gets community card: From sale of stock you get $45", 3)
            player.addMoney(45)

        # 14: Receive for services $25
        if communityCard == 14:
            log.write(
                player.name+" gets community card: Receive for services $25", 3)
            player.addMoney(25)

        # 15: Life insurance matures, collect $100
        if communityCard == 15:
            log.write(
                player.name+" gets community card: Life insurance matures, collect $100", 3)
            player.addMoney(100)

        # Put the card back
        if communityCard != 6:  # except GOOJF card
            board.communityCards.append(communityCard)


class Property(Cell):
    """Property Class (for Properties, Rails, Utilities)"""

    def __init__(self, name, cost_base, rent_base, cost_house, rent_house, group):
        self.name = name
        self.cost_base = cost_base
        self.rent_base = rent_base
        self.cost_house = cost_house
        self.rent_house = rent_house
        self.group = group
        self.owner = ""
        self.isMortgaged = False
        self.isMonopoly = False
        self.hasHouses = 0

    def action(self, player, rent, board):
        """Player ended on a property"""

        # it's their property or mortgaged - do nothing
        if self.owner == player or self.isMortgaged:
            log.write("No rent this time", 3)
            return

        # Property up for sale
        elif self.owner == "":
            if player.wantsToBuy(self.cost_base, self.group):
                log.write(player.name+" buys property " +
                          self.name + " for $"+str(self.cost_base), 3)
                player.takeMoney(self.cost_base)
                self.owner = player
                board.recalculateAfterPropertyChange()
            else:
                pass  # auction here
                log.write(player.name+" didn't buy the property.", 3)
                # Auction here
                # Decided not to implement it...
            return

        # someone else's property - pay the rent
        else:
            player.takeMoney(rent)
            self.owner.addMoney(rent)
            log.write(player.name+" pays the rent $" +
                      str(rent) + " to "+self.owner.name, 3)

    # mortgage the plot to the player / or sell the house
    def mortgage(self, player, board):
        """Sell hotel"""
        if self.hasHouses == 5:
            player.addMoney(self.cost_house * 5 // 2)
            self.hasHouses = 0
            board.nHotels -= 1
            log.write(player.name+" sells hotel on "+self.name, 3)
        # Sell one house
        elif self.hasHouses > 0:
            player.addMoney(self.cost_house // 2)
            self.hasHouses -= 1
            board.nHouses -= 1
            log.write(player.name+" sells house on "+self.name, 3)
        # Mortgage
        else:
            self.isMortgaged = True
            player.addMoney(self.cost_base // 2)
            # log name of the plot and money player need to pay to get it back
            player.hasMortgages.append(
                (self, int((self.cost_base // 2) * 1.1)))
            log.write(player.name+" mortgages "+self.name, 3)

    # unmortgage thr plot

    def unmortgage(self, player):
        # print (player.hasMortgages)
        for mortgage in player.hasMortgages:
            if mortgage[0] == self:
                thisMortgage = mortgage
        self.isMortgaged = False
        player.takeMoney(thisMortgage[1])
        player.hasMortgages.remove(thisMortgage)
        log.write(player.name+" unmortgages "+self.name, 3)


class Board:

    def __init__(self, players):
        """
        Board is a data for plots

        name: does not really matter, just convenience
        base_cost: used when buying plot, mortgage
        base_rent: used for rent and monopoly rent
         (for utilities and rail - in calculateRent method)
        house_cost: price of one house (or a hotel)
        house_rent: list of rent price with 1,2,3,4 houses and a hotel
        group: used to determine monopoly
        """

        # I know it is messy, but I need this for players to pay each other
        self.players = players

        self.b = []
        # 0-4
        self.b.append(Cell("Go"))
        self.b.append(Property("A1 Mediterraneal Avenue", 60,
                               2, 50, (10, 30, 90, 160, 250), "brown"))
        self.b.append(Community("Community Chest"))
        self.b.append(Property("A2 Baltic Avenue", 60, 4,
                               50, (20, 60, 180, 320, 450), "brown"))
        self.b.append(PropertyTax("Property Tax"))
        # 5-9
        self.b.append(Property("R1 Reading railroad",
                               200, 0, 0, (0, 0, 0, 0, 0), "rail"))
        self.b.append(Property("B1 Oriental Avenue", 100, 6,
                               50, (30, 90, 270, 400, 550), "lightblue"))
        self.b.append(Chance("Chance"))
        self.b.append(Property("B2 Vermont Avenue", 100, 6, 50,
                               (30, 90, 270, 400, 550), "lightblue"))
        self.b.append(Property("B3 Connecticut Avenue", 120, 8,
                               50, (40, 100, 300, 450, 600), "lightblue"))
        # 10-14
        self.b.append(Cell("Prison"))
        self.b.append(Property("C1 St.Charle's Place", 140, 10,
                               100, (50, 150, 450, 625, 750), "pink"))
        self.b.append(Property("U1 Electric Company",
                               150, 0, 0, (0, 0, 0, 0, 0), "util"))
        self.b.append(Property("C2 States Avenue", 140, 10,
                               100, (50, 150, 450, 625, 750), "pink"))
        self.b.append(Property("C3 Virginia Avenue", 160, 12,
                               100, (60, 180, 500, 700, 900), "pink"))
        # 15-19
        self.b.append(Property("R2 Pennsylvania Railroad",
                               200, 0, 0, (0, 0, 0, 0, 0), "rail"))
        self.b.append(Property("D1 St.James Place", 180, 14,
                               100, (70, 200, 550, 700, 950), "orange"))
        self.b.append(Community("Community Chest"))
        self.b.append(Property("D2 Tennessee Avenue", 180, 14,
                               100, (70, 200, 550, 700, 950), "orange"))
        self.b.append(Property("D3 New York Avenue", 200, 16,
                               100, (80, 220, 600, 800, 1000), "orange"))
        # 20-24
        self.b.append(Cell("Free Parking"))
        self.b.append(Property("E1 Kentucky Avenue", 220, 18,
                               150, (90, 250, 700, 875, 1050), "red"))
        self.b.append(Chance("Chance"))
        self.b.append(Property("E2 Indiana Avenue", 220, 18,
                               150, (90, 250, 700, 875, 1050), "red"))
        self.b.append(Property("E3 Illinois Avenue", 240, 20,
                               150, (100, 300, 750, 925, 1100), "red"))
        # 25-29
        self.b.append(Property("R3 BnO Railroad", 200,
                               0, 0, (0, 0, 0, 0, 0), "rail"))
        self.b.append(Property("F1 Atlantic Avenue", 260, 22,
                               150, (110, 330, 800, 975, 1150), "yellow"))
        self.b.append(Property("F2 Ventinor Avenue", 260, 22,
                               150, (110, 330, 800, 975, 1150), "yellow"))
        self.b.append(Property("U2 Waterworks", 150,
                               0, 0, (0, 0, 0, 0, 0), "util"))
        self.b.append(Property("F3 Martin Gardens", 280, 24, 150,
                               (120, 360, 850, 1025, 1200), "yellow"))
        # 30-34
        self.b.append(GoToJail("Go To Jail"))
        self.b.append(Property("G1 Pacific Avenue", 300, 26,
                               200, (130, 390, 900, 1100, 1275), "green"))
        self.b.append(Property("G2 North Carolina Avenue", 300,
                               26, 200, (130, 390, 900, 1100, 1275), "green"))
        self.b.append(Community("Community Chest"))
        self.b.append(Property("G3 Pennsylvania Avenue", 320, 28,
                               200, (150, 450, 100, 1200, 1400), "green"))
        # 35-39
        self.b.append(Property("R4 Short Line", 200,
                               0, 0, (0, 0, 0, 0, 0), "rail"))
        self.b.append(Chance("Chance"))
        self.b.append(Property("H1 Park Place", 350, 35, 200,
                               (175, 500, 1100, 1300, 1500), "indigo"))
        self.b.append(LuxuryTax("Luxury Tax"))
        self.b.append(Property("H2 Boardwalk", 400, 50, 200,
                               (200, 600, 1400, 1700, 2000), "indigo"))

        # number of built houses and hotels (to limit when needed)
        self.nHouses = 0
        self.nHotels = 0

        # Chance
        self.chanceCards = [i for i in range(16)]
        random.shuffle(self.chanceCards)

        # Community Chest
        self.communityCards = [i for i in range(16)]
        random.shuffle(self.communityCards)

    # Does the board have at least one monopoly
    # Used for statistics
    def hasMonopoly(self):
        for i in range(len(self.b)):
            if self.b[i].isMonopoly:
                return True
        return False

    # Count the number of rails of the same owner as "position"
    # Used in rent calculations
    def countRails(self, position):
        if type(self.b[position]) != Property or self.b[position].group != "rail":
            return False
        railcount = 0
        thisOwner = self.b[position].owner
        for plot in self.b:
            if type(plot) == Property and plot.group == "rail" \
               and plot.owner == thisOwner and plot.owner != "" \
               and not plot.isMortgaged:
                railcount += 1
        return railcount

    # What is the rent of plot "position"
    # Takes into account utilities, rails, monopoly

    def calculateRent(self, position, special=""):
        if type(self.b[position]) == Property:
            rent = 0

            # utility
            if self.b[position].group == "util":
                if self.b[position].isMonopoly or special == "from_chance":
                    rent = (random.randint(1, 6)+random.randint(1, 6)) * 10
                else:
                    rent = (random.randint(1, 6)+random.randint(1, 6)) * 4

            # rail
            elif self.b[position].group == "rail":
                rails = self.countRails(position)
                rent = 0 if rails == 0 else 25 * 2**(rails)
                if special == "from_chance":
                    rent *= 2

            # usual property
            else:
                if self.b[position].hasHouses > 0:
                    if self.b[position].hasHouses-1 > 5:
                        print(self.b[position].hasHouses-1)
                        print(position)
                        self.printMap()
                    rent = self.b[position].rent_house[self.b[position].hasHouses-1]
                elif self.b[position].isMonopoly:
                    rent = 2*self.b[position].rent_base
                else:
                    rent = self.b[position].rent_base
        else:  # not a Property
            rent = 0
        return rent

    # What % of plots of this group does player have
    # Used in calculation of least valuable property
    def shareOfGroup(self, group, player):
        total = 0
        owned = 0
        for plot in self.b:
            if type(plot) == Property and plot.group == group:
                total += 1
                if plot.owner == player:
                    owned += 1
        return owned / total

    # What is the least valuable property / building
    # Used to pick what to mortgage / sell buildings

    def choosePropertyToMortgageDowngrade(self, player):
        # list all the items this player has:
        ownedStuff = []
        for i in range(len(self.b)):
            plot = self.b[i]
            if type(plot) == Property and not plot.isMortgaged and plot.owner == player:
                ownedStuff.append((i, plot.cost_base, self.b[i].isMonopoly, self.shareOfGroup(
                    plot.group, player), plot.hasHouses))
        if len(ownedStuff) == 0:
            return False
        # first to sel/mortgage are: least "monoolistic"; most houses
        ownedStuff.sort(key=lambda x: (x[3], -x[4]))
        return ownedStuff[0][0]

    # Chose Property to build the next house/hotel according to its value and available money
    def listPropertyToBuild(self, player):
        # list all the items this player could built on:
        toBuildStuff = []
        # smaller level of improvement in the group (to prevent inequal improvement)
        minInGroup = {}
        # start with listing all their monopolies
        for i in range(len(self.b)):
            plot = self.b[i]
            if type(plot) == Property and self.b[i].isMonopoly and plot.owner == player \
               and plot.group != "rail" and plot.group != "util" and plot.hasHouses < 5:
                # limit max houses experiment
                if not (player.name == "exp" and expHouseBuildLimit == plot.hasHouses):
                    toBuildStuff.append(
                        (i, plot.name, plot.group, plot.hasHouses, plot.cost_house, plot.cost_base))
                    if plot.group in minInGroup:
                        minInGroup[plot.group] = min(
                            plot.hasHouses, minInGroup[plot.group])
                    else:
                        minInGroup[plot.group] = plot.hasHouses
        if len(toBuildStuff) == 0:
            return []

        # remove those that has more houses than other plots in monopoly (to ensure gradual development)
        toBuildStuff.sort(key=lambda x: (x[2], x[3]))
        for i in range(len(toBuildStuff)-1, -1, -1):
            # if it has more houses than minimum in that group, remove
            if toBuildStuff[i][3] > minInGroup[toBuildStuff[i][2]]:
                if not settingsAllowUnEqualDevelopment:
                    toBuildStuff.pop(i)

        # sort by house price and base
        if behaveBuildRandom:
            random.shuffle(toBuildStuff)
        elif behaveBuildCheapest:
            toBuildStuff.sort(key=lambda x: (-x[4], -x[5]))
        else:
            toBuildStuff.sort(key=lambda x: (x[4], x[5]))

        if expBuildCheapest and player.name == "exp":
            toBuildStuff.sort(key=lambda x: (-x[4], -x[5]))
        if expBuildExpensive and player.name == "exp":
            toBuildStuff.sort(key=lambda x: (x[4], x[5]))

        if expBuildThree and player.name == "exp":
            hasLessThanThree = False
            for i in range(len(toBuildStuff)):
                if toBuildStuff[i][3] < 3:
                    hasLessThanThree = True
            if hasLessThanThree:
                for i in range(len(toBuildStuff)-1, -1, -1):
                    if toBuildStuff[i][3] >= 3:
                        del toBuildStuff[i]
            toBuildStuff.sort(key=lambda x: (x[3], x[4], x[5]))
            # if len(toBuildStuff)>3:
            #    print (toBuildStuff)

        # if len(toBuildStuff)>5:
            # print (toBuildStuff)
        return toBuildStuff

    def choosePropertyToBuild(self, player, availiableMoney):
        for i in range(len(player.plotsToBuild)-1, -1, -1):
            if player.plotsToBuild[i][4] <= availiableMoney:
                return player.plotsToBuild[i][0]
        return False

    # Build one house/hotel withinavailabel money
    # return True if built, so this function will be called again

    def improveProperty(self, player, availiableMoney):
        propertyToImprove = self.choosePropertyToBuild(player, availiableMoney)
        if type(propertyToImprove) == bool and not propertyToImprove:
            return False

        # Check if we reached the limit of available Houses/Hotels
        thisIsHotel = True if self.b[propertyToImprove].hasHouses == 4 else False
        if thisIsHotel:
            if self.nHotels == settingHotelLimit:
                log.write("reached hotel limit", 3)
                return False
        else:
            if self.nHouses == settingHouseLimit:
                log.write("reached house limit", 3)
                return False

        # add a building
        self.b[propertyToImprove].hasHouses += 1
        # add to the counter
        if thisIsHotel:
            self.nHotels += 1
            self.nHouses -= 4
        else:
            self.nHouses += 1

        log.write(player.name+" builds house N" +
                  str(self.b[propertyToImprove].hasHouses)+" on "+self.b[propertyToImprove].name, 3)
        player.takeMoney(self.b[propertyToImprove].cost_house)
        player.plotsToBuild = self.listPropertyToBuild(player)
        return True

    # When player is bankrupt - return all their property to market

    def sellAll(self, player):
        for plot in self.b:
            if type(plot) == Property and plot.owner == player:
                plot.owner = ""
                plot.isMortgaged = False

    # Get the list of plots player would want to get
    # that is he lacks one to for a monopoly

    def getListOfWantedPlots(self, player):
        groups = {}
        for plot in self.b:
            if plot.group != "":
                if plot.group in groups:
                    groups[plot.group][0] += 1
                else:
                    groups[plot.group] = [1, 0]
                if plot.owner == player:
                    groups[plot.group][1] += 1
        wanted = []
        for group in groups:
            if group != "util" and groups[group][0]-groups[group][1] == 1:
                for i in range(len(self.b)):
                    if type(self.b[i]) == Property and self.b[i].group == group and self.b[i].owner != player:
                        wanted.append(i)
        return sorted(wanted)

    # Get the list of plots player would want to offer for trade
    # that one random plot in a group
    def getListOfOfferedPlots(self, player):
        groups = {}
        for plot in self.b:
            if plot.group != "":
                if plot.group not in groups:
                    groups[plot.group] = 0
                if plot.owner == player:
                    groups[plot.group] += 1
        offered = []
        for group in groups:
            if group != "util" and groups[group] == 1:
                for i in range(len(self.b)):
                    if type(self.b[i]) == Property and self.b[i].group == group \
                       and self.b[i].owner == player and self.b[i].isMortgaged == False:
                        offered.append(i)
        return sorted(offered)

    # update isMonopoly status for all plots
    def checkMonopolies(self):
        groups = {}
        for i in range(len(self.b)):
            plot = self.b[i]
            if type(plot) == Property:
                if plot.owner == "":
                    groups[plot.group] = False
                else:
                    if plot.group in groups:
                        if groups[plot.group] != plot.owner:
                            groups[plot.group] = False
                    else:
                        groups[plot.group] = plot.owner
        for i in range(len(self.b)):
            plot = self.b[i]
            if type(plot) == Property:
                if groups[plot.group] != False:
                    plot.isMonopoly = True
                else:
                    plot.isMonopoly = False

    # calculating heavy tasks that we want to do after property change:
    # list of wanted and offered properties for each player
    def recalculateAfterPropertyChange(self):
        self.checkMonopolies()
        for player in self.players:
            player.plotsWanted = self.getListOfWantedPlots(player)
            player.plotsOffered = self.getListOfOfferedPlots(player)
            player.plotsToBuild = self.listPropertyToBuild(player)

    # perform action for a player on a plot

    def action(self, player, position, special=""):

        # Landed on a property - calculate rent first
        if type(self.b[position]) == Property:
            # calculate the rent one would have to pay (but not pay it yet)
            rent = self.calculateRent(position, special=special)
            # pass action to to the cell
            self.b[position].action(player, rent, self)
        # landed on a chance, pass board, to track the chance cards
        elif type(self.b[position]) == Chance or type(self.b[position]) == Community or type(self.b[position]) == PropertyTax:
            self.b[position].action(player, self)
        # other cells
        else:
            self.b[position].action(player)

    def printMap(self):
        for i in range(len(self.b)):
            if type(self.b[i]) == Property:
                print(i, self.b[i].name, "houses:", self.b[i].hasHouses,
                      "mortgaged:", self.b[i].isMortgaged,
                      "owner:", "none" if self.b[i].owner == "" else self.b[i].owner.name,
                      "monopoly" if self.b[i].isMonopoly else ""
                      )
            else:
                pass
                # print (i, type(self.b[i]))


def isGameOver(players):
    """Check if there are more then 1 player left in the game"""
    alive = 0
    for player in players:
        if not player.isBankrupt:
            alive += 1
    if alive > 1:
        return False
    else:
        return True

# simulate one game


def oneGame():

    # create players
    players = []
    # names = ["pl"+str(i) for i in range(nPlayers)]
    names = ["pl"+str(i) for i in range(nPlayers-1)]+["exp"]
    if shufflePlayers:
        random.shuffle(names)
    for i in range(nPlayers):
        players.append(Player(names[i]))

    # create board
    gameBoard = Board(players)

    #  netWorth history first point
    if writeData == "netWorth":
        networthstring = ""
        for player in players:
            networthstring += str(player.netWorth(gameBoard))
            if player != players[-1]:
                networthstring += "\t"
        log.write(networthstring, data=True)

    # game
    for i in range(nMoves):

        if isGameOver(players):
            # to track length of the game
            if writeData == "lastTurn":
                log.write(str(i-1), data=True)
            break

        log.write(" TURN "+str(i+1), 1)
        for player in players:
            if player.money > 0:
                log.write(player.name+": $"+str(player.money) +
                          ", position:"+str(player.position), 2)

        for player in players:
            if not isGameOver(players):  # Only continue if 2 or more players
                # returns True if player has to go again
                while player.makeAMove(gameBoard):
                    pass

        # track netWorth history of the game
        if writeData == "netWorth":
            networthstring = ""
            for player in players:
                networthstring += str(player.netWorth(gameBoard))
                if player != players[-1]:
                    networthstring += "\t"
            log.write(networthstring, data=True)

    # tests
# for player in players:
# player.threeWayTrade(gameBoard)

    # return final scores
    results = [players[i].getMoney() for i in range(nPlayers)]

    # if it is an only simulation, print map and final score
    if nSimulations == 1 and showMap:
        gameBoard.printMap()
    if nSimulations == 1 and showResult:
        print(results)
    return results


def runSimulation():
    """run multiple game simulations"""
    results = []

    if showProgressBar:
        widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.ETA()]
        pbar = progressbar.ProgressBar(widgets=widgets, term_width=OUT_WIDTH, maxval=nSimulations)
        pbar.start()
    
    for i in range(nSimulations):

        if showProgressBar:
            pbar.update(i+1)
        
        log.write("="*10+" GAME "+str(i+1)+" "+"="*10+"\n")

        # remaining players - add to the results list
        results.append(oneGame())

        # write remaining players in a data log
        if writeData == "remainingPlayers":
            remPlayers = sum([1 for r in results[-1] if r > 0])
            log.write(str(remPlayers), data=True)
            
    print()
    if showProgressBar:
        pbar.finish()
    
    return results


def analyzeResults(results):
    """Analize results"""

    remainingPlayers = [0, ]*nPlayers
    for result in results:
        alive = 0
        for score in result:
            if score >= 0:
                alive += 1
        remainingPlayers[alive-1] += 1

    if showRemPlayers:
        print("Remaining:", remainingPlayers)


def analyzeData():

    if writeData == "losersNames" or writeData == "experiment" or writeData == "remainingPlayers":
        groups = {}
        with open("data.txt", "r") as fs:
            for line in fs:
                item = line.strip()
                if item in groups:
                    groups[item] += 1
                else:
                    groups[item] = 1
        experiment = 0
        control = 0
        for item in sorted(groups.keys()):
            count = groups[item]/nSimulations

            if writeData == "losersNames":
                count = 1-count
            if item == "exp":
                experiment = count
            else:
                control += count

            margin = 1.96 * math.sqrt(count*(1-count)/nSimulations)
            print("{}: {:.1%} +- {:.1%}".format(item, count, margin))

        if experiment != 0:
            print("Exp result: {:.1%}".format(experiment-control/(nPlayers-1)))

    if writeData == "netWorth":
        print("graph here")
        npdata = np.transpose(np.loadtxt(
            "data.txt", dtype=int, delimiter="\t"))
        x = np.arange(0, max([len(d) for d in npdata]))

        plt.ioff()
        fig, ax = plt.subplots()
        for i in range(nPlayers):
            ax.plot(x, npdata[i], label='1')
        plt.savefig("fig"+str(time.time())+".png")


if __name__ == "__main__":

    print("="*OUT_WIDTH)

    t = time.time()
    log = Log()
    if seed != "":
        random.seed(seed)
    else:
        random.seed()
    print("Players:", nPlayers, " Turns:", nMoves,
          " Games:", nSimulations, " Seed:", seed)
    results = runSimulation()
    analyzeResults(results)
    log.close()
    analyzeData()
    print("Done in {:.2f}s".format(time.time()-t))
