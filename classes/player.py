''' Player Class
'''

from classes.board import Property, GoToJail, LuxuryTax, IncomeTax
from classes.board import FreeParking, Chance, CommunityChest
from settings import GameSettings

class Player:
    ''' Class to contain player-replated into and actions:
    - money, position, owned property
    - actions to buy property of handle Chance cards etc
    '''

    def __init__(self, name, settings):

        # Player's name and behavioral settings
        self.name = name
        self.settings = settings

        # Player's money (will be set up by the simulation)
        self.money = 0

        # Player's position
        self.position = 0

        # Person's roll double and jail status
        self.in_jail = False
        self.had_doubles = 0
        self.days_in_jail = 0

        # Owned properties
        self.owned = []

        # List of properties player wants to sell / buy
        # through trading with other players
        self.wants_to_sell = set()
        self.wants_to_buy = set()

        # Bankrupt (game ended for thi player)
        self.is_bankrupt = False

        # Placeholder for various flags used throughout the game
        self.other_notes = ""

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

        # Look for a trade opportunity
        while self.do_a_two_way_trade(players, board, log):
            pass

        # Unmortgage, if there is enough money for it
        while self.unmortgage_a_property(board, log):
            pass

        # Improve any properties, if needed
        self.improve_properties(board, log)



        # Player rolls the dice
        _, dice_roll_score, dice_roll_is_double = dice.cast()

        # Get doubles for the third time: go to jail
        if dice_roll_is_double and self.had_doubles == 2:
            self.go_to_jail("rolled 3 doubles in a row", log)
            return

        # Player is currently in jail
        if self.in_jail:
            # Will return True if player stays in jail and move ends
            if self.handle_jail(dice_roll_is_double, board, log):
                return

        # Player moves to the new cell
        self.position += dice_roll_score
        # Get salary if we passed go on the way
        if self.position >= 40:
            self.get_salary(board, log)
        # Finish the move
        self.position %= 40
        log.add(f"Player {self.name} goes to: {board.b[self.position].name}")

        # Handle various types of cells player may land on

        # Both cards should be before landing on property
        # (as they may send player to a property)

        # Player lands on "Chance"
        if isinstance(board.b[self.position], Chance):
            self.handle_chance(board, log)

        # Player lands on "Community Chest"
        if isinstance(board.b[self.position], CommunityChest):
            self.handle_community_chest(board, log)


        # Player lands on a property
        if isinstance(board.b[self.position], Property):
            self.handle_landing_on_property(board, players, dice, log)

        # Player lands on "Go To Jail"
        if isinstance(board.b[self.position], GoToJail):
            self.go_to_jail("landed on Go To Jail", log)
            # End turn for this player, even if it was a double
            return

        # Player lands on "Free Parking"
        if isinstance(board.b[self.position], FreeParking):
            # If Free Parking Money house rule is on: get the money
            if GameSettings.free_parking_money:
                log.add(f"{self} gets ${board.free_parking_money} from Free Parking")
                self.money += board.free_parking_money
                board.free_parking_money = 0

        # Player lands on "Luxury Tax"
        if isinstance(board.b[self.position], LuxuryTax):
            self.pay_money(GameSettings.luxury_tax, "bank", board, log)
            if not self.is_bankrupt:
                log.add(f"{self} pays Luxury Tax ${GameSettings.luxury_tax}")

        # Player lands on "Income Tax"
        if isinstance(board.b[self.position], IncomeTax):
            self.handle_income_tax(board, log)

        # Reset Other notes flag
        self.other_notes = ""

        # If player went bankrupt this turn - return string "bankrupt"
        if self.is_bankrupt:
            return "bankrupt"

        # If the roll was a double
        if dice_roll_is_double:
            # Keep track of doubles in a row
            self.had_doubles += 1
            # We already handled sending to jail, so player just goes again
            log.add(f"{self} rolled a double ({self.had_doubles} in a row) so they go again.")
            self.make_a_move(board, players, dice, log)
        # If now a double: reset double counter
        else:
            self.had_doubles = 0

    def net_worth(self):
        ''' Calculate player's net worth (cache + property + houses)
        '''
        net_worth = int(self.money)

        for cell in self.owned:

            # This is against "classic rules", where mortgages property
            # calculated as 100% for net worth
            # But it doesn't make sense! So I use 1 - mortgage
            if cell.is_mortgaged:
                net_worth += cell.cost_base * (1 - GameSettings.mortgage_value)
            else:
                net_worth += cell.cost_base
                net_worth += (cell.has_houses + cell.has_hotel) * cell.cost_house

        return net_worth

    def handle_jail(self, dice_roll_is_double, board, log):
        ''' Handle player being in Jail
        Return True if the player stays in jail (to end his turn)
        '''
        # Get out of jail on rolling double
        if dice_roll_is_double:
            log.add(f"{self} rolled a double, a leaves jail for free")
            self.in_jail = False
            self.days_in_jail = 0
        # Get out of jail and pay fine
        elif self.days_in_jail == 2: # It's your third day
            log.add(f"{self} did not rolled a double for the third time, " +
                    f"pays {GameSettings.exit_jail_fine} and leaves jail")
            self.pay_money(GameSettings.exit_jail_fine, "bank", board, log)
            self.in_jail = False
            self.days_in_jail = 0
        # Stay in jail for another turn
        else:
            log.add(f"{self} stays in jail")
            self.days_in_jail  += 1
            return True
        return False


    def handle_chance(self, board, log):
        ''' Draw and act on a Chance card
        '''
        card = board.chance.draw()
        log.add(f"{self} drew Chance card: '{card}'")
        if card == "Advance to Boardwalk":
            log.add(f"{self} goes to {board.b[39]}")
            self.position = 39

        elif card == "Advance to Go (Collect $200)":
            log.add(f"{self} goes to {board.b[0]}")
            self.position = 0
            self.get_salary(board, log)

        elif card == "Advance to Illinois Avenue. If you pass Go, collect $200":
            log.add(f"{self} goes to {board.b[24]}")
            if self.position > 24:
                self.get_salary(board, log)
            self.position = 24

        elif card == "Advance to St. Charles Place. If you pass Go, collect $200":
            log.add(f"{self} goes to {board.b[11]}")
            if self.position > 11:
                self.get_salary(board, log)
            self.position = 11

        elif card == "Advance to the nearest Railroad. " + \
                     "If owned, pay owner twice the rental to which they are otherwise entitled":
            nearest_railroad = self.position
            while (nearest_railroad - 5) % 10 != 0:
                nearest_railroad += 1
                nearest_railroad %= 40
            log.add(f"{self} goes to {board.b[nearest_railroad]}")
            if self.position > nearest_railroad:
                self.get_salary(board, log)
            self.position = nearest_railroad
            self.other_notes = "double rent"


    def handle_community_chest(self, board, log):
        ''' Draw and act on a Community Chest card
        '''
        card = board.chest.draw()
        log.add(f"{self} drew Community Chest card: '{card}'")


    def handle_income_tax(self, board, log):
        ''' Handle Income tax: choose which option
        (fix or %) is less money and go with it
        '''
        # Choose smaller between fixed rate and percentage
        tax_to_pay = min(
            GameSettings.income_tax,
            int(GameSettings.income_tax_percentage * self.net_worth()))

        if tax_to_pay == GameSettings.income_tax:
            log.add(f"{self} pays fixed Income tax {GameSettings.income_tax}")
        else:
            log.add(f"{self} pays {GameSettings.income_tax_percentage * 100:.0f}% " +
                    f"Income tax {tax_to_pay}")
        self.pay_money(tax_to_pay, "bank", board, log)

    def handle_landing_on_property(self, board, players, dice, log):
        ''' Landing on property: either buy it or pay rent
        '''
        # Property is not owned by anyone
        if board.b[self.position].owner is None:

            # Does the player want to buy it?
            if self.is_willing_to_buy_property(board.b[self.position]):
                # Buy property
                self.buy_property(board.b[self.position])
                log.add(f"Player {self.name} bought {board.b[self.position]} " +
                        f"for ${board.b[self.position].cost_base}")

                # Recalculate all monopoly / can build flags
                board.recalculate_monopoly_coeffs(board.b[self.position])

                # Recalculate who wants to buy what
                # (for all players, it may affect their decisions too)
                for player in players:
                    player.update_lists_of_properties_to_trade(board)

            else:
                log.add(f"Player {self.name} landed on a property, he refuses to buy it")

        # Property has an owner
        else:
            # It is mortgaged: no action
            if board.b[self.position].is_mortgaged:
                log.add("Property is mortgaged, no rent")
            # It is player's own property
            elif board.b[self.position].owner == self:
                log.add("Own property, no rent")
            # Handle rent payments
            else:
                log.add(f"Player {self.name} landed on a property, " +
                        f"owned by {board.b[self.position].owner}")
                rent_amount = board.b[self.position].calculate_rent(dice)
                if self.other_notes == "double rent":
                    rent_amount *= 2
                    log.add("Per Chance card, rent is doubled.")
                self.pay_money(rent_amount, board.b[self.position].owner, board, log)
                if not self.is_bankrupt:
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
        # in the list (most developed)
        list_to_improve.sort(key = lambda x: (x[0], -x[1]))
        return list_to_improve

    def improve_properties(self, board, log):
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

            if cell_to_improve.has_houses != 4 and board.available_houses > 0:
                cell_to_improve.has_houses += 1
                board.available_houses -= 1
                log.add(f"{self} built {ordinal[cell_to_improve.has_houses]} " +
                        f"house on {cell_to_improve}")
                # Paying for the improvement
                self.money -= cell_to_improve.cost_house

            # Building a hotel
            elif cell_to_improve.has_houses == 4 and board.available_hotels > 0:
                cell_to_improve.has_houses = 0
                cell_to_improve.has_hotel = 1
                board.available_houses += 4
                board.available_hotels -= 1
                # Paying for the improvement
                self.money -= cell_to_improve.cost_house
                log.add(f"{self} built a hotel on {cell_to_improve}")
                # Should not be improved beyond hotel
                cell_to_improve.can_be_improved = False


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
        [(n_of_houses, cost_of_house, cell), ...]
        List will be sorted to have less developed properties first
        '''
        list_of_hotels = []
        for cell in self.owned:
            if cell.has_hotel == 1:
                for i in range(1, 6):
                    list_of_hotels.append((i, cell.cost_house // 2, cell))
        list_of_houses = []
        for cell in self.owned:
            if cell.has_houses > 0:
                for i in range(1, cell.has_houses + 1):
                    list_of_houses.append((i, cell.cost_house // 2, cell))

        # It will be popped from the end, so first to sell should be last
        # Selling order - first properties with only houses, then hotels
        list_of_hotels.sort(key = lambda x: (x[0], x[1]))
        list_of_houses.sort(key = lambda x: (x[0], x[1]))
        list_to_deimprove = list_of_hotels + list_of_houses
        return list_to_deimprove

    def get_list_of_properties_to_mortgage(self):
        ''' Put together a list of properties a player can sell houses from.
        '''
        list_to_mortgage = []
        for cell in self.owned:
            if not cell.is_mortgaged:
                list_to_mortgage.append((cell.cost_base * GameSettings.mortgage_value, cell))

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
                # Selling hotel: can replace with 4 houses
                if board.available_houses >= 4:
                    cell_to_deimprove.has_hotel = 0
                    cell_to_deimprove.has_houses = 4
                    board.available_hotels += 1
                    board.available_houses -= 4
                    cell_to_deimprove.can_be_improved = True
                    log.add(f"{self} sells a hotel on {cell_to_deimprove}, raising ${sell_price}")
                    self.money += sell_price
                # Selling hotel, must tear down all 5 houses from one plot
                # TODO: I think we need to tear down all 3 hotels?
                else:
                    cell_to_deimprove.has_hotel = 0
                    cell_to_deimprove.has_houses = 0
                    board.available_hotels += 1
                    cell_to_deimprove.can_be_improved = True
                    log.add(f"{self} sells a hotel and all houses on {cell_to_deimprove}, " +
                            f"raising ${sell_price * 5}")
                    self.money += sell_price * 5
                    # Recalculate the list of properties to sell, start over
                    list_to_deimprove = self.get_list_of_properties_to_deimprove()
                    continue
            else:
                cell_to_deimprove.has_houses -= 1
                board.available_houses += 1
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

            # Transfer to a player
            if isinstance(payee, Player):
                cell_to_transfer.owner = payee
                payee.owned.append(cell_to_transfer)
            # Transfer to the bank. TODO: Auction the property
            else:
                cell_to_transfer.owner = None
                cell_to_transfer.is_mortgaged = False

            board.recalculate_monopoly_coeffs(cell_to_transfer)
            log.add(f"{self} transfers {cell_to_transfer} to {payee}")

    def pay_money(self, amount, payee, board, log):
        ''' Function to pay money to another player (or bank)
        This is where Bankruptcy will be triggered.
        '''
        # Regular transaction
        if amount < self.money:
            self.money -= amount
            if payee != "bank":
                payee.money += amount
            elif payee == "bank" and GameSettings.free_parking_money:
                board.free_parking_money += amount
            return

        max_raisable_money = self.max_raisable_money()
        # Can pay but need to sell some things first
        if amount < max_raisable_money:
            log.add(f"{self} can pay ${amount}, but needs to sell some things for that")
            self.raise_money(amount, board, log)
            self.money -= amount
            if payee != "bank":
                payee.money += amount
            elif payee == "bank" and GameSettings.free_parking_money:
                board.free_parking_money += amount


        # Bunkruptcy (can't pay even after selling and mortgaging all)
        else:
            log.add(f"{self} has to pay ${amount}, max they can raise is ${max_raisable_money}")
            self.is_bankrupt = True
            log.add(f"{self} is bankrupt")

            # Raise as much cash as possible to give payee
            self.raise_money(amount, board, log)
            log.add(f"{self} gave {payee} all their remaining money (${self.money})")
            if payee != "bank":
                payee.money += self.money
            elif payee == "bank" and GameSettings.free_parking_money:
                board.free_parking_money += amount

            self.money = 0

            # Transfer all property (mortgaged at this point) to payee
            self.transfer_all_properties(payee, board, log)

            # Reset all trade settings
            self.wants_to_sell = set()
            self.wants_to_buy = set()

    def is_willing_to_buy_property(self, property_to_buy):
        ''' Check if the player is willing to buy an unowned property
        '''
        # Player has money lower than unspendable minimum
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

    def update_lists_of_properties_to_trade(self, board):
        ''' Update list of properties player is willing to sell / buy
        '''

        # If player is not willing to trade, he would
        # have not declare his offered and desired properties,
        # thus stopping any trade with them
        if not self.settings.participates_in_trades:
            return

        # Reset the lists
        self.wants_to_sell = set()
        self.wants_to_buy = set()

        # Go through each group
        for group_cells in board.groups.values():

            # Break down all properties within each color group into
            # "owned by me" / "owned by others" / "not owned"
            owned_by_me = []
            owned_by_others = []
            not_owned = []
            for cell in group_cells:
                if cell.owner == self:
                    owned_by_me.append(cell)
                elif cell.owner is None:
                    not_owned.append(cell)
                else:
                    owned_by_others.append(cell)

            # If there properties to buy - no trades
            if not_owned:
                continue
            # If I own 1: I am ready to sell it
            if len(owned_by_me) == 1:
                self.wants_to_sell.add(owned_by_me[0])
            # If someone owns 1 (and I own the rest): I want to buy it
            if len(owned_by_others) == 1:
                self.wants_to_buy.add(owned_by_others[0])

    def get_price_difference(self, gives, receives):
        ''' Calculate price difference between items player
        is about to give minus what he is about to receive.
        >0 means player gives away more
        Return both absolute (in $), relative for a giver, relative for a receiver
        '''

        cost_gives = sum(cell.cost_base for cell in gives)
        cost_receives = sum(cell.cost_base for cell in receives)

        diff_abs = cost_gives - cost_receives

        diff_giver, diff_receiver = float("inf"), float("inf")
        if receives:
            diff_giver = cost_gives / cost_receives
        if gives:
            diff_receiver = cost_receives / cost_gives

        return diff_abs, diff_giver, diff_receiver

    def fair_deal(self, player_gives, player_receives, other_player):
        ''' Remove properties from to_sell and to_buy to make it as fair as possible
        '''

        def remove_by_color(cells, color):
            new_cells = [cell for cell in cells if cell.group != color]
            return new_cells

        # First, get all colors in both sides of the deal
        color_receives = [cell.group for cell in player_receives]
        color_gives = [cell.group for cell in player_gives]

        # If there are only properties from size-2 groups, no trade
        both_colors = set(color_receives + color_gives)
        if both_colors.issubset({"Utilities", "Indigo", "Brown"}):
            return [], []

        # Look at "Indigo", "Brown", "Utilities". These have 2 properties,
        # so both players would want to receive them
        # If they are present, remove it from the guy who has longer list
        # If list has the same length, remove both questionable items

        for questionable_color in ["Utilities", "Indigo", "Brown"]:
            if questionable_color in color_receives and questionable_color in color_gives:
                if len(player_receives) > len(player_gives):
                    player_receives = remove_by_color(player_receives, questionable_color)
                elif len(player_receives) < len(player_gives):
                    player_gives = remove_by_color(player_gives, questionable_color)
                else:
                    player_receives = remove_by_color(player_receives, questionable_color)
                    player_gives = remove_by_color(player_gives, questionable_color)


        # Sort, starting from the most expensive
        player_receives.sort(key=lambda x: -x.cost_base)
        player_gives.sort(key=lambda x: -x.cost_base)


        # Check the difference in value and make sure it is not larger that player's preference
        while player_gives and player_receives:

            diff_abs, diff_giver, diff_receiver = \
                self.get_price_difference(player_gives, player_receives)

            # This player gives too much
            if diff_abs > self.settings.trade_max_diff_abs or \
               diff_giver > self.settings.trade_max_diff_rel:
                player_gives.pop()
                continue
            # Other player gives too much
            if -diff_abs > other_player.settings.trade_max_diff_abs or \
               diff_receiver > other_player.settings.trade_max_diff_rel:
                player_receives.pop()
                continue
            break

        return player_gives, player_receives

    def do_a_two_way_trade(self, players, board, log):
        ''' Look for and perform a two-way trade
        '''
        for other_player in players:
            # Selling/buying thing matches
            if self.wants_to_buy.intersection(other_player.wants_to_sell) and \
               self.wants_to_sell.intersection(other_player.wants_to_buy):
                player_receives = list(self.wants_to_buy.intersection(other_player.wants_to_sell))
                player_gives = list(self.wants_to_sell.intersection(other_player.wants_to_buy))

                # Work out a fair deal (don't trade same color,
                # get value difference within the limit)
                player_gives, player_receives = \
                    self.fair_deal(player_gives, player_receives, other_player)

                # If their deal is not empty, go on
                if player_receives and player_gives:

                    # Price difference in traded properties
                    price_difference, _, _ = \
                        self.get_price_difference(player_gives, player_receives)

                    # Player gives await more expensive item, other play has to pay
                    if price_difference > 0:
                        # Other guy can't pay
                        if other_player.money - price_difference < \
                           other_player.settings.unspendable_cash:
                            return False
                        other_player.money -= price_difference
                        self.money += price_difference

                    # Player gives cheaper stuff, has to pay
                    if price_difference < 0:
                        # This player can't pay
                        if self.money - abs(price_difference) < \
                           self.settings.unspendable_cash:
                            return False
                        other_player.money += abs(price_difference)
                        self.money -= abs(price_difference)

                    # Property changes hands
                    for cell_to_receive in player_receives:
                        cell_to_receive.owner = self
                        self.owned.append(cell_to_receive)
                        other_player.owned.remove(cell_to_receive)
                    for cell_to_give in player_gives:
                        cell_to_give.owner = other_player
                        other_player.owned.append(cell_to_give)
                        self.owned.remove(cell_to_give)

                    # Log the trade and compensation payment
                    log.add(f"Trade: {self} gives {[str(cell) for cell in player_gives]}, " +
                            f"receives {[str(cell) for cell in player_receives]} " +
                            f"from {other_player}")

                    if price_difference > 0:
                        log.add(f"{self} receive from {other_player} " +
                                f"price difference compensation {abs(price_difference)}")
                    if price_difference < 0:
                        log.add(f"{other_player} receive from {self} " +
                                f"price difference compensation {abs(price_difference)}")

                    # Recalculate monopoly and improvement status
                    board.recalculate_monopoly_coeffs(player_gives[0])
                    board.recalculate_monopoly_coeffs(player_receives[0])

                    # Recalculate who wants to buy what
                    # (for all players, it may affect their decisions too)
                    for player in players:
                        player.update_lists_of_properties_to_trade(board)

                    # Return True, to run trading function again
                    return True

        return False

    def unmortgage_a_property(self, board, log):
        ''' Go through the list of properties and unmortgage one,
        if there is enough money to do so. Return True, if any unmortgaging
        took p;lace (to call it again)
        '''

        for cell in self.owned:
            if cell.is_mortgaged:
                mooney_to_unmortgage = \
                    cell.cost_base * GameSettings.mortgage_value + \
                    cell.cost_base * GameSettings.mortgage_fee
                if self.money - mooney_to_unmortgage >= self.settings.unspendable_cash:
                    log.add(f"{self} unmortgages {cell} for ${mooney_to_unmortgage}")
                    self.money -= mooney_to_unmortgage
                    cell.is_mortgaged = False
                    board.recalculate_monopoly_coeffs(cell)
                    self.update_lists_of_properties_to_trade(board)
                    return True

        return False

    def go_to_jail(self, message, log):
        ''' Start the jail time
        '''
        log.add(f"{self} {message}, and goes to Jail.")
        self.position = 10
        self.in_jail = True
        self.had_doubles = 0
        self.days_in_jail = 0
