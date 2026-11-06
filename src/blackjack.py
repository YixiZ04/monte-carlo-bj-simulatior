"""
    Rules:
        - Decks can vary according the number to simulate.
        - All shuffled together.
        - Cut card -> Leaves a small part of the Deck not to be used (Assume 15-20%).
        - Dealer deals cards till the cut card:
            * Player gets its first card.
            * Dealer gets its first card -> FACE UP.
            * Player gets its second card.
            * Dealer gets its second card -> FACE DOWN
        - Once reached the cut card, all the 6 decks are re-shuffled.
        - The dealer MUST STAND on a fix value given as an argument.
        - The shuffling is done once and played to the cut-card (Not continuous shuffling).
        - BlackJack pays 3:2
        - Double after splitting (DAS) is allowed.
        - Split Aces is allowed.
        - Player can double any 2 cards.
        - Card counting not allowed (well, not simulated at least...).
"""
###################################################################################################################################
# Import modules
###################################################################################################################################

from src.bj_card_utils import Deck, Hand
from src.dealer import BlackJackDealer
from src.player import BlackJackPlayer

import numpy as np

from copy import deepcopy


# BlackJackGame

class BlackJackGame:
    def __init__ (self,
                  random_seed: int = 7,
                  dealer_must_hit: int = 17,
                  player_bet_value: int | float = 1,
                  deck_number: int = 6) :
        """
            Initialized with a random seed and the player's bet value, which by default is 1.
        """

        # Player associated parameters

        self.player_bet_value = player_bet_value
        self.player = BlackJackPlayer(bet_value = self.player_bet_value)
        self.player_considered_value = 0
        self.player_win = False
        self.player_won_money = 0
        self.player_won_hands = 0
        self.split_winning_times = 0
        self.split_hands = 0
        self.push_hands = 0
        self.doubling_time = 0
        self.doubling_winning_time = 0
        self.doubling_pushes = 0
        self.doubling_losing_time = 0
        self.player_bj_times = 0
        self.player_bj_won_money = 0
        self.player_won_less_18 = 0
        self.player_won_less_22 = 0
        self.player_won_more_21 = 0
        self.player_loss_less_18 = 0
        self.player_loss_less_22 = 0
        self.player_busted = 0
        self.player_split_winning_hands = []
        self.player_split_losing_hands = []

        # Dealer's associated parameters

        self.dealer = BlackJackDealer()
        self.dealer_must_hit = dealer_must_hit
        self.dealer_considered_value = 0
        self.dealer_win = False
        self.dealer_won_hands = 0
        self.dealer_won_less_17 = 0
        self.dealer_won_less_22 = 0
        self.dealer_won_more_21 = 0  # When player splits one hand busted and others not
        self.dealer_loss_less_17 = 0  # Player natural bj
        self.dealer_loss_less_22 = 0
        self.dealer_busted = 0

        # Game's associated parameters

        self.continue_game = True
        self.need_compare_value = False

        self.shuffled_deck = Deck.english_deck() * deck_number
        self.deck_copy = Deck.english_deck() * deck_number

        self.random_seed = random_seed

        self.rng = np.random.default_rng (self.random_seed)
        self.rng.shuffle(self.shuffled_deck)
        self.rng.shuffle(self.shuffled_deck)

        self.deck_number = deck_number
        self.cut_card = np.floor(self.rng.uniform(0.15, 0.20) * len(self.shuffled_deck)) if self.deck_number > 1 else 20

        self.has_bug = False


    def _reset_all_values(self) -> None:
        """
            Resets all values to their initial values.
        """

        # Player's associated parameters

        self.player = BlackJackPlayer(bet_value=self.player_bet_value)
        self.player_won_money = 0
        self.player_won_hands = 0
        self.push_hands = 0
        self.split_hands = 0
        self.split_winning_times = 0
        self.doubling_winning_time = 0
        self.doubling_losing_time = 0
        self.doubling_pushes = 0
        self.doubling_time = 0
        self.player_bj_times = 0
        self.player_bj_won_money = 0
        self.player_won_less_18 = 0
        self.player_won_less_22 = 0
        self.player_won_more_21 = 0
        self.player_loss_less_18 = 0
        self.player_loss_less_22 = 0
        self.player_busted = 0
        self.player_split_winning_hands = []
        self.player_split_losing_hands = []

        # Dealer's associated values
        self.dealer = BlackJackDealer()
        self.dealer_won_hands = 0
        self.dealer_won_less_17 = 0
        self.dealer_won_less_22 = 0
        self.dealer_won_more_21 = 0         # When player splits one hand busted and others not
        self.dealer_loss_less_17 = 0       # Player natural bj
        self.dealer_loss_less_22 = 0
        self.dealer_busted = 0

        # Game associated parameters
        self.pushes_less_17 = 0
        self.pushes_less_22 = 0
        self.pushes_more_21 = 0             #Should always be 0

        self.continue_game = True
        self.need_compare_value = False
        self.player_win = False
        self.dealer_win = False

        self.has_bug = False

    @property
    def player_total_bet(self):
        total_bet = 0
        if self.player.first_round_split:
            for bet_value in self.player.bet_value_array:
                total_bet += bet_value
        else:
            total_bet = self.player.bet_value

        return total_bet


    def _check_reshuffle_deck(self) -> None:
        """
            Reshuffles the deck once reached to the cut card.
            Each time reshuffled, the cut card should have a new value.
        """

        if len(self.shuffled_deck) < self.cut_card:
            self.cut_card = np.floor(self.rng.uniform(0.15, 0.20) * len(self.deck_copy)) if self.deck_number > 1 else 20  # New value
            self.dealer.reshuffle(self.deck_copy,
                                  self.rng)
            self.shuffled_deck = deepcopy(self.deck_copy)

    def _start_game (self) -> None:
        """
            Starts the game by checking if needed to reshuffle and resetting all parameters.
            After that, the first round is dealt.
        """

        self._check_reshuffle_deck()

        self._reset_all_values()

        self.dealer.deal_first_round(self.player,
                                     self.shuffled_deck)

    def _first_round_status_check (self) -> None:
        """
            Checks if the player has BJ and check cases for the dealer:
                * If player has BJ and dealer first card < 10 -> Pays 3:2 directly
                * If player has BJ and dealer first card == 10 or Ace -> Need check for the face-down card.

            As this simulation is done assuming that player never takes insurance, its logic is not coded.
        """

        # self.player_considered_value = self.player.best_value
        # self.player_dealer_considered_value = self.dealer.best_value

        if self.player.has_bj() and not self.dealer.has_bj():
            self.continue_game = False
            self.player_win = True
            self.dealer_win = False
            self.player_won_money += 0.5*self.player_bet_value
            self.player_bj_times += 1
            self.player_bj_won_money += 1.5*self.player_total_bet

        if self.player.has_bj() and self.dealer.has_bj():
            self.continue_game = False
            self.player_bj_times += 1
            # None of the player nor dealer wins. Both win set as False

        if not self.player.has_bj() and self.dealer.has_bj():
            self.continue_game = False
            self.player_win = False
            self.dealer_win = True


    def _dealer_action(self) -> None:
        """
            If dealer needs to action, he must hit till soft 17.
        """
        while True:
            self.dealer_considered_value = self.dealer.best_value

            if self.dealer_considered_value < self.dealer_must_hit:
               self.dealer.hit(self.shuffled_deck)

            elif self.dealer_considered_value > 21:
                self.need_compare_value = False
                self.continue_game = False
                self.player_win = True
                self.dealer_win = False
                break

            elif self.dealer_must_hit <= self.dealer_considered_value <= 21:
                self.continue_game = False
                self.need_compare_value = True
                break

    def _compare_values(self,
                        player_hand: Hand) -> None:

        self.player_considered_value = player_hand.best_value
        self.dealer_considered_value = self.dealer.best_value

        player_value = self.player_considered_value
        dealer_value = self.dealer_considered_value

        if player_value > 21:
            # A player bust loses, even if the dealer also busts.
            self.player_win = False
            self.dealer_win = True

        elif dealer_value > 21:
            self.player_win = True
            self.dealer_win = False

        elif player_value > dealer_value:
            self.player_win = True
            self.dealer_win = False

        elif player_value < dealer_value:
            self.player_win = False
            self.dealer_win = True

        else:
            # Equal totals are a push.
            self.player_win = False
            self.dealer_win = False

    def _check_winner(self,
                      player_bet_value) -> None:
        """
            Does what its name indicates.
        """
        if self.dealer_win:
            self.player_won_money -= player_bet_value

        elif self.player_win:
            self.player_won_money += player_bet_value

        elif not self.dealer_win and not self.player_win:
            pass


    def _record_player_winning_values(self, 
                               playing_hand:Hand) -> None:
        """
            If player won having >= 22, there is a bug on somewhere. 
        """
        
        if playing_hand.best_value <= 18:
            self.player_won_less_18 += 1
            
        elif playing_hand.best_value < 22:
            self.player_won_less_22 += 1
            
        else:
            self.player_won_more_21 += 1
            
            
    def _record_player_losing_values(self, 
                                     playing_hand:Hand) -> None:

        if playing_hand.best_value <= 18:
            self.player_loss_less_18 += 1
            
        elif playing_hand.best_value < 22:
            self.player_loss_less_22 += 1
            
        else:
            self.player_busted += 1
            
    def _record_dealer_winning_values (self) -> None:
        if self.dealer.best_value < 17:
            self.dealer_won_less_17 += 1
            
        elif self.dealer.best_value < 22:
            self.dealer_won_less_22 += 1
        
        else:
            self.dealer_won_more_21 += 1
            
    
    def _record_dealer_losing_values (self) -> None:
        if self.dealer.best_value < 17:
            self.dealer_loss_less_17 += 1
            
        elif self.dealer.best_value < 22:
            self.dealer_loss_less_22 += 1
            
        else:
            self.dealer_busted += 1
    
    def _record_pushes_values(self):
        """Only uses dealer values because it by definition is the same as player's value."""
        if self.dealer.best_value < 17:
            self.pushes_less_17 += 1

        elif self.dealer.best_value < 22:
            self.pushes_less_22 += 1

        else:
            self.pushes_more_21 += 1


    def _record_doubling_metrics(self, bet_value_: int | float) -> None:
        
        if bet_value_ > self.player_bet_value:
            self.doubling_time += 1
            if self.player_win:
                self.doubling_winning_time += 1

            elif self.dealer_win:
                self.doubling_losing_time += 1

            else:
                self.doubling_pushes += 1
        
    def _check_winning_status(self):
        """
            Not only this denotes the winning for split/not split cases, but it also helps to update records of split/double times.
        """
        if self.player.first_round_split:
            for hand, bet_value_ in zip(self.player.split_hands, self.player.bet_value_array):
                self._compare_values(hand)
                self._check_winner(bet_value_)
                
                if self.player_win:
                    self.split_winning_times += 1
                    self.player_won_hands += 1
                    self._record_player_winning_values(hand)
                    self._record_dealer_losing_values()
                    self.player_split_winning_hands.append(hand)

                elif self.dealer_win:
                    if hand.best_value == 21:
                        self.has_bug = True
                    self.dealer_won_hands += 1
                    self._record_player_losing_values(hand)
                    self._record_dealer_winning_values()
                    self.player_split_losing_hands.append(hand)

                elif not self.dealer_win and not self.player_win:
                    self.push_hands += 1
                    self._record_pushes_values()
                        
            self.split_hands += len(self.player.split_hands)

        else:
            self._compare_values(self.player)
            self._check_winner(self.player.bet_value)

            if self.player_win:
                self.player_won_hands += 1
                self._record_player_winning_values(self.player)
                self._record_dealer_losing_values()

            elif self.dealer_win:
                if self.player.best_value == 21:
                    self.has_bug = True
                self.dealer_won_hands += 1
                self._record_dealer_winning_values()
                self._record_player_losing_values(self.player)

            elif not self.dealer_win and not self.player_win:
                self.push_hands += 1
                self._record_pushes_values()

            self._record_doubling_metrics(self.player.bet_value)


    def _check_passive_winning_status(self):
        self._compare_values(self.player)
        self._check_winner(self.player.bet_value)

        if self.player_win:
            self.player_won_hands += 1
            self._record_player_winning_values(self.player)
            self._record_dealer_losing_values()

        elif self.dealer_win:
            if self.player.best_value == 21:
                self.has_bug = True
            self.dealer_won_hands += 1
            self._record_dealer_winning_values()
            self._record_player_losing_values(self.player)

        elif not self.dealer_win and not self.player_win:
            self.push_hands += 1
            self._record_pushes_values()

        self._record_doubling_metrics(self.player.bet_value)


    def player_never_hit(self):
        """
            This is the main method where the player takes no action at all -> No splitting, NO doubling-down nor hit.
            This would be the most passive strategy ever, either waits for:
                1. Dealer to bust
                2. Player to have an incredible hand in the first round
            This can be the ground case, any "good" strategy must at least beat this one's casino's edge.
        """
        self._start_game()
        self._first_round_status_check()

        while self.continue_game:
            # Note that player does no action.
            self._dealer_action()

        self._check_passive_winning_status()

    def player_best_strategy(self):
        """
            This is for player's best strategy. As it involves splitting, the evaluation of both cases (split / not split) should be different.
        """
        self._start_game()
        self._first_round_status_check()

        if self.continue_game:
            self.player.play_best_strategy(self.dealer,
                                           self.shuffled_deck)

            # This is important: dealer only needs to action if player has not busted
            if not self.player.first_round_split:
                if self.player.best_value > 21:
                    self.continue_game = False
                    self.dealer_win = True
                else:
                    self._dealer_action()

            # This is the case when player has split, and at least one of the hands is less than 21. If all busted, no action of dealer should be done.
            if self.player.first_round_split and any(hand.best_value <= 21 for hand in self.player.split_hands):
                self._dealer_action()

        self._check_winning_status()

        if self.dealer.best_value == 21 and self.player_win:
            raise RuntimeError("BUUUUUUUUUUUUUG")


if __name__ == "__main__":
    pass