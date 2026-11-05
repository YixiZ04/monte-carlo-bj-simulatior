from src.bj_card_utils import Hand, Card
from src.dealer import BlackJackDealer

class BlackJackPlayer(Hand):
    def __init__(self, bet_value: int | float ):
        super().__init__()
        # Single hand associated variables
        self.bet_value = bet_value
        self.continue_action = True
        self.double_down_bool = False
        self.take_insurance = False

        # Splitting associated variables
        self.max_split_time = 3  # Maximum 3 splits per game
        self.split_time = 0
        self.should_split = False
        self.first_round_split = False
        self.split_hands = []  # This array will store those split hands whose action has finished.
        self.continue_action_array = []
        self.bet_value_array = []
        self.double_down_array = []

    @staticmethod
    def stand() -> bool:
        """
            Associated with any continue_action boolean, such that every time this method is called, continue_action = False
        """
        return False


    @staticmethod
    def hit(playing_hand: Hand,
            deck: list) -> None:
        """
            This is static method because of the fact of splitting.
        """
        playing_hand.cards.append(deck.pop(0))


    @staticmethod
    def _create_new_hand(card: Card) -> Hand:
        """
            Given a card, this method creates a new Hand object using the given card such that Hand.cards = [card]
        """
        temp_hand = Hand()
        temp_hand.cards.append(card)
        return temp_hand


    def split(self,
              playing_hand: Hand) -> None:
        """
            Depends on if it is first time splitting or splitting after splitting:
                * If it is the first time -> Initialize self.split_hands appending 2 Hand objects created with both cards
                * If not the first time -> Updates the self.split_hand array by poping the current hand's second card,
                which is used to create a Hand object that is appended to that list.

            Either case, self.split_time adds 1.

            Note: be aware of that after splitting, no card is added to the current playing hand.
        """
        if self.split_time == 0:
            self.split_hands = [self._create_new_hand(card) for card in playing_hand.cards]
            self.continue_action_array = [True, True]
            self.bet_value_array = []

        elif self.split_time < self.max_split_time:
            self.split_hands.append(self._create_new_hand(playing_hand.cards.pop(1)))
            self.continue_action_array.append(True)

        else:
            # When split_time != 0 and >= max_split_time. No action here should be done.
            pass

        self.split_time += 1


    @staticmethod
    def double_down(bet_value: int | float) -> int | float:
        """
            Returns the doubled bet value.
        """
        return round(bet_value*2, 2)



    def _initial_stand_soft_hand (self,
                                  playing_hand: Hand,
                                  dealer: BlackJackDealer) -> bool:
        """
            This method decides if initially the hand contains Ace, the player should stand or not.
            In case of returning True, that means some more action is required: either hit or double.
        """
        if playing_hand.soft_hand_value in (20, 21):
            # If A and 9 / A and 8-> Just stand (Soft value = 20 or 19)
            return self.stand()

        if playing_hand.soft_hand_value == 19 and dealer.first_card_value != 6:
            # A + 9 vs not 6
            return self.stand()

        if playing_hand.soft_hand_value == 18 and dealer.first_card_value in (7, 8):
            # If A and 7 and dealer's up-card is 7 or 8 just stand.
            return self.stand()

        # If none of cases above, need more action: either double down or only hit.
        return True


    @staticmethod
    def _double_down_soft_hand(playing_hand: Hand,
                                  dealer: BlackJackDealer) -> bool:
        """
            This method decides if the player should double down if the hand contains Ace.
        """
        if playing_hand.soft_hand_value == 19 and dealer.first_card_value == 6:
            # A + 8 vs 6
            return True

        if playing_hand.soft_hand_value == 18 and 1 < dealer.first_card_value < 7:
            # If A + 7 and player dealer has 2/3/4/5/6, should double.
            return True

        if 13 <= playing_hand.soft_hand_value <= 17 and dealer.first_card_value in (5, 6):
            # If A + (2, 3, 4, 5, 6) and dealer has 5 or 6. Double down
            return True

        if playing_hand.soft_hand_value in (15, 16, 17) and dealer.first_card_value == 4:
            # If A + 4/5/6 and dealer has 4. Double down
            return True

        if playing_hand.soft_hand_value == 17 and dealer.first_card_value == 3:
            # If A + 6 and dealer has 3. Double down.
            return True

        # In any of the remaining cases do not double down.
        return False


    def _stand_soft_hand(self,
                         playing_hand: Hand,
                         dealer: BlackJackDealer,
                         ) -> bool:
        """
            Exclusively uses after first decision has been made.
            The returned Boolean is to decide if stands, meaning that if False then hit.
        """

        best_value = playing_hand.best_value  # To see the best value of a possible combination (>1 Aces)

        if best_value != playing_hand.hard_hand_value:

            if best_value >= 19:
                # If my value can be higher than 19, then just stand
                return self.stand() 

            if best_value == 18:
                if dealer.first_card_value not in (9, 10, 1):
                    # If soft 18 and dealer do not have 9/10/A, stand.
                    return self.stand()
                else:
                    return True

            if best_value < 18:
                # When the value is less than 18, then hit.
                return True

        else:
            # This cae is when all the Aces has to be considered having value 1.
            return self._stand_hard_hand(playing_hand, dealer)
        
        # Should never be raised
        raise RuntimeError("Unexpected values...")


    def _stand_hard_hand(self,
                         playing_hand: Hand, 
                         dealer: BlackJackDealer) -> bool:
        """
            Used both for initial case and not initial case, as the logic does not change for hands not containing Ace.
        """
        if playing_hand.hard_hand_value >= 17:
            # If the hard hand value is already >= 17, just stand.
            return self.stand()

        if playing_hand.hard_hand_value in (13, 14, 15, 16) and 1 < dealer.first_card_value <= 6:
            # If the value is 13/14/15/16 and dealer has 6 or less. Stand
            return self.stand()

        if playing_hand.hard_hand_value == 12 and dealer.first_card_value in (4,5,6):
            # If the value is 12 and dealer ahs 4/5/6. Stand
            return self.stand()

        # Any other cases needs more action (Hit/ Double)
        return True


    @staticmethod
    def _double_down_hard_hand(playing_hand: Hand,
                               dealer: BlackJackDealer) -> bool:
        """ 
            This method decides if the player should double down if the hand does not contain Ace.
        """

        if playing_hand.hard_hand_value == 11:
            # Double every time if hand value is 11
            return True

        if playing_hand.hard_hand_value == 10 and dealer.first_card_value not in (10, 1):
            # Hard hand value of 10 and dealer not having 10 or Ace
            return True

        if playing_hand.hard_hand_value == 9 and dealer.first_card_value in (3,4,5,6):
            # Hard hand value of 9 and dealer has 3/4/5/6
            return True

        return False


    @staticmethod
    def _decide_if_split(playing_hand: Hand,
                         dealer: BlackJackDealer) -> bool:
        """
            This is the split decision for the best strategy.
            Includes the logic to decide if a hand should be split.
            It is a static method because of a split hand can be again split.
        """
        if playing_hand.first_card_value != playing_hand.second_card_value:
            return False

        # Only consider splitting if the cards have the same value.
        if playing_hand.first_card_value in (1, 8):
            # Having Aces or 8s ALWAYS split
            return True

        if playing_hand.first_card_value in (2, 3, 7) and 1 < dealer.first_card_value <= 7:
            # Having 2s, 3s or 7s, if dealer has 7 or under, split.
            return True

        if playing_hand.first_card_value == 6 and 1 < dealer.first_card_value <= 6:
            # When having 6s, and dealer first card is 6 or under. SPLIT
            return True

        if playing_hand.first_card_value == 9 and dealer.first_card_value in (2, 3, 4, 5, 6, 8, 9):
            # When having 9s, and dealer's upper card is 2/3/4/5/6/8/9. SPLIT
            return True

        if playing_hand.first_card_value == 4 and dealer.first_card_value in (5,6):
            return True

        if playing_hand.first_card_value in (2,3) and dealer.first_card_value in (2,3):
            return True

        return False


    def _play_first_round(self,
                          dealer: BlackJackDealer,
                          deck: list):
        """
            Given the initial 2 cards, plays them the proper way:
                - Decide if split the first place -> If so, the rest of the action do not need to be evaluated.
                - If not split -> See if needed to hit/stand/double and this does the action.
        """

        self.first_round_split = self._decide_if_split(self, dealer)

        if self.first_round_split:
            # print("Before split:", "".join(str(card) for card in self.cards))
            # If split, no need to continue evaluating anything else
            self.split(self)

            return

        if self.has_ace():
            # Soft hand evaluation
            self.continue_action = self._initial_stand_soft_hand(self, dealer)
            self.double_down_bool = self._double_down_soft_hand(self, dealer)
        else:
            # Hard hand evaluation
            self.continue_action = self._stand_hard_hand(self, dealer)
            self.double_down_bool = self._double_down_hard_hand(self, dealer)

        if not self.continue_action:
            return

        if self.double_down_bool:
            self.bet_value = self.double_down(self.bet_value)
            self.hit(self, deck)
            self.continue_action = False
        
        else:
            self.hit(self, deck)


    def _evaluate_multiple_splitting(self,
                                     playing_hand: Hand,
                                     dealer: BlackJackDealer,
                                     deck:list):
        """
            This method is exclusively for split hand. Because when playing a split hand, it requires to split multiple times.
            For example, after splitting 8s, and keep playing, the player can receive another 8, which would cause 8s again. After
            splitting again, another 8 can be given, which requires to split again.
        """


        self.should_split = self._decide_if_split(playing_hand, dealer)

        while self.should_split and self.split_time < self.max_split_time:
            self.split(playing_hand)
            self.hit(playing_hand, deck)
            playing_hand.assign_cards()
            # print(f"Cards after resplitting: {"".join(str(card) for card in playing_hand.cards)}")
            # print(f"After split and hit: {"".join(str(card) for card in playing_hand.cards)}\n "
            #       f"Players first and second card: {str(playing_hand.first_card)}; {str(playing_hand.second_card)}\n ")
            self.should_split = self._decide_if_split(playing_hand, dealer)


    def _play_split_hand(self,
                         playing_hand: Hand,
                         dealer: BlackJackDealer,
                         deck: list,
                         ) -> tuple[bool, bool]:
        """
            This is very similar to self._play_first_round(*args), as this method is also to decide whether to stand/hit/double in the first round.
            Only differs on current method does not include logic for splitting and also this returns an additional boolean for double_down_
        """

        if playing_hand.has_ace():
            continue_action_ = self._initial_stand_soft_hand(playing_hand, dealer)
            double_down_ = self._double_down_soft_hand(playing_hand, dealer)

        else:
            continue_action_ = self._stand_hard_hand(playing_hand, dealer)
            double_down_ = self._double_down_hard_hand(playing_hand, dealer)

        if not continue_action_:
            return False, False

        if double_down_:
            self.hit(playing_hand, deck)
            return False, True

        else:
            self.hit(playing_hand, deck)
            return True, False


    def play_best_strategy(self, dealer: BlackJackDealer, deck: list):
        """
            This is the best strategy for the player, it a sequence of the previous methods.
        """

        # First round play.
        self._play_first_round(dealer, deck)

        # Case when NOT splitting. The easy case.
        if not self.first_round_split:
            # Case when not split.
            while self.continue_action and self.best_value < 21:
                if self.has_ace():
                    self.continue_action = self._stand_soft_hand(self, dealer)
                    if self.continue_action:
                        self.hit(self, deck)
                else:
                    self.continue_action = self._stand_hard_hand(self, dealer)
                    if self.continue_action:
                        self.hit(self, deck)

        # Case when splitting. The complicated case.
        if self.first_round_split:
            for hand, continue_action in zip(self.split_hands, self.continue_action_array):

                # Remember the current hand has only 1 card, needs one more. This makes sure that player goes plays one hand at a time.
                self.hit(hand, deck)
                hand.assign_cards()

                # First evaluate if needed to split again.

                self._evaluate_multiple_splitting(hand, dealer, deck)

                # "First round action"
                continue_action, double_down_ = self._play_split_hand(hand, dealer, deck)

                if double_down_:
                    self.bet_value_array.append(2*self.bet_value)
                else:
                    self.bet_value_array.append(self.bet_value)

                # After first round action, if needed more action
                while continue_action and hand.best_value < 21:
                    if hand.has_ace():
                        continue_action = self._stand_soft_hand(hand, dealer)
                        if continue_action:
                            self.hit(hand, deck)
                    else:
                        continue_action = self._stand_hard_hand(hand, dealer)
                        if continue_action:
                            self.hit(hand, deck)



if __name__ == "__main__":
    pass

