""" Class for Dice, a thread-safe seed-based random generator,
that can:
- cast dice (with adjustable number of dice and sides)
- shuffle a deck (community chest and chance)
"""

import random


def is_dice_are_double(cast):
    return len(set(cast)) == 1


class Dice:
    """ Class to have dice settings, in case we want to play with that
    """
    
    def __init__(self, seed, dice_count, dice_sides, log):
        self.dice_count = dice_count
        self.dice_sides = dice_sides
        
        # Create a local random generator that can be thread-safe
        self.local_random = random.Random()
        self.local_random.seed(seed)
        
        self.log = log
    
    def cast(self):
        """ Cast dice and return: return raw cast, the score, is it a double
        """
        
        cast = [self.local_random.randint(1, self.dice_sides) for _ in range(self.dice_count)]
        self.log.add(f"roll: {sum(cast)}, ({cast}{',double' if is_dice_are_double(cast) else ''})")
        
        # if values are the same (double in case of 2 dice)
        return cast, sum(cast), is_dice_are_double(cast)

    def shuffle(self, object_to_shuffle):
        """ Copy of random.shuffle, but with local
        random generator (to be thread safe)
        """
        self.local_random.shuffle(object_to_shuffle)
