""" Player Class
"""
from monopoly.core.cell import GoToJail, LuxuryTax, IncomeTax, FreeParking, Chance, CommunityChest, Property
from monopoly.core.constants import INDIGO, BROWN, RAILROADS, UTILITIES
from monopoly.core.move_result import MoveResult
from settings import GameMechanics


class Player:
    """ Class to contain player-related into and actions:
    - money, position, owned property
    - actions to buy property of handle Chance cards etc.
    """

    def __init__(self, name, settings):

        # Player's name and behavioral settings
        self.name = name
        self.settings = settings

        # Player's money (will be set up by the simulation)
        self.money = 0

        # Player's position
        self.position = 0

        # Person's roll double and jail status
        # Is the player currently in jail
        self.in_jail = False
        # number of doubles each player thrown so far
        self.had_doubles = 0
        # number of days in jail each player spent so far
        self.days_in_jail = 0
        # is the player holding a GOOJF card(s)
        self.get_out_of_jail_chance = False
        self.get_out_of_jail_comm_chest = False

        # Owned properties
        self.owned = []

        # List of properties the player wants to sell / buy
        # through trading with other players
        self.wants_to_sell = set()
        self.wants_to_buy = set()

        # Bankrupt (game ended for this player)
        self.is_bankrupt = False

        # Placeholder for various flags used throughout the game
        self.other_notes = ""

    def __str__(self):
        return self.name

    def net_worth(self, count_mortgaged_as_full_value=False):
        """ Calculate player's net worth (cache + property + houses)
        count_mortgaged_as_full_value determines if we consider property mortgaged status:
        - True: count as full, for Income Tax calculation
        - False: count partially, for net worth statistics
        """
        net_worth = int(self.money)

        for cell in self.owned:

            if cell.is_mortgaged and not count_mortgaged_as_full_value:
                # Partially count mortgaged properties
                net_worth += int(cell.cost_base * (1 - GameMechanics.mortgage_value))
            else:
                net_worth += cell.cost_base
                net_worth += (cell.has_houses + cell.has_hotel) * cell.cost_house

        return net_worth

    def make_a_move(self, board, players, dice, log) -> MoveResult:
        """ Main function for a player to make a move
        Receives:
        - the game state: board, cells, players' state
        - other players (in case we need to make transactions with them)
        - dice (to roll)
        - log handle
        Returns:
            MoveResult: CONTINUE, BANKRUPT, END_MOVE
        """

        # If the player bankrupt - do nothing
        if self.is_bankrupt:
            return MoveResult.BANKRUPT  # check if this is needed or this will writes bankrupt twice

        log.add(f"=== {self.name} (${self.money}, " +
                f"at {board.cells[self.position].name}) goes: ===")

        # Before the throwing of the dice:
        # 1. Trade with other players. Keep trading until no trades are possible
        # 2. Unmortgage a property. Keep doing it until possible
        # 3. Improve all properties that can be improved
        while self.do_a_two_way_trade(players, board, log):
            pass
        while self.unmortgage_a_property(board, log):
            pass
        self.improve_properties(board, log)

        # The move itself:
        # Player rolls the dice
        _, dice_sum, is_double = dice.roll()

        # Get doubles for the third time: go to jail
        if is_double and self.had_doubles == 2:
            self.handle_going_to_jail("rolled 3 doubles in a row", log)
            return MoveResult.END_MOVE

        # Player is currently in jail
        if self.in_jail:
            if self.is_player_stay_in_jail(is_double, board, log):
                return MoveResult.END_MOVE

        # Player moves to a cell
        self.position += dice_sum
        # Get salary if we passed go on the way
        if self.position >= 40:
            self.handle_salary(board, log)
        # Get the correct position if we passed GO
        self.position %= 40
        log.add(f"{self.name} goes to: {board.cells[self.position].name}")

        # Handle special cells:

        # Both Chance and Community Chest are processed first, as they may send the player to a property
        # Chance is before "Community Chest" as Chance can send to Community Chest

        # Player lands on "Chance"
        if isinstance(board.cells[self.position], Chance):
            if self.handle_chance(board, players, log) == MoveResult.END_MOVE:
                return MoveResult.END_MOVE

        # Player lands on "Community Chest"
        if isinstance(board.cells[self.position], CommunityChest):
            if self.handle_community_chest(board, players, log) == MoveResult.END_MOVE:
                return MoveResult.END_MOVE

        # Player lands on a property
        if isinstance(board.cells[self.position], Property):
            self.handle_landing_on_property(board, players, dice, log)

        # Player lands on "Go To Jail"
        if isinstance(board.cells[self.position], GoToJail):
            self.handle_going_to_jail("landed on Go To Jail", log)
            return MoveResult.END_MOVE

        # Player lands on "Free Parking"
        if isinstance(board.cells[self.position], FreeParking):
            # If Free Parking Money house rule is on: get the money
            if GameMechanics.free_parking_money:
                log.add(f"{self} gets ${board.free_parking_money} from Free Parking")
                self.money += board.free_parking_money
                board.free_parking_money = 0

        # Player lands on "Luxury Tax"
        if isinstance(board.cells[self.position], LuxuryTax):
            self.pay_money(GameMechanics.luxury_tax, "bank", board, log)
            if not self.is_bankrupt:
                log.add(f"{self} pays Luxury Tax ${GameMechanics.luxury_tax}")

        # Player lands on "Income Tax"
        if isinstance(board.cells[self.position], IncomeTax):
            self.handle_income_tax(board, log)

        # Reset the other_notes flag
        self.other_notes = ""

        # If the player went bankrupt -> return string "bankrupt"
        if self.is_bankrupt:
            return MoveResult.BANKRUPT

        if is_double:
            self.had_doubles += 1
            log.add(f"{self} rolled a double ({self.had_doubles} in a row) so they go again.")
            move_result_of_double_move = self.make_a_move(board, players, dice, log)
            return move_result_of_double_move
        # not a double: Reset doubles count
        self.had_doubles = 0
        return MoveResult.END_MOVE

    def handle_salary(self, board, log):
        """ Adding Salary to the player's money, according to the game's settings """
        self.money += board.settings.mechanics.salary
        log.add(f" {self.name} receives salary ${board.settings.mechanics.salary}")

    def handle_going_to_jail(self, message, log):
        """ Start the jail time
        """
        log.add(f"{self} {message}, and goes to Jail.")
        self.position = 10
        self.in_jail = True
        self.had_doubles = 0
        self.days_in_jail = 0

    def is_player_stay_in_jail(self, dice_roll_is_double, board, log):
        """ Handle a player being in Jail
        Return True if the player stays in jail (to end his turn)
        """
        # Get out of jail on rolling double
        if self.get_out_of_jail_chance or self.get_out_of_jail_comm_chest:
            log.add(f"{self} uses a GOOJF card")
            self.in_jail = False
            self.days_in_jail = 0
            # Return the card to the deck
            if self.get_out_of_jail_chance:
                board.chance.add("Get Out of Jail Free")
                self.get_out_of_jail_chance = False
            else:
                board.chest.add("Get Out of Jail Free")
                self.get_out_of_jail_comm_chest = False

        # Get out of jail on rolling double
        elif dice_roll_is_double:
            log.add(f"{self} rolled a double, a leaves jail for free")
            self.in_jail = False
            self.days_in_jail = 0
        # Get out of jail and pay a fine
        elif self.days_in_jail == 2:  # It's your third day
            log.add(f"{self} did not rolled a double for the third time, " +
                    f"pays {GameMechanics.exit_jail_fine} and leaves jail")
            self.pay_money(GameMechanics.exit_jail_fine, "bank", board, log)
            self.in_jail = False
            self.days_in_jail = 0
        # Stay in jail for another turn
        else:
            log.add(f"{self} stays in jail")
            self.days_in_jail += 1
            return True
        return False

    def handle_chance(self, board, players, log):
        """ Draw and act on a Chance card
        Return True if the move should be over (go to jail)
        """
        card = board.chance.draw()
        log.add(f"{self} drew Chance card: '{card}'")

        # Cards that send you to a certain location on board

        if card == "Advance to Boardwalk":
            log.add(f"{self} goes to {board.cells[39]}")
            self.position = 39

        elif card == "Advance to Go (Collect $200)":
            log.add(f"{self} goes to {board.cells[0]}")
            self.position = 0
            self.handle_salary(board, log)

        elif card == "Advance to Illinois Avenue. If you pass Go, collect $200":
            log.add(f"{self} goes to {board.cells[24]}")
            if self.position > 24:
                self.handle_salary(board, log)
            self.position = 24

        elif card == "Advance to St. Charles Place. If you pass Go, collect $200":
            log.add(f"{self} goes to {board.cells[11]}")
            if self.position > 11:
                self.handle_salary(board, log)
            self.position = 11

        elif card == "Take a trip to Reading Railroad. If you pass Go, collect $200":
            log.add(f"{self} goes to {board.cells[5]}")
            if self.position > 5:
                self.handle_salary(board, log)
            self.position = 5

        # Going backwards

        elif card == "Go Back 3 Spaces":
            self.position -= 3
            log.add(f"{self} goes to {board.cells[self.position]}")

        # Sends to a type of location, and affects the rent amount

        elif card == "Advance to the nearest Railroad. " + \
                "If owned, pay owner twice the rental to which they are otherwise entitled":
            nearest_railroad = self.position
            while (nearest_railroad - 5) % 10 != 0:
                nearest_railroad += 1
                nearest_railroad %= 40
            log.add(f"{self} goes to {board.cells[nearest_railroad]}")
            if self.position > nearest_railroad:
                self.handle_salary(board, log)
            self.position = nearest_railroad
            self.other_notes = "double rent"

        elif card == "Advance token to nearest Utility. " + \
                "If owned, throw dice and pay owner a total ten times amount thrown.":
            nearest_utility = self.position
            while nearest_utility not in (12, 28):
                nearest_utility += 1
                nearest_utility %= 40
            log.add(f"{self} goes to {board.cells[nearest_utility]}")
            if self.position > nearest_utility:
                self.handle_salary(board, log)
            self.position = nearest_utility
            self.other_notes = "10 times dice"

        # Jail related (go to jail or GOOJF card)

        elif card == "Get Out of Jail Free":
            log.add(f"{self} now has a 'Get Out of Jail Free' card")
            self.get_out_of_jail_chance = True
            # Remove the card from the deck
            board.chance.remove("Get Out of Jail Free")

        elif card == "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200":
            self.handle_going_to_jail("got GTJ Chance card", log)
            return MoveResult.END_MOVE

        # Receiving money

        elif card == "Bank pays you dividend of $50":
            log.add(f"{self} gets $50")
            self.money += 50

        elif card == "Your building loan matures. Collect $150":
            log.add(f"{self} gets $150")
            self.money += 150

        # Paying money (+ depending on property + to other players)

        elif card == "Speeding fine $15":
            self.pay_money(15, "bank", board, log)

        elif card == "Make general repairs on all your property. For each house pay $25. " + \
                "For each hotel pay $100":
            repair_cost = sum(cell.has_houses * 25 + cell.has_hotel * 100 for cell in self.owned)
            log.add(f"Repair cost: ${repair_cost}")
            self.pay_money(repair_cost, "bank", board, log)

        elif card == "You have been elected Chairman of the Board. Pay each player $50":
            for other_player in players:
                if other_player != self and not other_player.is_bankrupt:
                    self.pay_money(50, other_player, board, log)
                    if not self.is_bankrupt:
                        log.add(f"{self} pays {other_player} $50")

        return ""

    def handle_community_chest(self, board, players, log):
        """ Draw and act on a Community Chest card
        Return True if the move should be over (go to jail)
        """

        card = board.chest.draw()
        log.add(f"{self} drew Community Chest card: '{card}'")

        # Moving to Go

        if card == "Advance to Go (Collect $200)":
            log.add(f"{self} goes to {board.cells[0]}")
            self.position = 0
            self.handle_salary(board, log)

        # Jail related

        elif card == "Get Out of Jail Free":
            log.add(f"{self} now has a 'Get Out of Jail Free' card")
            self.get_out_of_jail_comm_chest = True
            # Remove the card from the deck
            board.chest.remove("Get Out of Jail Free")

        elif card == "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200":
            self.handle_going_to_jail("got GTJ Community Chest card", log)
            return MoveResult.END_MOVE

        # Paying money

        elif card == "Doctor's fee. Pay $50":
            self.pay_money(50, "bank", board, log)

        elif card == "Pay hospital fees of $100":
            self.pay_money(100, "bank", board, log)

        elif card == "Pay school fees of $50":
            self.pay_money(50, "bank", board, log)

        elif card == "You are assessed for street repair. $40 per house. $115 per hotel":
            repair_cost = sum(cell.has_houses * 40 + cell.has_hotel * 115 for cell in self.owned)
            log.add(f"Repair cost: ${repair_cost}")
            self.pay_money(repair_cost, "bank", board, log)

        # Receive money

        elif card == "Bank error in your favor. Collect $200":
            log.add(f"{self} gets $200")
            self.money += 200

        elif card == "From sale of stock you get $50":
            log.add(f"{self} gets $50")
            self.money += 50

        elif card == "Holiday fund matures. Receive $100":
            log.add(f"{self} gets $100")
            self.money += 100

        elif card == "Income tax refund. Collect $20":
            log.add(f"{self} gets $20")
            self.money += 20

        elif card == "Life insurance matures. Collect $100":
            log.add(f"{self} gets $100")
            self.money += 100

        elif card == "Receive $25 consultancy fee":
            log.add(f"{self} gets $25")
            self.money += 25

        elif card == "You have won second prize in a beauty contest. Collect $10":
            log.add(f"{self} gets $10")
            self.money += 10

        elif card == "You inherit $100""You inherit $100":
            log.add(f"{self} gets $100")
            self.money += 100

        # Receiving money from other players

        elif card == "It is your birthday. Collect $10 from every player":
            for other_player in players:
                if other_player != self and not other_player.is_bankrupt:
                    other_player.pay_money(50, self, board, log)
                    if not other_player.is_bankrupt:
                        log.add(f"{other_player} pays {self} $10")

        return ""

    def handle_income_tax(self, board, log):
        """ Handle Income tax: choose which option
        (fix or %) is less money and go with it
        """
        # Choose smaller between fixed rate and percentage
        tax_to_pay = min(
            GameMechanics.income_tax,
            int(GameMechanics.income_tax_percentage *
                self.net_worth(count_mortgaged_as_full_value=True)))

        if tax_to_pay == GameMechanics.income_tax:
            log.add(f"{self} pays fixed Income tax {GameMechanics.income_tax}")
        else:
            log.add(f"{self} pays {GameMechanics.income_tax_percentage * 100:.0f}% " +
                    f"Income tax {tax_to_pay}")
        self.pay_money(tax_to_pay, "bank", board, log)

    def handle_landing_on_property(self, board, players, dice, log):
        """ Landing on property: either buy it or pay rent
        """

        def is_willing_to_buy_property(property_to_buy):
            """ Check if the player is willing to buy an unowned property
            """
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

        def buy_property(property_to_buy):
            """ Player buys the property
            """
            property_to_buy.owner = self
            self.owned.append(property_to_buy)
            self.money -= property_to_buy.cost_base

        # This is the property a player landed on
        landed_property = board.cells[self.position]

        # Property is not owned by anyone
        if landed_property.owner is None:

            # Does the player want to buy it?
            if is_willing_to_buy_property(landed_property):
                # Buy property
                buy_property(landed_property)
                log.add(f"{self.name} bought {landed_property} " +
                        f"for ${landed_property.cost_base}")

                # Recalculate all monopolies / can build flags
                board.recalculate_monopoly_multipliers(landed_property)

                # Recalculate who wants to buy what
                # (for all players, it may affect their decisions too)
                for player in players:
                    player.update_lists_of_properties_to_trade(board)

            else:
                log.add(f"{self.name} landed on a {landed_property}, he refuses to buy it")
                # TODO: Bank auctions the property

        # Property has an owner
        else:
            # It is mortgaged: no action
            if landed_property.is_mortgaged:
                log.add("Property is mortgaged, no rent")
            # It is player's own property
            elif landed_property.owner == self:
                log.add("Own property, no rent")
            # Handle rent payments
            else:
                log.add(f"{self.name} landed on a property, " +
                        f"owned by {landed_property.owner}")
                rent_amount = landed_property.calculate_rent(dice)
                if self.other_notes == "double rent":
                    rent_amount *= 2
                    log.add(f"Per Chance card, rent is doubled (${rent_amount}).")
                if self.other_notes == "10 times dice":
                    # Divide by monopoly_coef to restore the dice throw
                    # Multiply that by 10
                    rent_amount = rent_amount // landed_property.monopoly_multiplier * 10
                    log.add(f"Per Chance card, rent is 10x dice throw (${rent_amount}).")
                self.pay_money(rent_amount, landed_property.owner, board, log)
                if not self.is_bankrupt:
                    log.add(f"{self} pays {landed_property.owner} rent ${rent_amount}")

    def improve_properties(self, board, log):
        """ While there is money to spend and properties to improve,
        keep building houses/hotels
        """

        def get_next_property_to_improve():
            """ Decide what is the next property to improve:
            - it should be eligible for improvement (is monopoly, not mortgaged,
            has not more houses than other cells in the group)
            - start with cheapest
            """
            can_be_improved = []
            for cell in self.owned:
                # Property has to be:
                # - not maxed out (no hotel)
                # - not mortgaged
                # - a part of monopoly, but not railway or utility (so the monopoly_multiplier is 2)
                if (
                        cell.has_hotel == 0
                        and not cell.is_mortgaged
                        and cell.monopoly_multiplier == 2
                        and cell.group not in (RAILROADS, UTILITIES)
                ):
                    # In order for this cell to be able to be improved, it needs that all cells in the group:
                    # 1. have at least as many houses as this cell (or a hotel)
                    # 2. not be mortgaged
                    # 3. available houses/hotel in the bank
                    for other_cell in board.groups[cell.group]:
                        if (other_cell.has_houses < cell.has_houses and not other_cell.has_hotel) or other_cell.is_mortgaged:
                            break
                    else:
                        if cell.has_houses != 4 and board.available_houses > 0 or \
                                cell.has_houses == 4 and board.available_hotels > 0:
                            can_be_improved.append(cell)
            # Sort the list by the cost of house
            can_be_improved.sort(key=lambda x: x.cost_house)

            # Return first (the cheapest) property that can be improved
            if can_be_improved:
                return can_be_improved[0]
            return None

        while True:
            cell_to_improve = get_next_property_to_improve()

            # Nothing to improve anymore
            if cell_to_improve is None:
                break

            improvement_cost = cell_to_improve.cost_house

            # Don't do it if you don't have money to spend
            if self.money - improvement_cost < self.settings.unspendable_cash:
                break

            # Building a house
            ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}

            if cell_to_improve.has_houses != 4:
                cell_to_improve.has_houses += 1
                board.available_houses -= 1
                # Paying for the improvement
                self.money -= cell_to_improve.cost_house
                log.add(f"{self} built {ordinal[cell_to_improve.has_houses]} " +
                        f"house on {cell_to_improve} for ${cell_to_improve.cost_house}")

            # Building a hotel
            elif cell_to_improve.has_houses == 4:
                cell_to_improve.has_houses = 0
                cell_to_improve.has_hotel = 1
                board.available_houses += 4
                board.available_hotels -= 1
                # Paying for the improvement
                self.money -= cell_to_improve.cost_house
                log.add(f"{self} built a hotel on {cell_to_improve}")

    def unmortgage_a_property(self, board, log):
        """ Go through the list of properties and unmortgage one,
        if there is enough money to do so. Return True, if any unmortgaging
        took place (to call it again)
        """

        for cell in self.owned:
            if cell.is_mortgaged:
                cost_to_unmortgage = \
                    cell.cost_base * GameMechanics.mortgage_value + \
                    cell.cost_base * GameMechanics.mortgage_fee
                if self.money - cost_to_unmortgage >= self.settings.unspendable_cash:
                    log.add(f"{self} unmortgages {cell} for ${cost_to_unmortgage}")
                    self.money -= cost_to_unmortgage
                    cell.is_mortgaged = False
                    self.update_lists_of_properties_to_trade(board)
                    return True

        return False

    def raise_money(self, required_amount, board, log):
        """ Part of the "Pay money" method. If there is not enough cash, the player has to
        sell houses, hotels, mortgage property until you get the `required_amount` of money
        """

        def get_next_property_to_downgrade(required_amount):
            """ Get the next property to sell houses/hotel from.
            Logic goes as follows:
            - sell a house is able, otherwise sell a hotel
            - sell one that would bring you just above the required amount (or the most expensive)
            """

            # 1. let's see which properties CAN be de-improved
            # The house/hotel count is the highest in the group
            can_be_downgrade = []
            can_be_downgrade_has_houses = False
            for cell in self.owned:
                if cell.has_houses > 0 or cell.has_hotel > 0:
                    # Look at other cells in this group
                    # Do they have more houses or hotels?
                    # If so, this property cannot be de-improved
                    for other_cell in board.groups[cell.group]:
                        if cell.has_hotel == 0 and (
                                other_cell.has_houses > cell.has_houses or other_cell.has_hotel > 0):
                            break
                    else:
                        can_be_downgrade.append(cell)
                        if cell.has_houses > 0:
                            can_be_downgrade_has_houses = True

            # No further de-improvements possible
            if len(can_be_downgrade) == 0:
                return None

            # 2. If there are houses and hotels, remove hotels from the list
            # Selling a hotel is a last resort
            if can_be_downgrade_has_houses:
                can_be_downgrade = [x for x in can_be_downgrade if x.has_hotel == 0]

            # 3. Find one that's just above the required amount (or the most expensive one)
            # Sort potential de-improvements from cheap to expensive
            can_be_downgrade.sort(key=lambda x: x.cost_house // 2)
            while True:
                # Only one possible option left
                if len(can_be_downgrade) == 1:
                    return can_be_downgrade[0]
                # The second expensive option is not enough, sell most expensive
                if can_be_downgrade[-2].cost_house // 2 < required_amount:
                    return can_be_downgrade[-1]
                # Remove the most expensive option
                can_be_downgrade.pop()

        def get_list_of_properties_to_mortgage():
            """ Put together a list of properties a player can sell houses from.
            """
            list_to_mortgage = []
            for cell in self.owned:
                if not cell.is_mortgaged:
                    list_to_mortgage.append(
                        (int(cell.cost_base * GameMechanics.mortgage_value), cell))

            # It will be popped from the end, so first to sell should be last
            list_to_mortgage.sort(key=lambda x: -x[0])
            return list_to_mortgage

        # Cycle through all possible de-improvements until
        # all houses/hotels are sold or enough money is raised
        while True:
            money_to_raise = required_amount - self.money
            cell_to_deimprove = get_next_property_to_downgrade(money_to_raise)

            if cell_to_deimprove is None or money_to_raise <= 0:
                break

            sell_price = cell_to_deimprove.cost_house // 2

            # Selling a hotel
            if cell_to_deimprove.has_hotel:
                # Selling hotel: can replace with 4 houses
                if board.available_houses >= 4:
                    cell_to_deimprove.has_hotel = 0
                    cell_to_deimprove.has_houses = 4
                    board.available_hotels += 1
                    board.available_houses -= 4
                    log.add(f"{self} sells a hotel on {cell_to_deimprove}, raising ${sell_price}")
                    self.money += sell_price
                # Selling hotel, must tear down all 5 houses from one plot
                # TODO: I think we need to tear down all 3 hotels in this situation?
                else:
                    cell_to_deimprove.has_hotel = 0
                    cell_to_deimprove.has_houses = 0
                    board.available_hotels += 1
                    log.add(f"{self} sells a hotel and all houses on {cell_to_deimprove}, " +
                            f"raising ${sell_price * 5}")
                    self.money += sell_price * 5

            # Selling a house
            else:
                cell_to_deimprove.has_houses -= 1
                board.available_houses += 1
                ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
                log.add(f"{self} sells {ordinal[cell_to_deimprove.has_houses + 1]} " +
                        f"house on {cell_to_deimprove}, raising ${sell_price}")
                self.money += sell_price

        # Mortgage properties
        list_to_mortgage = get_list_of_properties_to_mortgage()

        while list_to_mortgage and self.money < required_amount:
            # Pick a property to mortgage from the list
            mortgage_price, cell_to_mortgage = list_to_mortgage.pop()

            # Mortgage this property
            cell_to_mortgage.is_mortgaged = True
            self.money += mortgage_price
            log.add(f"{self} mortgages {cell_to_mortgage}, raising ${mortgage_price}")

    def pay_money(self, amount, payee, board, log):
        """ Function to pay money to another player (or bank)
        This is where Bankruptcy is triggered.
        """

        def count_max_raisable_money():
            """ How much cash can a player produce?
            Used to determine if they should go bankrupt or not.
            Max raisable money is 1/2 of houses cost + 1/2 of unmortgaged properties cost
            """
            max_raisable = self.money
            for cell in self.owned:
                if cell.has_houses > 0:
                    max_raisable += cell.cost_house * cell.has_houses // 2
                if cell.has_hotel > 0:
                    max_raisable += cell.cost_house * 5 // 2
                if not cell.is_mortgaged:
                    max_raisable += int(cell.cost_base * GameMechanics.mortgage_value)
            return max_raisable

        def transfer_all_properties(payee, board, log):
            """ Part of bankruptcy procedure, transfer all mortgaged property to the creditor
            """

            while self.owned:
                cell_to_transfer = self.owned.pop()

                # Transfer to a player
                # TODO: Unmortgage the property right away, or pay more
                if isinstance(payee, Player):
                    cell_to_transfer.owner = payee
                    payee.owned.append(cell_to_transfer)
                # Transfer to the bank
                # TODO: Auction the property
                else:
                    cell_to_transfer.owner = None
                    cell_to_transfer.is_mortgaged = False

                board.recalculate_monopoly_multipliers(cell_to_transfer)
                log.add(f"{self} transfers {cell_to_transfer} to {payee}")

        # Regular transaction
        if amount < self.money:
            self.money -= amount
            if payee != "bank":
                payee.money += amount
            elif payee == "bank" and GameMechanics.free_parking_money:
                board.free_parking_money += amount
            return

        max_raisable_money = count_max_raisable_money()
        # Can pay but need to sell some things first
        if amount < max_raisable_money:
            log.add(f"{self} has ${self.money}, he can pay ${amount}, " +
                    "but needs to mortgage/sell some things for that")
            self.raise_money(amount, board, log)
            self.money -= amount
            if payee != "bank":
                payee.money += amount
            elif payee == "bank" and GameMechanics.free_parking_money:
                board.free_parking_money += amount

        # Bankruptcy (can't pay even after selling and mortgaging all)
        else:
            log.add(f"{self} has to pay ${amount}, max they can raise is ${max_raisable_money}")
            self.is_bankrupt = True
            log.add(f"{self} is bankrupt")

            # Raise as much cash as possible to give payee
            self.raise_money(amount, board, log)
            log.add(f"{self} gave {payee} all their remaining money (${self.money})")
            if payee != "bank":
                payee.money += self.money
            elif payee == "bank" and GameMechanics.free_parking_money:
                board.free_parking_money += amount

            self.money = 0

            # Transfer all property (mortgaged at this point) to payee
            transfer_all_properties(payee, board, log)

            # Reset all trade settings
            self.wants_to_sell = set()
            self.wants_to_buy = set()

    def update_lists_of_properties_to_trade(self, board):
        """ Update list of properties player is willing to sell / buy
        """

        # If player is not willing to trade, he would
        # have not declared his offered and desired properties,
        # thus stopping any trade with them
        if not self.settings.is_willing_to_make_trades:
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

            # If there are properties to buy - no trades
            if not_owned:
                continue
            # If I own 1: I am ready to sell it
            if len(owned_by_me) == 1:
                self.wants_to_sell.add(owned_by_me[0])
            # If someone owns 1 (and I own the rest): I want to buy it
            if len(owned_by_others) == 1:
                self.wants_to_buy.add(owned_by_others[0])

    def do_a_two_way_trade(self, players, board, log):
        """ Look for and perform a two-way trade
        """

        def get_price_difference(gives, receives):
            """ Calculate price difference between items player
            is about to give minus what he is about to receive.
            >0 means a player gives away more
            Return both absolute (in $), relative for a giver, relative for a receiver
            """

            cost_gives = sum(cell.cost_base for cell in gives)
            cost_receives = sum(cell.cost_base for cell in receives)

            diff_abs = cost_gives - cost_receives

            diff_giver, diff_receiver = float("inf"), float("inf")
            if receives:
                diff_giver = cost_gives / cost_receives
            if gives:
                diff_receiver = cost_receives / cost_gives

            return diff_abs, diff_giver, diff_receiver

        def remove_by_color(cells, color):
            new_cells = [cell for cell in cells if cell.group != color]
            return new_cells

        def fair_deal(player_gives, player_receives, other_player):
            """ Remove properties from to_sell and to_buy to make it as fair as possible
            """

            # First, get all colors in both sides of the deal
            color_receives = [cell.group for cell in player_receives]
            color_gives = [cell.group for cell in player_gives]

            # If there are only properties from size-2 groups, no trade
            both_colors = set(color_receives + color_gives)
            if both_colors.issubset({UTILITIES, INDIGO, BROWN}):
                return [], []

            # Look at "Indigo", "Brown", "Utilities". These have 2 properties,
            # so both players would want to receive them
            # If they are present, remove it from the guy who has the longer list
            # If a list has the same length, remove both questionable items

            for questionable_color in [UTILITIES, INDIGO, BROWN]:
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
                    get_price_difference(player_gives, player_receives)

                # This player gives too much
                if diff_abs > self.settings.trade_max_diff_absolute or \
                        diff_giver > self.settings.trade_max_diff_relative:
                    player_gives.pop()
                    continue
                # The Other player gives too much
                if -diff_abs > other_player.settings.trade_max_diff_absolute or \
                        diff_receiver > other_player.settings.trade_max_diff_relative:
                    player_receives.pop()
                    continue
                break

            return player_gives, player_receives

        for other_player in players:
            # Selling/buying thing matches
            if self.wants_to_buy.intersection(other_player.wants_to_sell) and \
                    self.wants_to_sell.intersection(other_player.wants_to_buy):
                player_receives = list(self.wants_to_buy.intersection(other_player.wants_to_sell))
                player_gives = list(self.wants_to_sell.intersection(other_player.wants_to_buy))

                # Work out a fair deal (don't trade the same color,
                # get value difference within the limit)
                player_gives, player_receives = \
                    fair_deal(player_gives, player_receives, other_player)

                # If their deal is not empty, go on
                if player_receives and player_gives:

                    # Price difference in traded properties
                    price_difference, _, _ = \
                        get_price_difference(player_gives, player_receives)

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
                        log.add(f"{self} received " +
                                f"price difference compensation ${abs(price_difference)} " +
                                f"from {other_player}")
                    if price_difference < 0:
                        log.add(f"{other_player} received " +
                                f"price difference compensation ${abs(price_difference)} " +
                                f"from {self}")

                    # Recalculate monopoly and improvement status
                    board.recalculate_monopoly_multipliers(player_gives[0])
                    board.recalculate_monopoly_multipliers(player_receives[0])

                    # Recalculate who wants to buy what
                    # (for all players, it may affect their decisions too)
                    for player in players:
                        player.update_lists_of_properties_to_trade(board)

                    # Return True to run a trading function again
                    return True

        return False
