"""
"""
from dataclasses import dataclass

_VALUES = {
    "2" : 2,
    "3" : 3,
    "4" : 4,
    "5" : 5,
    "6" : 6,
    "7" : 7,
    "8" : 8,
    "9" : 9,
    "10" : 10,
    "J" : 10,
    "Q" : 10,
    "K" : 10,
    "A" : 1
}
_NUMBERS = list(_VALUES.keys())
_SUITS = ["♦", "♣", "♥" ,"♠"]


@dataclass
class Card:
    number: str
    suit: str
    value_: int

    def __str__(self):
        return f"{self.number}{self.suit} "


@dataclass
class Deck:
    cards: list[Card]

    @classmethod
    def english_deck(cls):
        cards = [
            Card(number_, suit_, _VALUES[number_])
                 for number_ in _NUMBERS for suit_ in _SUITS
        ]

        return list(cards)

    @classmethod
    def all_six_deck(cls):
        cards = [
            Card("6", suit_, 6) for suit_ in _SUITS
        ]

        return list(cards)

    @classmethod
    def all_eight_deck(cls):
        cards = [
            Card("8", suit_, 8) for suit_ in _SUITS
        ]
        return list(cards)


class Hand:
    """
        Specifically used for the initial dealing.
    """
    def __init__(self):
        self.cards = []
        self.first_card = None
        self.second_card = None
        self.soft_hand_value = 0
        self.hard_hand_value = 0
        self.first_card_value = 0
        self.second_card_value = 0


    def assign_cards(self):
        self.first_card = self.cards[0]
        self.second_card = self.cards[1]
        self.first_card_value = self.first_card.value_
        self.second_card_value = self.second_card.value_
        self._calculate_hand_value()


    @staticmethod
    def is_ace(card: Card):
        return True if card.value_ == 1 else False

    def has_ace(self):
        if any(card.value_ == 1 for card in self.cards):
            return True
        else:
            return False

    def has_bj(self):
        """
            FIRST ROUND ONLY
        """

        return True if self.soft_hand_value == 21 else False

    def _calculate_hand_value(self):
        """
            Used for calculating the hard and soft value of the hand
        """
        self.soft_hand_value, self.hard_hand_value = 0, 0
        ace_count = 0
        for card in self.cards:
            if ace_count == 0 and self.is_ace(card):
                self.hard_hand_value += 1
                self.soft_hand_value += 11
                ace_count += 1
            else:
                self.hard_hand_value += card.value_
                self.soft_hand_value += card.value_


    @property
    def best_value(self):
        """
            This decides which value is going to be considered:
                * If no aces -> Hard value.
                * If with aces, here we can consider 3 possible cases:
                    1. (Probably most common one) Soft hand value > 21, but considering hard value <= 21
                    2. Both > 21 -> Returns hard hand value.
                    3. Both < 21 -> Just use the soft hand value because it is the higher one.
        """
        self._calculate_hand_value()

        # NO aces in the hand, thus either value can be used
        if self.soft_hand_value == self.hard_hand_value:
            return self.hard_hand_value

        # With Aces in hand, but soft hand busted and hard hand NOT busted.
        if self.soft_hand_value > 21:
            return self.hard_hand_value

        # With Aces in hand, but both soft and hard busted.
        if self.hard_hand_value > 21:
            return self.hard_hand_value

        # With aces in hand, and both values less or equal to 21 -> Just return the highest value (SOFT hand)
        if self.soft_hand_value <= 21:
            return self.soft_hand_value

        raise RuntimeError("Unexpected values!")


if __name__ == "__main__":
    pass