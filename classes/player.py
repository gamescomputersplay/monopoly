''' Player Class
'''

from .board import Property
class Player:

    def __init__(self, name, settings):

        # Player's name and behavioral settings
        self.name = name
        self.settings = settings

        # Player's money (will be set up by the simulation)
        self.money = 0

        # Player's position
        self.position = 0

        # Owned properties
        self.owned = []

    def make_a_move(self, board, players, dice, log):
        ''' Main function for a player to make a move
        Receives:
        - a board, with all cells and other things
        - other players (in case we need to make transactions with them)
        - log handle
        '''

        log.add(f"=== Player {self.name}'s move ===")

        # Player rolls the dice
        dice_roll, dice_roll_score, dice_roll_is_double = dice.cast()
        log.add(f"Player {self.name} rolls: {dice_roll} " + 
                f"(score {dice_roll_score}{', double' if dice_roll_is_double else ''})")

        # Player moves to the new cell
        self.position += dice_roll_score
        # Get salary if we passed go on the way
        if self.position >= 40:
            self.get_salary(board, log)
        # Finish the move
        self.position %= 40
        log.add(f"Player {self.name} goes to: {board.b[self.position].name}")

        # Player lands on a property
        if isinstance(board.b[self.position], Property):
            # Property is not owned by anyone
            if board.b[self.position].owner is None:
                # Does the player want to buy it?
                if self.wants_to_buy(board.b[self.position]):
                    log.add(f"Player {self.name} landed on a property, he wants to buy it")
                else:
                    log.add(f"Player {self.name} landed on a property, he refuses to buy it")

    def get_salary(self, board, log):
        ''' Adding Salary to the player's money, according to the game's settings
        '''
        self.money += board.settings.salary
        log.add(f"Player {self.name} receives salary ${board.settings.salary}")


    def wants_to_buy(self, property_to_buy):
        ''' Check if the player is willing to buy an onowned property
        '''
        # Player has money lower than unspendable minumum
        if self.money - property_to_buy.cost_base < self.settings.unspendable_cash:
            return False

        # Player does not have enough money
        # If unspendable_cash >= 0 this check is redundant
        # However we'll need to think if a "mortgage to buy" situation
        if property_to_buy.cost_base > self.money:
            return False

        # Property is in one of the groups, player chose to ignore
        if property_to_buy.group in self.settings.ignore_property_groups:
            return False

        # Nothing stops the player from making a purchase
        return True
