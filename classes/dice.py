''' Class for Dice (thread safe seed based, with adjutable number of dice and sides)
'''

import random

class Dice:
    ''' Class to have dice settings, in case we want to play with that
    '''

    def __init__(self, seed, dice_count, dice_sides):
        self.dice_count = dice_count
        self.dice_sides = dice_sides

        self.local_random = random.Random()
        self.local_random.seed(seed)

    def cast(self):
        ''' Cast dice and return: return raw cast, the score, is it a double
        '''

        cast = [self.local_random.randint(1, self.dice_sides) for _ in range(self.dice_count)]

        # Cast, total score, all dice are equal
        return cast, sum(cast), len(set(cast)) == 1
