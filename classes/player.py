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

        # Bankrupt (game ended for thi player)
        self.is_bankrupt = False

    def __str__(self):
        return self.name

    def make_a_move(self, board, players, dice, log):
        ''' Main function for a player to make a move
        Receives:
        - a board, with all cells and other things
        - other players (in case we need to make transactions with them)
        - log handle
        '''

        # Is player is bankrupt - do nothing
        if self.is_bankrupt:
            return None

        log.add(f"=== Player {self.name}'s move ===")

        # Improve any properties, if needed
        self.improve_properties(log)

        # Player rolls the dice
        _, dice_roll_score, dice_roll_is_double = dice.cast()

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
            self.handle_landing_on_property(board, dice, log)

        # If player went bankrupt this turn - return string "baknrupt"
        if self.is_bankrupt:
            return "bankrupt"

    def handle_landing_on_property(self, board, dice, log):
        ''' Landing on property: either buy it or pay rent
        '''
        # Property is not owned by anyone
        if board.b[self.position].owner is None:

            # Does the player want to buy it?
            if self.wants_to_buy(board.b[self.position]):
                self.buy_property(board.b[self.position])
                log.add(f"Player {self.name} bought {board.b[self.position]} " +
                        f"for ${board.b[self.position].cost_base}")
                board.recalculate_monopoly_coeffs(board.b[self.position])

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
                rent_amount = board.b[self.position].calculate_rent(dice)
                self.pay_money(rent_amount, board.b[self.position].owner, board, log)
                log.add(f"{self} pays {board.b[self.position].owner} rent ${rent_amount}")

    def get_list_of_properties_to_improve(self):
        ''' Put together a list of properties a player wants to improve, in order.
        Properties will appear several times, once for each house/hotel that can be built.
        '''
        list_to_improve = []
        for cell in self.owned:
            if cell.can_be_improved:
                # Number available to build houses from cell.has_houses + 1 to 5
                for i in range(cell.has_houses + 1, 6):
                    list_to_improve.append((i, cell.cost_house, cell))
        # It will be popped from the end, so first to build should be last
        # in the list (by default, least developed and cheaperst)
        list_to_improve.sort(key = lambda x: (-x[0], -x[1]))
        return list_to_improve

    def improve_properties(self, log):
        ''' While there is money to spend and properties to improve,
        keep building houses/hotels
        '''
        list_to_improve = self.get_list_of_properties_to_improve()
        while list_to_improve:

            _, improvement_cost, cell_to_improve = list_to_improve.pop()

            # Don't do it if you don't have money to spend
            if self.money - improvement_cost < self.settings.unspendable_cash:
                break

            # Building a house
            ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4:"4th"}

            if cell_to_improve.has_houses != 4:
                cell_to_improve.has_houses += 1
                log.add(f"{self} built {ordinal[cell_to_improve.has_houses]} " +
                        f"house on {cell_to_improve}")

            # Building a hotel
            else:
                cell_to_improve.has_houses = 0
                cell_to_improve.has_hotel = 1
                log.add(f"{self} built a hotel on {cell_to_improve}")
                # Should not be improved beyong hotel
                cell_to_improve.can_be_improved = False

            # Paying for the improvement
            self.money -= cell_to_improve.cost_house


    def get_salary(self, board, log):
        ''' Adding Salary to the player's money, according to the game's settings
        '''
        self.money += board.settings.salary
        log.add(f"Player {self.name} receives salary ${board.settings.salary}")

    def max_raisable_money(self):
        ''' How much cash a plyer can produce?
        Used to determine if they should go bankrupt or not.
        Max raisable money are 1/2 of houses cost + 1/2 of unmortgaged properties cost
        '''
        max_raisable = self.money
        for cell in self.owned:
            if cell.has_houses > 0:
                max_raisable += cell.cost_house * cell.has_houses // 2
            if cell.has_hotel > 0:
                max_raisable += cell.cost_house * 5 // 2
            if not cell.is_mortgaged:
                max_raisable += cell.cost_base // 2
        return max_raisable

    def get_list_of_properties_to_deimprove(self):
        ''' Put together a list of properties a player can sell houses from.
        '''
        list_to_deimprove = []
        for cell in self.owned:
            if cell.has_hotel == 1:
                for i in range(1, 6):
                    list_to_deimprove.append((i, cell.cost_house // 2, cell))
            if cell.has_houses > 0:
                for i in range(1, cell.has_houses + 1):
                    list_to_deimprove.append((i, cell.cost_house // 2, cell))
        # It will be popped from the end, so first to sell should be last
        list_to_deimprove.sort(key = lambda x: (x[0], x[1]))
        return list_to_deimprove

    def get_list_of_properties_to_mortgage(self):
        ''' Put together a list of properties a player can sell houses from.
        '''
        list_to_mortgage = []
        for cell in self.owned:
            if not cell.is_mortgaged:
                list_to_mortgage.append((cell.cost_base // 2, cell))

        # It will be popped from the end, so first to sell should be last
        list_to_mortgage.sort(key = lambda x: -x[0])
        return list_to_mortgage

    def raise_money(self, required_amount, board, log):
        ''' Sell houses, hotels, mortgage property until you get required_amount of money
        '''
        # Sell improvements
        list_to_deimprove = self.get_list_of_properties_to_deimprove()

        while list_to_deimprove and self.money < required_amount:
            order, sell_price, cell_to_deimprove = list_to_deimprove.pop()
            if order == 5:
                cell_to_deimprove.has_hotel = 0
                cell_to_deimprove.has_houses = 4
                cell_to_deimprove.can_be_improved = True
                log.add(f"{self} sells hotel on {cell_to_deimprove}, raising ${sell_price}")
            else:
                cell_to_deimprove.has_houses -= 1
                log.add(f"{self} sells a house on {cell_to_deimprove}, raising ${sell_price}")
            self.money += sell_price

        # Mortgage properties
        list_to_mortgage = self.get_list_of_properties_to_mortgage()
        while list_to_mortgage and self.money < required_amount:
            mortgage_price, cell_to_mortgage = list_to_mortgage.pop()
            # Mortgage this property
            cell_to_mortgage.is_mortgages = True
            self.money += mortgage_price
            board.recalculate_monopoly_coeffs(cell_to_mortgage)
            log.add(f"{self} mortgages {cell_to_mortgage}, raising ${mortgage_price}")

    def transfer_all_properties(self, payee, board, log):
        ''' Part of bankruptcy procedure, transfer all mortgaged property to the creditor
        '''
        while self.owned:
            cell_to_transfer = self.owned.pop()
            payee.owned.append(cell_to_transfer)
            board.recalculate_monopoly_coeffs(cell_to_transfer)
            log.add(f"{self} transfers {cell_to_transfer} to {payee}")

    def pay_money(self, amount, payee, board, log):
        ''' Function to pay money to another player (or bank)
        This is where Bankrupcy will be triggered.
        '''
        # Regular transaction
        if amount < self.money:
            self.money -= amount
            payee.money += amount
            return

        max_raisable_money = self.max_raisable_money()
        # Can pay but need to sell some things first
        if amount < max_raisable_money:
            log.add(f"{self} can pay ${amount}, but needs to sell some things for that")
            self.raise_money(amount, board, log)
            self.money -= amount
            payee.money += amount

        # Bunkruptcy (can't pay even after selling and morgtgaging all)
        else:
            log.add(f"{self} has to pay ${amount}, max they can raise is ${max_raisable_money}")
            self.is_bankrupt = True
            log.add(f"{self} is bankrupt")
            self.raise_money(amount, board, log)
            log.add(f"{self} gave {payee} all their remaining money (${self.money})")
            payee.money += self.money
            self.money = 0
            self.transfer_all_properties(payee, board, log)

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
