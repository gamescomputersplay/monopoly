''' Class to hold board information
'''

class Cell:
    """ Generic Cell Class, base for other classes
    """

    def __init__(self, name):
        self.name = name


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
        self.is_monopoly = False
        self.has_houses = 0
        self.has_hotel = 0

    def __str__(self):
        return self.name

    def calculate_rent(self):
        ''' Calculate the rent amount for this property, including monopoly, houses etc
        '''
        # There is a hotel on this property
        if self.has_hotel:
            return self.rent_house[-1]

        # There are houses on this property
        if self.has_houses:
            return self.rent_house[self.has_houses - 1]

        # Monopoly: double rent on undeveloped properties
        if self.is_monopoly:
            return self.rent_base * 2

        # Otherwise, just the base rent
        return self.rent_base
class Board:
    ''' Class collecting board repalted information:
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
            "A1 Mediterraneal Avenue", 60, 2, 50, (10, 30, 90, 160, 250), "Brown"))
        self.b.append(Cell("COM1 Community Chest"))
        self.b.append(Property(
            "A2 Baltic Avenue", 60, 4, 50, (20, 60, 180, 320, 450), "Brown"))
        self.b.append(Cell("PT Property Tax"))

        # 5-9
        self.b.append(Property(
            "R1 Reading railroad", 200, 0, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "B1 Oriental Avenue", 100, 6, 50, (30, 90, 270, 400, 550), "Lightblue"))
        self.b.append(Cell("CH1 Chance"))
        self.b.append(Property(
            "B2 Vermont Avenue", 100, 6, 50, (30, 90, 270, 400, 550), "Lightblue"))
        self.b.append(Property(
            "B3 Connecticut Avenue",120,8,50,(40, 100, 300, 450, 600),"Lightblue"))

        # 10-14
        self.b.append(Cell("PR Prison"))
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
            "R2 Pennsylvania Railroad", 200, 0, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "D1 St.James Place", 180, 14, 100, (70, 200, 550, 700, 950), "Orange"))
        self.b.append(Cell("COM2 Community Chest"))
        self.b.append(Property(
            "D2 Tennessee Avenue", 180, 14, 100, (70, 200, 550, 700, 950), "Orange"))
        self.b.append(Property(
            "D3 New York Avenue", 200, 16, 100, (80, 220, 600, 800, 1000), "Orange"))

        # 20-24
        self.b.append(Cell("FP Free Parking"))
        self.b.append(Property(
            "E1 Kentucky Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), "Red"))
        self.b.append(Cell("CH2 Chance"))
        self.b.append(Property(
            "E2 Indiana Avenue", 220, 18, 150, (90, 250, 700, 875, 1050), "Red"))
        self.b.append(Property(
            "E3 Illinois Avenue", 240, 20, 150, (100, 300, 750, 925, 1100), "Red"))

        # 25-29
        self.b.append(Property(
            "R3 BnO Railroad", 200, 0, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Property(
            "F1 Atlantic Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), "Yellow"))
        self.b.append(Property(
            "F2 Ventinor Avenue", 260, 22, 150, (110, 330, 800, 975, 1150), "Yellow"))
        self.b.append(Property(
            "U2 Waterworks", 150, 0, 0, (0, 0, 0, 0, 0), "Utilities"))
        self.b.append(Property(
            "F3 Martin Gardens", 280, 24, 150, (120, 360, 850, 1025, 1200), "Yellow"))

        # 30-34
        self.b.append(Cell("GTJ Go To Jail"))
        self.b.append(Property(
            "G1 Pacific Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), "Green"))
        self.b.append(Property(
            "G2 North Carolina Avenue", 300, 26, 200, (130, 390, 900, 1100, 1275), "Green"))
        self.b.append(Cell("COM3 Community Chest"))
        self.b.append(Property(
            "G3 Pennsylvania Avenue", 320, 28, 200, (150, 450, 100, 1200, 1400), "Green"))

        # 35-39
        self.b.append(Property(
            "R4 Short Line", 200, 0, 0, (0, 0, 0, 0, 0), "Railroads"))
        self.b.append(Cell("CH3 Chance"))
        self.b.append(Property(
            "H1 Park Place", 350, 35, 200, (175, 500, 1100, 1300, 1500), "Indigo"))
        self.b.append(Cell("LT Luxury Tax"))
        self.b.append(Property(
            "H2 Boardwalk", 400, 50, 200, (200, 600, 1400, 1700, 2000), "Indigo"))

    def check_if_monopoly(self, property_to_check):
        ''' Checks if property_to_check is a monopoly. If it is (or isn't),
        sets the monopoly flags on the property.
        Returns True or False if the property is a monopoly
        '''
        # This is the group we'll be looking at
        group_to_check = property_to_check.group

        # Collect all owners of this group in this set.
        owners = set()
        for cell in self.b:
            if isinstance(cell, Property) and cell.group == group_to_check:
                owners.add(cell.owner)

        # It is a monopoly: update the monopoly status
        if len(owners) == 1 and None not in owners:
            for cell in self.b:
                if isinstance(cell, Property) and cell.group == group_to_check:
                    cell.is_monopoly = True
            return True
        # It is a NOT monopoly: also update the monopoly status
        for cell in self.b:
            if isinstance(cell, Property) and cell.group == group_to_check:
                cell.is_monopoly = False
        return False
