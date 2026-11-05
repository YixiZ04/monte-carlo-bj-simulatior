from src.bj_card_utils import Hand
from src.blackjack import BlackJackGame
from src.bj_simulator import BlackJackSimulator

import os

class Main:
    def __init__(self):
        self.simulation_time = 2000000
        self.seeds2use = 50
        self.dealer_must_hit = (16, 17, 18)
        self.deck_number = (1,4,6,8)
        self.passive_dealer_must_hit = 17
        self.passive_deck_number = 6
        self.strategies = ("best_strategy", "passive_strategy")
        self.all_combination = [ (dealer_must_hit, deck_number)  for dealer_must_hit in self.dealer_must_hit for deck_number in self.deck_number ]
        self.root_dir = os.path.join(os.getcwd(), "logs", "version_2_dealer_fixed")
        self.all_dirs = [os.path.join(self.root_dir, f"dealer_hit_{dealer_must_hit}", f"{deck}") for dealer_must_hit, deck in self.all_combination]
        self.path2passive_strategy = os.path.join(self.root_dir, "passive_strategy")


    def _make_necessary_directories(self):

        for dirname in self.all_dirs:
            os.makedirs(dirname, exist_ok=True)

        os.makedirs(self.path2passive_strategy, exist_ok=True)


    def simulate_passive_strategy(self):
        self._make_necessary_directories()

        passive_simulator = BlackJackSimulator(simulation_time=self.simulation_time,
                                               deck_number=self.passive_deck_number,
                                               dealer_must_hit=self.passive_dealer_must_hit,
                                               seeds=self.seeds2use,
                                               path2results=self.path2passive_strategy)
        passive_simulator.passive_strategy_simulation()


    def simulate_all_cases(self):
        """
            Simulates the best strategy for the combination of:
                * Dealer Must-Hit: (16, 17, 18)
                * Deck Number: (1,4,6,8)
            And also once passive strategy for dealer must-hit = 17 and deck number = 6 (The defined rules)
        """
        self._make_necessary_directories()
        for (dealer_must_hit, deck_number), dirname in zip(self.all_combination,self.all_dirs):
            print(f"Dealer must hit: {dealer_must_hit}, deck number: {deck_number}")
            simulator = BlackJackSimulator(simulation_time=self.simulation_time,
                                           deck_number=deck_number,
                                           dealer_must_hit=dealer_must_hit,
                                           seeds=self.seeds2use,
                                           path2results=dirname)
            simulator.best_strategy_simulation()

        passive_simulator = BlackJackSimulator(simulation_time=self.simulation_time,
                                               deck_number=self.passive_deck_number,
                                               dealer_must_hit=self.passive_dealer_must_hit,
                                               seeds=self.seeds2use,
                                               path2results=self.path2passive_strategy)
        passive_simulator.passive_strategy_simulation()


if __name__ == '__main__':
    main = Main()
    main.simulate_all_cases()