""" Class to hold board information.
That includes:
    - Properties
    - Special cells (Go, Jail, etc.)
    - Decks (Chance, Community Chest)
"""
from monopoly.core.cell import Cell, GoToJail, LuxuryTax, IncomeTax, FreeParking, Chance, CommunityChest, Property
from monopoly.core.deck import Deck
from settings import GameSettings

INDIGO = "Indigo"
GREEN = "Green"
YELLOW = "Yellow"
RED = "Red"
ORANGE = "Orange"
PINK = "Pink"
LIGHTBLUE = "Lightblue"
BROWN = "Brown"
RAILROADS = "Railroads"
UTILITIES = "Utilities"


class Board:
    """ Class collecting board-related information:
    properties and their owners, build houses, etc.
    """

    def __init__(self, settings):
        """ Initialize board configuration: properties, special cells etc
        """
        # Keep a copy of game settings (to use in in-game calculations)
        self.settings = settings

        self.cells = []
        # 0-4
        self.cells.append(Cell("GO"))
        self.cells.append(Property("A1 Mediterranean Avenue", 60, 2, 50, (10, 30, 90, 160, 250), BROWN))
        self.cells.append(CommunityChest("COM1 Community Chest"))
        self.cells.append(Property("A2 Baltic Avenue", 60, 4, 50, (20, 60, 180, 320, 450), BROWN))
        self.cells.append(IncomeTax("IT Income Tax"))
        # 5-9
        self.cells.append(Property("R1 Reading Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
        self.cells.append(Property("B1 Oriental Avenue", 100, 6, 50, (30, 90, 270, 400, 550), LIGHTBLUE))
        self.cells.append(Chance("CH1 Chance"))
        self.cells.append(Property("B2 Vermont Avenue", 100, 6, 50, (30, 90, 270, 400, 550), LIGHTBLUE))
        self.cells.append(Property("B3 Connecticut Avenue", 120, 8, 50, (40, 100, 300, 450, 600), LIGHTBLUE))
        # 10-14
        self.cells.append(Cell("JL Jail"))
        self.cells.append(Property("C1 St. Charles Place", 140, 10, 100, (50, 150, 450, 625, 750), PINK))
        self.cells.append(Property("U1 Electric Company", 150, 0, 0, (0, 0, 0, 0, 0), UTILITIES))
        self.cells.append(Property("C2 States Avenue", 140, 10, 100, (50, 150, 450, 625, 750), PINK))
        self.cells.append(Property("C3 Virginia Avenue", 160, 12, 100, (60, 180, 500, 700, 900), PINK))
        # 15-19
        self.cells.append(Property("R2 Pennsylvania Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
        self.cells.append(Property("D1 St. James Place", 180, 14, 100, (70, 200, 550, 700, 950), ORANGE))
        self.cells.append(CommunityChest("COM2 Community Chest"))
        self.cells.append(Property("D2 Tennessee Avenue", 180, 14, 100, (70, 200, 550, 700, 950), ORANGE))
        self.cells.append(Property("D3 New York Avenue", 200, 16, 100, (80, 220, 600, 800, 1000), ORANGE))
        # 20-24
        self.cells.append(FreeParking("FP Free Parking"))
        self.cells.append(Property("E1 Kentucky Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), RED))
        self.cells.append(Chance("CH2 Chance"))
        self.cells.append(Property("E2 Indiana Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), RED))
        self.cells.append(Property("E3 Illinois Avenue", 240, 20, 150, (100, 300, 750, 925, 1100), RED))
        # 25-29
        self.cells.append(Property("R3 B&O Railroad", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
        self.cells.append(Property("F1 Atlantic Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), YELLOW))
        self.cells.append(Property("F2 Ventnor Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), YELLOW))
        self.cells.append(Property("U2 Waterworks", 150, 0, 0, (0, 0, 0, 0, 0), UTILITIES))
        self.cells.append(Property("F3 Marvin Gardens", 280, 24, 150, (120, 360, 850, 1025, 1200), YELLOW))
        # 30-34
        self.cells.append(GoToJail("GTJ Go To Jail"))
        self.cells.append(Property("G1 Pacific Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), GREEN))
        self.cells.append(Property("G2 North Carolina Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), GREEN))
        self.cells.append(CommunityChest("COM3 Community Chest"))
        self.cells.append(Property("G3 Pennsylvania Avenue", 320, 28, 200, (150, 450, 1000, 1200, 1400), GREEN))
        # 35-39
        self.cells.append(Property("R4 Short Line", 200, 25, 0, (0, 0, 0, 0, 0), RAILROADS))
        self.cells.append(Chance("CH3 Chance"))
        self.cells.append(Property("H1 Park Place", 350, 35, 200, (175, 500, 1100, 1300, 1500), INDIGO))
        self.cells.append(LuxuryTax("LT Luxury Tax"))
        self.cells.append(Property("H2 Boardwalk", 400, 50, 200, (200, 600, 1400, 1700, 2000), INDIGO))

        # Board fields, grouped by group self.groups["Green"] - list of all greens
        self.groups = self.create_property_groups()

        # when the "Free Parking" rule is active, Keep track of the amount of money at the "Free parking money"
        self.free_parking_money = 0

        # Available houses and hotels
        self.available_houses = GameSettings.available_houses
        self.available_hotels = GameSettings.available_hotels

        # Chance deck
        self.chance = Deck([
            "Advance to Boardwalk",
            "Advance to Go (Collect $200)",
            "Advance to Illinois Avenue. If you pass Go, collect $200",
            "Advance to St. Charles Place. If you pass Go, collect $200",
            "Advance to the nearest Railroad. If owned, pay owner twice " + \
            "the rental to which they are otherwise entitled",
            "Advance to the nearest Railroad. If owned, pay owner twice " + \
            "the rental to which they are otherwise entitled",
            "Advance token to nearest Utility. " + \
            "If owned, throw dice and pay owner a total ten times amount thrown.",
            "Bank pays you dividend of $50",
            "Get Out of Jail Free",
            "Go Back 3 Spaces",
            "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200",
            "Make general repairs on all your property. For each house pay $25. " + \
            "For each hotel pay $100",
            "Speeding fine $15",
            "Take a trip to Reading Railroad. If you pass Go, collect $200",
            "You have been elected Chairman of the Board. Pay each player $50",
            "Your building loan matures. Collect $150"
        ])

        # Community Chest deck
        self.chest = Deck([
            "Advance to Go (Collect $200)",
            "Bank error in your favor. Collect $200",
            "Doctor's fee. Pay $50",
            "From sale of stock you get $50",
            "Get Out of Jail Free",
            "Go to Jail. Go directly to jail, do not pass Go, do not collect $200",
            "Holiday fund matures. Receive $100",
            "Income tax refund. Collect $20",
            "It is your birthday. Collect $10 from every player",
            "Life insurance matures. Collect $100",
            "Pay hospital fees of $100",
            "Pay school fees of $50",
            "Receive $25 consultancy fee",
            "You are assessed for street repair. $40 per house. $115 per hotel",
            "You have won second prize in a beauty contest. Collect $10",
            "You inherit $100"
        ])

    def create_property_groups(self):
        """ self.groups is a convenient way to group cells by color/type,
        so we don't have to check all properties on the board, to, for example,
        update their monopoly status.
        This function populates self.groups with all properties
        """
        groups = {}
        for cell in self.cells:
            if not isinstance(cell, Property):
                continue
            if cell.group not in groups:
                groups[cell.group] = []
            groups[cell.group].append(cell)
        return groups

    def log_board_state(self, log):
        """ Log the current state of the houses/hotels, free parking money
        """
        log.add(f"Available houses/hotels: {self.available_houses}/{self.available_hotels}")
        if GameSettings.free_parking_money:
            log.add(f"Free Parking Money: ${self.free_parking_money}")

    def log_current_map(self, log):
        """ Log the current situation on the board,
        who owns what, monopolies, improvements, etc.
        """
        log.add("\n== BOARD ==")
        for cell in self.cells:
            if not isinstance(cell, Property):
                continue
            improvements = "none"
            if cell.has_hotel == 1:
                improvements = "hotel"
            if cell.has_houses > 0:
                improvements = f"{cell.has_houses} house(s)"
            # Log property name, owner, rent multipliers, improvements:
            # G1 Pacific Avenue, Owner: Exp, Rent multiplier: 2, Can improve: False, Improvements: hotel
            log.add(f"- {cell.name}, Owner: {cell.owner}, " +
                    f"Rent multiplier: {cell.monopoly_multiplier}, Improvements: {improvements}")

    def recalculate_monopoly_multipliers(self, changed_cell):
        """ Go through all properties in the property group and update flags:
        - monopoly_multiplier
        runs every time property ownership changes.
        1. Properties can have 1/2 depending on if the player owns a monopoly.
        2. Railroads can have 1/2/4/8 depending on how many owned
        3. Utilities can have 4/10 depending on if owning one or both
        """

        # To check if this is a monopoly, we need to know how many owners are there in a group
        owners = [cell.owner for cell in self.groups[changed_cell.group]]

        # Update monopoly_multipliers
        for cell in self.groups[changed_cell.group]:
            ownership_count = owners.count(cell.owner)

            # For railroad, it is 1/2/4/8 (or 2**(n-1))
            if cell.group == RAILROADS:
                cell.monopoly_multiplier = 2 ** (ownership_count - 1)

            # For Utilities, it is either 4 or 10
            elif cell.group == UTILITIES:
                if ownership_count == 2:
                    cell.monopoly_multiplier = 10
                else:
                    cell.monopoly_multiplier = 4

            # For all other properties it is 2 (monopoly) or 1 (no monopoly)
            # It is a monopoly if the player owns as all properties in the group
            elif ownership_count == len(self.groups[changed_cell.group]):
                cell.monopoly_multiplier = 2
            else:
                cell.monopoly_multiplier = 1

        return
