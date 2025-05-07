class Deck:
    """ Parent for Community Chest and Chance cards
    """

    def __init__(self, cards):
        # List of cards
        self.cards = cards
        # Pointer to the next card to draw
        self.pointer = 0

    def draw(self):
        """ Draw one card from the deck and put it underneath.
        Actually, we don't manipulate cards, just shuffle them once
        and then move the pointer through the deck.
        """
        drawn_card = self.cards[self.pointer]
        self.pointer += 1
        if self.pointer == len(self.cards):
            self.pointer = 0
        return drawn_card

    def remove(self, card_to_remove):
        """ Remove a card (used for GOOJF card)
        """
        self.cards.remove(card_to_remove)
        # Make sure the pointer is still okay
        if self.pointer == len(self.cards):
            self.pointer = 0

    def add(self, card_to_add):
        """ Add card (to put the removed GOOJF card back in once it's been used)
        """
        self.cards.insert(self.pointer - 1, card_to_add)
