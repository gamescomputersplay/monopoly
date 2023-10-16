''' Player Class
'''

class Player:

    def __init__(self, name, settings):

        # Player's name and behavioral settings
        self.name = name
        self.settings = settings

        # Player's money (will be set up by the simulation)
        self.money = 0

        # Player's position
        self.position = 0

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
        self.position %= 40
        log.add(f"Player {self.name} goes to: {board.b[self.position].name}")

