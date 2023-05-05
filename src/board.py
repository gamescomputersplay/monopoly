from .cells import Property, Cell, Community, PropertyTax, Chance, GoToJail, LuxuryTax
from .util.configs import BANK_NAME
import random


class Board:
    def __init__(self, players, game_conf, log):
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
        self.log = log
        self.game_conf = game_conf

        self.b = []
        # 0-4
        self.b.append(Cell("Go", log))
        self.b.append(
            Property(
                "A1 Mediterraneal Avenue",
                60,
                2,
                50,
                (10, 30, 90, 160, 250),
                "brown",
                log,
            )
        )
        self.b.append(Community("Community Chest", log))
        self.b.append(
            Property(
                "A2 Baltic Avenue", 60, 4, 50, (20, 60, 180, 320, 450), "brown", log
            )
        )
        self.b.append(PropertyTax("Property Tax", log))
        # 5-9
        self.b.append(
            Property("R1 Reading railroad", 200, 0, 0, (0, 0, 0, 0, 0), "rail", log)
        )
        self.b.append(
            Property(
                "B1 Oriental Avenue",
                100,
                6,
                50,
                (30, 90, 270, 400, 550),
                "lightblue",
                log,
            )
        )
        self.b.append(Chance("Chance", log))
        self.b.append(
            Property(
                "B2 Vermont Avenue",
                100,
                6,
                50,
                (30, 90, 270, 400, 550),
                "lightblue",
                log,
            )
        )
        self.b.append(
            Property(
                "B3 Connecticut Avenue",
                120,
                8,
                50,
                (40, 100, 300, 450, 600),
                "lightblue",
                log,
            )
        )
        # 10-14
        self.b.append(Cell("Prison", log))
        self.b.append(
            Property(
                "C1 St.Charle's Place",
                140,
                10,
                100,
                (50, 150, 450, 625, 750),
                "pink",
                log,
            )
        )
        self.b.append(
            Property("U1 Electric Company", 150, 0, 0, (0, 0, 0, 0, 0), "util", log)
        )
        self.b.append(
            Property(
                "C2 States Avenue", 140, 10, 100, (50, 150, 450, 625, 750), "pink", log
            )
        )
        self.b.append(
            Property(
                "C3 Virginia Avenue",
                160,
                12,
                100,
                (60, 180, 500, 700, 900),
                "pink",
                log,
            )
        )
        # 15-19
        self.b.append(
            Property(
                "R2 Pennsylvania Railroad", 200, 0, 0, (0, 0, 0, 0, 0), "rail", log
            )
        )
        self.b.append(
            Property(
                "D1 St.James Place",
                180,
                14,
                100,
                (70, 200, 550, 700, 950),
                "orange",
                log,
            )
        )
        self.b.append(Community("Community Chest", log))
        self.b.append(
            Property(
                "D2 Tennessee Avenue",
                180,
                14,
                100,
                (70, 200, 550, 700, 950),
                "orange",
                log,
            )
        )
        self.b.append(
            Property(
                "D3 New York Avenue",
                200,
                16,
                100,
                (80, 220, 600, 800, 1000),
                "orange",
                log,
            )
        )
        # 20-24
        self.b.append(Cell("Free Parking", log))
        self.b.append(
            Property(
                "E1 Kentucky Avenue",
                220,
                18,
                150,
                (90, 250, 700, 875, 1050),
                "red",
                log,
            )
        )
        self.b.append(Chance("Chance", log))
        self.b.append(
            Property(
                "E2 Indiana Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), "red", log
            )
        )
        self.b.append(
            Property(
                "E3 Illinois Avenue",
                240,
                20,
                150,
                (100, 300, 750, 925, 1100),
                "red",
                log,
            )
        )
        # 25-29
        self.b.append(
            Property("R3 BnO Railroad", 200, 0, 0, (0, 0, 0, 0, 0), "rail", log)
        )
        self.b.append(
            Property(
                "F1 Atlantic Avenue",
                260,
                22,
                150,
                (110, 330, 800, 975, 1150),
                "yellow",
                log,
            )
        )
        self.b.append(
            Property(
                "F2 Ventinor Avenue",
                260,
                22,
                150,
                (110, 330, 800, 975, 1150),
                "yellow",
                log,
            )
        )
        self.b.append(
            Property("U2 Waterworks", 150, 0, 0, (0, 0, 0, 0, 0), "util", log)
        )
        self.b.append(
            Property(
                "F3 Martin Gardens",
                280,
                24,
                150,
                (120, 360, 850, 1025, 1200),
                "yellow",
                log,
            )
        )
        # 30-34
        self.b.append(GoToJail("Go To Jail", log))
        self.b.append(
            Property(
                "G1 Pacific Avenue",
                300,
                26,
                200,
                (130, 390, 900, 1100, 1275),
                "green",
                log,
            )
        )
        self.b.append(
            Property(
                "G2 North Carolina Avenue",
                300,
                26,
                200,
                (130, 390, 900, 1100, 1275),
                "green",
                log,
            )
        )
        self.b.append(Community("Community Chest", log))
        self.b.append(
            Property(
                "G3 Pennsylvania Avenue",
                320,
                28,
                200,
                (150, 450, 100, 1200, 1400),
                "green",
                log,
            )
        )
        # 35-39
        self.b.append(
            Property("R4 Short Line", 200, 0, 0, (0, 0, 0, 0, 0), "rail", log)
        )
        self.b.append(Chance("Chance", log))
        self.b.append(
            Property(
                "H1 Park Place",
                350,
                35,
                200,
                (175, 500, 1100, 1300, 1500),
                "indigo",
                log,
            )
        )
        self.b.append(LuxuryTax("Luxury Tax", log))
        self.b.append(
            Property(
                "H2 Boardwalk",
                400,
                50,
                200,
                (200, 600, 1400, 1700, 2000),
                "indigo",
                log,
            )
        )

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
            if (
                type(plot) == Property
                and plot.group == "rail"
                and plot.owner == thisOwner
                and plot.owner != ""
                and not plot.isMortgaged
            ):
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
                    rent = (random.randint(1, 6) + random.randint(1, 6)) * 10
                else:
                    rent = (random.randint(1, 6) + random.randint(1, 6)) * 4

            # rail
            elif self.b[position].group == "rail":
                rails = self.countRails(position)
                rent = 0 if rails == 0 else 25 * 2 ** (rails)
                if special == "from_chance":
                    rent *= 2

            # usual property
            else:
                if self.b[position].hasHouses > 0:
                    if self.b[position].hasHouses - 1 > 5:
                        print(self.b[position].hasHouses - 1)
                        print(position)
                        self.printMap()
                    rent = self.b[position].rent_house[self.b[position].hasHouses - 1]
                elif self.b[position].isMonopoly:
                    rent = 2 * self.b[position].rent_base
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
                ownedStuff.append(
                    (
                        i,
                        plot.cost_base,
                        self.b[i].isMonopoly,
                        self.shareOfGroup(plot.group, player),
                        plot.hasHouses,
                    )
                )
        if len(ownedStuff) == 0:
            return False
        # first to sel/mortgage are: least "monoolistic"; most houses
        ownedStuff.sort(key=lambda x: (x[3], -x[4]))
        return ownedStuff[0][0]

    # Chose Property to build the next house/hotel according to its value and available money
    def listPropertyToBuild(self, player, board):
        # list all the items this player could built on:
        toBuildStuff = []
        # smaller level of improvement in the group (to prevent inequal improvement)
        minInGroup = {}
        # start with listing all their monopolies
        for i in range(len(self.b)):
            plot = self.b[i]
            if (
                type(plot) == Property
                and self.b[i].isMonopoly
                and plot.owner == player
                and plot.group != "rail"
                and plot.group != "util"
                and plot.hasHouses < 5
            ):
                # limit max houses experiment
                if not (player.name == "exp" and expHouseBuildLimit == plot.hasHouses):
                    toBuildStuff.append(
                        (
                            i,
                            plot.name,
                            plot.group,
                            plot.hasHouses,
                            plot.cost_house,
                            plot.cost_base,
                        )
                    )
                    if plot.group in minInGroup:
                        minInGroup[plot.group] = min(
                            plot.hasHouses, minInGroup[plot.group]
                        )
                    else:
                        minInGroup[plot.group] = plot.hasHouses
        if len(toBuildStuff) == 0:
            return []

        # remove those that has more houses than other plots in monopoly (to ensure gradual development)
        toBuildStuff.sort(key=lambda x: (x[2], x[3]))
        for i in range(len(toBuildStuff) - 1, -1, -1):
            # if it has more houses than minimum in that group, remove
            if toBuildStuff[i][3] > minInGroup[toBuildStuff[i][2]]:
                if not board.game_conf.allow_unequal_development:
                    toBuildStuff.pop(i)

        # sort by house price and base
        if player.behaviour.build_randomly:
            random.shuffle(toBuildStuff)
        elif player.behaviour.build_cheapest:
            toBuildStuff.sort(key=lambda x: (-x[4], -x[5]))
        else:
            toBuildStuff.sort(key=lambda x: (x[4], x[5]))

        if player.behaviour.build_cheapest and player.name == "exp":
            toBuildStuff.sort(key=lambda x: (-x[4], -x[5]))

        if player.behaviour.build_expensive and player.name == "exp":
            toBuildStuff.sort(key=lambda x: (x[4], x[5]))

        if player.behaviour.build_only_three_houses and player.name == "exp":
            hasLessThanThree = False
            for i in range(len(toBuildStuff)):
                if toBuildStuff[i][3] < 3:
                    hasLessThanThree = True
            if hasLessThanThree:
                for i in range(len(toBuildStuff) - 1, -1, -1):
                    if toBuildStuff[i][3] >= 3:
                        del toBuildStuff[i]
            toBuildStuff.sort(key=lambda x: (x[3], x[4], x[5]))
            # if len(toBuildStuff)>3:
            #    print (toBuildStuff)

        # if len(toBuildStuff)>5:
        # print (toBuildStuff)
        return toBuildStuff

    def choosePropertyToBuild(self, player, availiableMoney):
        for i in range(len(player.plots_to_build) - 1, -1, -1):
            if player.plots_to_build[i][4] <= availiableMoney:
                return player.plots_to_build[i][0]
        return False

    # Build one house/hotel withinavailabel money
    # return True if built, so this function will be called again

    def improveProperty(self, player, board, availiableMoney):
        propertyToImprove = self.choosePropertyToBuild(player, availiableMoney)
        if type(propertyToImprove) == bool and not propertyToImprove:
            return False

        # Check if we reached the limit of available Houses/Hotels
        thisIsHotel = True if self.b[propertyToImprove].hasHouses == 4 else False
        if thisIsHotel:
            if self.nHotels == board.game_conf.hotel_limit:
                self.log.write("reached hotel limit", 3)
                return False
        else:
            if self.nHouses == board.game_conf.house_limit:
                self.log.write("reached house limit", 3)
                return False

        # add a building
        self.b[propertyToImprove].hasHouses += 1
        # add to the counter
        if thisIsHotel:
            self.nHotels += 1
            self.nHouses -= 4
        else:
            self.nHouses += 1

        self.log.write(
            player.name
            + " builds house N"
            + str(self.b[propertyToImprove].hasHouses)
            + " on "
            + self.b[propertyToImprove].name,
            3,
        )
        player.take_money(self.b[propertyToImprove].cost_house, self, BANK_NAME)
        player.plots_to_build = self.listPropertyToBuild(player, board)
        return True

    # When player is bankrupt - return all their property to market

    def sellAll(self, player, other_player=None):
        for plot in self.b:
            if type(plot) == Property and plot.owner == player:
                if other_player is None:
                    plot.owner = ""
                    plot.isMortgaged = False
                else:
                    plot.owner = other_player

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
            if group != "util" and groups[group][0] - groups[group][1] == 1:
                for i in range(len(self.b)):
                    if (
                        type(self.b[i]) == Property
                        and self.b[i].group == group
                        and self.b[i].owner != player
                    ):
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
                    if (
                        type(self.b[i]) == Property
                        and self.b[i].group == group
                        and self.b[i].owner == player
                        and self.b[i].isMortgaged == False
                    ):
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
            player.plots_wanted = self.getListOfWantedPlots(player)
            player.plots_offered = self.getListOfOfferedPlots(player)
            player.plots_to_build = self.listPropertyToBuild(player, self)

    # perform action for a player on a plot

    def action(self, player, position, special=""):
        # Landed on a property - calculate rent first
        if type(self.b[position]) == Property:
            # calculate the rent one would have to pay (but not pay it yet)
            rent = self.calculateRent(position, special=special)
            # pass action to to the cell
            self.b[position].action(player, rent, self)
        # landed on a chance, pass board, to track the chance cards
        elif (
            type(self.b[position]) == Chance
            or type(self.b[position]) == Community
            or type(self.b[position]) == PropertyTax
        ):
            self.b[position].action(player, self)
        # other cells
        else:
            self.b[position].action(player, self)

    def printMap(self):
        for i in range(len(self.b)):
            if type(self.b[i]) == Property:
                print(
                    i,
                    self.b[i].name,
                    "houses:",
                    self.b[i].hasHouses,
                    "mortgaged:",
                    self.b[i].isMortgaged,
                    "owner:",
                    "none" if self.b[i].owner == "" else self.b[i].owner.name,
                    "monopoly" if self.b[i].isMonopoly else "",
                )
            else:
                pass
                # print (i, type(self.b[i]))
