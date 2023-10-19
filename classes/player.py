''' Player Class
'''

from classes.board import Property


class Player:
    ''' Class to contain player-replated into and actions:
    - money, position, owned property
    - actions to buy property of hadle Chance cards etc
    '''

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

    def __str__(self):
        return self.name

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
                    self.buy_property(board.b[self.position])
                    log.add(f"Player {self.name} bought {board.b[self.position]} " +
                            f"for ${board.b[self.position].cost_base}")
                    monopoly_was_created = board.check_if_monopoly(board.b[self.position])
                    if monopoly_was_created:
                        log.add(f"{board.b[self.position].group} is now a monopoly")

                else:
                    log.add(f"Player {self.name} landed on a property, he refuses to buy it")

            # Property has an owner
            else:
                # It is mortgaged: no action
                if board.b[self.position].is_mortgaged:
                    log.add("Property is mortgaged, no rent")
                # It is mortgaged: no action
                elif board.b[self.position].owner == self:
                    log.add("Own property, no rent")
                # Handle rent payments
                else:
                    log.add(f"Player {self.name} landed on a property, " +
                            f"owned by {board.b[self.position].owner}")
                    rent_amount = board.b[self.position].calculate_rent()
                    self.money -= rent_amount
                    board.b[self.position].owner.money += rent_amount
                    log.add(f"{self} pays {board.b[self.position].owner} rent ${rent_amount}")


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

    def buy_property(self, property_to_buy):
        ''' Player buys the property
        '''
        property_to_buy.owner = self
        self.owned.append(property_to_buy)
        self.money -= property_to_buy.cost_base
