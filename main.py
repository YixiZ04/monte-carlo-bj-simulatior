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
        self.strategies = ("best_strategy", "passive_strategy")
        self.all_combination = [ (dealer_must_hit, deck_number)  for dealer_must_hit in self.dealer_must_hit for deck_number in self.deck_number ]
        self.root_dir = os.path.join(os.getcwd(), "logs", "any_dirname")
        self.all_dirs = [os.path.join(self.root_dir, f"{strategy}", f"dealer_hit_{dealer_must_hit}", f"{deck}") for strategy in self.strategies for dealer_must_hit, deck in self.all_combination]
        self.best_dirs = self.all_dirs[:12]
        self.passive_dirs = self.all_dirs[12:]


    def _make_necessary_directories(self):
        for dirname in self.all_dirs:
            os.makedirs(dirname, exist_ok=True)


    def simulate_best_strategy(self):
        self._make_necessary_directories()

        print("Simulating Best Strategy...")

        for (dealer_must_hit, deck_number), dirname in zip(self.all_combination, self.best_dirs):
            print(f"Dealer must hit: {dealer_must_hit}, deck number: {deck_number}")
            simulator = BlackJackSimulator(simulation_time=self.simulation_time,
                                           deck_number=deck_number,
                                           dealer_must_hit=dealer_must_hit,
                                           seeds=self.seeds2use,
                                           path2results=dirname)
            simulator.best_strategy_simulation()


    def simulate_passive_strategy(self):
        self._make_necessary_directories()

        print("Simulating Passive Strategy...")

        for (dealer_must_hit, deck_number), dirname in zip(self.all_combination, self.passive_dirs):
            print(f"Dealer must hit: {dealer_must_hit}, deck number: {deck_number}")
            passive_simulator = BlackJackSimulator(simulation_time=self.simulation_time,
                                                   seeds=self.seeds2use,
                                                   deck_number=deck_number,
                                                   dealer_must_hit=dealer_must_hit,
                                                   path2results=dirname)
            passive_simulator.passive_strategy_simulation()


    def simulate_all_cases(self):
        """
            Simulates all cases for the combination of:
                * Dealer Must-Hit: (16, 17, 18)
                * Deck Number: (1,4,6,8)
        """
        self.simulate_best_strategy()
        self.simulate_passive_strategy()

if __name__ == '__main__':
    main = Main()
    main.simulate_all_cases()