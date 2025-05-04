class Cell:
    """Base class for all board cells."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class GoToJail(Cell):
    """ Class for Go To Jail cell
    not much going on here
    """


class LuxuryTax(Cell):
    """ Class for LuxuryTax
    """


class IncomeTax(Cell):
    """ Class for IncomeTax
    """


class FreeParking(Cell):
    """ Class for Free Parking """


class Chance(Cell):
    """ Class for Chance
    """


class CommunityChest(Cell):
    """ Class for Community Chest
    """


class Property(Cell):
    """ Property Class (for Properties, Rails, Utilities)
    """

    def __init__(self, name, cost_base, rent_base, cost_house, rent_house, group):
        """
        Example of parameters for a property:
        "B2 Vermont Avenue", 100, 6, 50, (30, 90, 270, 400, 550), "Lightblue"
        """
        super().__init__(name)

        # Initial parameters (usually found on a property card):
        # Cost to buy the property
        self.cost_base = cost_base
        # Base rent (no houses)
        self.rent_base = rent_base
        # Cost to build a house /hotel
        self.cost_house = cost_house
        # Rent with 1/2/3/4 houses and a hotel (a tuple of 5 values)
        self.rent_house = rent_house
        # Group of the property (color, or "Railroads", "Utilities")
        self.group = group

        # Current state of the property
        # Owner of the property (Will be a Player object or None if not owned)
        self.owner = None
        # Is the property mortgaged
        self.is_mortgaged = False

        # Multiplier to calculate rent
        # regular properties: 1/2, railways: 1/2/4/8, utilities: 4/10)
        self.monopoly_multiplier = 1

        # Number of houses/hotel on the property
        self.has_houses = 0
        self.has_hotel = 0

    def calculate_rent(self, dice):
        """ Calculate the rent amount for this property, including monopoly, houses etc.
        dice are used to calculate rent for utilities
        """
        # There is a hotel on this property
        if self.has_hotel == 1:
            return self.rent_house[-1]

        # There are 1 or more houses on this property
        if self.has_houses:
            return self.rent_house[self.has_houses - 1]

        if self.group != "Utilities":
            # Undeveloped monopoly: double rent
            # Rails: multiply rent depending on how many owned
            return self.rent_base * self.monopoly_multiplier

        # Utilities: Dice roll * 4/10
        _, dice_points, _ = dice.cast()
        return dice_points * self.monopoly_multiplier
