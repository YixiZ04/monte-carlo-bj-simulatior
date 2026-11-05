from src.bj_card_utils import Hand
import numpy as np

class BlackJackDealer(Hand):
    """
        Dealer. Do not need additional parameters than those initialized in Hand
    """

    @staticmethod
    def _add_card(hand: Hand,
                  deck:list) -> None:

        hand.cards.append(deck.pop(0))


    def hit(self,
            deck: list) -> None:

        self._add_card(self, deck)


    def deal_first_round(self,
                         player: Hand,
                         deck: list ) -> None:
        """
            First round:
                1. Player gets the first card, then dealer gets his face-up card.
                2. Player gets his second card, then dealer gets his face-down card.
        """
        for _ in range(2):
            self._add_card(player, deck)
            self._add_card(self, deck)
        player.assign_cards()
        self.assign_cards()


    @staticmethod
    def reshuffle(deck_copy: list,
                  rng: np.random.Generator) -> None:
        """
            Used np.random.Generator initialized in BlackJackGame to reshuffle the deck, this makes sure that the same random seed is used everywhere.
        """
        rng.shuffle(deck_copy)



