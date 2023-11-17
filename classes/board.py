''' Class to hold board information
'''

from settings import GameSettings

class Cell:
    """ Generic Cell Class, base for other classes
    """

    def __init__(self, name):
        self.name = name

class GoToJail(Cell):
    ''' Class for Go To Jail cell
    not much going on here
    '''

class LuxuryTax(Cell):
    ''' Class for LuxuryTax
    '''

class IncomeTax(Cell):
    ''' Class for IncomeTax
    '''

class FreeParking(Cell):
    ''' Class for IncomeTax
    '''

class Chance(Cell):
    ''' Class for Chance
    '''

class CommunityChest(Cell):
    ''' Class for Chance
    '''

class Property(Cell):
    ''' Property Class (for Properties, Rails, Utilities)
    '''

    def __init__(self, name, cost_base, rent_base, cost_house, rent_house, group):
        super().__init__(name)
        self.cost_base = cost_base
        self.rent_base = rent_base
        self.cost_house = cost_house
        self.rent_house = rent_house
        self.group = group
        self.owner = None
        self.is_mortgaged = False

        # Multiplier to calculate rent(1 - no monopoly, 2 - monopoly,
        # 2/4/8 - railways, 4/10 - utilities)
        self.monopoly_coef = 1

        # Flag that indicates that a property can be built on
        self.can_be_improved = False

        self.has_houses = 0
        self.has_hotel = 0

    def __str__(self):
        return self.name

    def calculate_rent(self, dice):
        ''' Calculate the rent amount for this property, including monopoly, houses etc.
        dice are used to calculate rent for utilities
        '''
        # There is a hotel on this property
        if self.has_hotel == 1:
            return self.rent_house[-1]

        # There are houses on this property
        if self.has_houses:
            return self.rent_house[self.has_houses - 1]

        if self.group != "Utilities":
            # Monopoly: double rent on undeveloped properties
            # Rails: multiply rent depending on how many owned
            return self.rent_base * self.monopoly_coef

        # Utilities: Dice roll * 4/10
        _, dice_points, _ = dice.cast()
        return dice_points * self.monopoly_coef

class Deck:
    ''' Parent for Community Chest and Chance cards
    '''
    def __init__(self, cards):
        # List of cards
        self.cards = cards
        # Pointer to a next card to draw
        self.pointer = 0

    def draw(self):
        ''' Draw one card from the deck
        (and put it underneath, so the deck will cycle through the same cycle)
        '''
        drawn_card = self.cards[self.pointer]
        self.pointer += 1
        if self.pointer == len(self.cards):
            self.pointer = 0
        return drawn_card
    
    def shuffle(self, random_thing):
        ''' Shuffle the cards. Uses random thing, so we could use thread-safe random generator
        '''
        random_thing.shuffle(self.cards)

class Board:
    ''' Class collecting board related information:
    properties and their owners, build houses, etc
    '''

    def __init__(self, settings):
        ''' Initialize board configuration: properties, special cells etc
        '''
        # Keep a copy of game settings (to use in in-game calculations)
        self.settings = settings

        self.b = []

        # 0-4
        self.b.append(Cell("GO"))
        self.b.append(Property(
            "A1 Mediterranean Avenue", 60, 2, 50, (10, 30, 90, 160, 250), "Brown"))
        self.b.append(CommunityChest("COM1 Community Chest"))
        self.b.append(Property(
            "A2 Baltic Avenue", 60, 4, 50, (20, 60, 180, 320, 450), "Brown"))
        self.b.append(IncomeTax("IT Income Tax"))

        # 5-9
        self.b.append(Property(
            "R1 Reading railroad", 200, 25, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "B1 Oriental Avenue", 100, 6, 50, (30, 90, 270, 400, 550), "Lightblue"))
        self.b.append(Chance("CH1 Chance"))
        self.b.append(Property(
            "B2 Vermont Avenue", 100, 6, 50, (30, 90, 270, 400, 550), "Lightblue"))
        self.b.append(Property(
            "B3 Connecticut Avenue",120,8,50,(40, 100, 300, 450, 600),"Lightblue"))

        # 10-14
        self.b.append(Cell("JL Jail"))
        self.b.append(Property(
            "C1 St.Charle's Place", 140, 10, 100, (50, 150, 450, 625, 750), "Pink"))
        self.b.append(Property(
            "U1 Electric Company", 150, 0, 0, (0, 0, 0, 0, 0), "Utilities"))
        self.b.append(Property(
            "C2 States Avenue", 140, 10, 100, (50, 150, 450, 625, 750), "Pink"))
        self.b.append(Property(
            "C3 Virginia Avenue", 160, 12, 100, (60, 180, 500, 700, 900), "Pink"))

        # 15-19
        self.b.append(Property(
            "R2 Pennsylvania Railroad", 200, 25, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "D1 St.James Place", 180, 14, 100, (70, 200, 550, 700, 950), "Orange"))
        self.b.append(CommunityChest("COM2 Community Chest"))
        self.b.append(Property(
            "D2 Tennessee Avenue", 180, 14, 100, (70, 200, 550, 700, 950), "Orange"))
        self.b.append(Property(
            "D3 New York Avenue", 200, 16, 100, (80, 220, 600, 800, 1000), "Orange"))

        # 20-24
        self.b.append(FreeParking("FP Free Parking"))
        self.b.append(Property(
            "E1 Kentucky Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), "Red"))
        self.b.append(Chance("CH2 Chance"))
        self.b.append(Property(
            "E2 Indiana Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), "Red"))
        self.b.append(Property(
            "E3 Illinois Avenue", 240, 20, 150, (100, 300, 750, 925, 1100), "Red"))

        # 25-29
        self.b.append(Property(
            "R3 BnO Railroad", 200, 25, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "F1 Atlantic Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), "Yellow"))
        self.b.append(Property(
            "F2 Ventinor Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), "Yellow"))
        self.b.append(Property(
            "U2 Waterworks", 150, 0, 0, (0, 0, 0, 0, 0), "Utilities"))
        self.b.append(Property(
            "F3 Martin Gardens", 280, 24, 150, (120, 360, 850, 1025, 1200), "Yellow"))

        # 30-34
        self.b.append(GoToJail("GTJ Go To Jail"))
        self.b.append(Property(
            "G1 Pacific Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), "Green"))
        self.b.append(Property(
            "G2 North Carolina Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), "Green"))
        self.b.append(CommunityChest("COM3 Community Chest"))
        self.b.append(Property(
            "G3 Pennsylvania Avenue", 320, 28, 200, (150, 450, 100, 1200, 1400), "Green"))

        # 35-39
        self.b.append(Property(
            "R4 Short Line", 200, 25, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Chance("CH3 Chance"))
        self.b.append(Property(
            "H1 Park Place", 350, 35, 200, (175, 500, 1100, 1300, 1500), "Indigo"))
        self.b.append(LuxuryTax("LT Luxury Tax"))
        self.b.append(Property(
            "H2 Boardwalk", 400, 50, 200, (200, 600, 1400, 1700, 2000), "Indigo"))

        # Board fields, grouped by group self.groups["Green"] - list of all greens
        self.groups = self.property_groups()

        # For "Free parking money" rule. How much money are on "Free Parking"
        self.free_parking_money = 0

        # Available houses and hotels
        self.available_houses = GameSettings.available_houses
        self.available_hotels = GameSettings.available_hotels

        # Chance deck
        self.chance = Deck([
            "Chance 1",
            "Chance 2",
            "Chance 3",
            "Chance 4"
        ])

        # Community Chest deck
        self.chest = Deck([
            "Community Chest 1",
            "Community Chest 2",
            "Community Chest 3",
            "Community Chest 4"
        ])

    def property_groups(self):
        ''' self.groups is a convenient way to group cells by the group,
        so we don't have to check all properties on the board, to, for example,
        update their monopoly status
        '''
        groups = {}
        for cell in self.b:
            if not isinstance(cell, Property):
                continue
            if cell.group not in groups:
                groups[cell.group] = []
            groups[cell.group].append(cell)
        return groups

    def log_current_state(self, log):
        ''' Log current state of the houses/hotels, free parking money
        '''
        log.add(f"Available houses/hotels: {self.available_houses}/{self.available_hotels}")
        if GameSettings.free_parking_money:
            log.add(f"Free Parking Money: ${self.free_parking_money}")

    def log_current_map(self, log):
        ''' Log current situation on the board,
        who owns what, monopolies, improvements, etc
        '''
        log.add("\n== BOARD ==")
        for cell in self.b:
            if not isinstance(cell, Property):
                continue
            improvements = "none"
            if cell.has_hotel == 1:
                improvements = "hotel"
            if cell.has_houses > 0:
                improvements = f"{cell.has_houses} house(s)"
            log.add(f"- {cell.name}, Owner: {cell.owner}, " +
                    f"Rent coef: {cell.monopoly_coef}, Can improve: {cell.can_be_improved}, " +
                    f"Improvements: {improvements}")

    def recalculate_monopoly_coeffs(self, changed_cell):
        ''' Go through all properties and set monopoly_coef,
        depending of how many properties in teh same group players own.
        Would be run every time, when property ownership change.
        '''

        # Create and populate list of owners for this group
        owners = []

        has_mortgages = False
        for cell in self.groups[changed_cell.group]:
            owners.append(cell.owner)
            if cell.is_mortgaged:
                has_mortgages = True

        # Update monopoly_coeff
        for cell in self.groups[changed_cell.group]:

            # Go through cells. For each cell count how many properties
            # in a group owner of this cell has
            ownership_count = owners.count(cell.owner)

            # For railroad it is 1/2/4/8 (or 2**(n-1))
            if cell.group == "Railroads":
                cell.monopoly_coeff = 2 ** (ownership_count - 1)

            # For Utilities it is either 4 or 10
            elif cell.group == "Utilities":
                if ownership_count == 2:
                    cell.monopoly_coeff = 10
                else:
                    cell.monopoly_coeff = 4

            # For all other properties it is 1 or 2
            else:
                # Reset "can improve" flag
                cell.can_be_improved = False

                # This is a monopoly (owner owns all properties of this color)
                if ownership_count == len(self.groups[changed_cell.group]):
                    # Rent coefficient for unimproved cells is 2
                    cell.monopoly_coeff = 2
                    # And, unless it already has a hotel, it can be improved
                    # And unless one of the properties of this group is mortgaged
                    if cell.has_hotel == 0 and not has_mortgages:
                        cell.can_be_improved = True
                else:
                    cell.monopoly_coeff = 1

        return
