
from src.blackjack import BlackJackGame
from src.bj_card_utils import Deck, Hand

import os

import numpy as np
import pandas as pd

from tqdm import tqdm

from collections import Counter, defaultdict

from itertools import chain

class BlackJackSimulator:
    def __init__ (self,
                  simulation_time=200000,
                  generator_random_seed = 7,
                  seeds = 100,
                  dealer_must_hit = 17,
                  deck_number = 6,
                  player_bet_value: int = 1,
                  path2results: str = os.path.join(".", "logs"),
                  ):
        # Simulation metrics

        self.simulation_times = simulation_time

        self.rng = np.random.default_rng(generator_random_seed)
        self.random_seeds = self.rng.integers(0, 1000000, size=seeds)
        # self.random_seeds = [74,888,750,514,548,455,230,90,300,366]
        self.final_metric_list = []

        self.single_simulation_cards = []
        self.all_cards = []

        self.hand_value_per_seed = []

        # Player metrics
        self.player_bet_value = player_bet_value

        self.player_winning_times = 0
        self.split_times = 0
        self.split_hands = 0
        self.split_winning_times = 0
        self.pushes = 0
        self.doubling_times = 0
        self.doubling_winning_times = 0
        self.doubling_pushes = 0
        self.doubling_losing_time = 0
        self.player_total_bet = 0
        self.player_bj_times = 0
        self.player_bj_won_money = 0
        self.player_won_money = 0
        self.player_winning_hands = []
        self.player_losing_hands = []
        self.player_all_winning_values_count = []
        self.player_all_losing_values_count= []
        self.player_won_less_18 = 0
        self.player_won_less_22 = 0
        self.player_won_more_21 = 0
        self.player_loss_less_18 = 0
        self.player_loss_less_22 = 0
        self.player_busted = 0

        # Casino metrics
        self.deck_number = deck_number
        self.dealer_must_hit = dealer_must_hit
        self.casino_winning_times = 0
        self.casino_winning_hands = []
        self.casino_losing_hands = []
        self.casino_all_winning_values_count = []
        self.casino_all_losing_values_count = []
        self.dealer_won_less_17 = 0
        self.dealer_won_less_22 = 0
        self.dealer_won_more_21 = 0  # When player splits one hand busted and others not
        self.dealer_loss_less_17 = 0  # Player natural bj
        self.dealer_loss_less_22 = 0
        self.dealer_busted = 0

        #Export files
        self.path2results = path2results
        os.makedirs(self.path2results, exist_ok=True)

    def _reset_parameters(self):
        self.single_simulation_cards = []

        # Player metrics

        self.player_winning_times = 0
        self.split_times = 0
        self.split_hands = 0
        self.split_winning_times = 0
        self.pushes = 0
        self.doubling_times = 0
        self.doubling_winning_times = 0
        self.doubling_pushes = 0
        self.doubling_losing_time = 0
        self.player_total_bet = 0
        self.player_bj_times = 0
        self.player_bj_won_money = 0
        self.player_won_money = 0
        self.player_winning_hands = []
        self.player_losing_hands = []

        self.player_won_less_18 = 0
        self.player_won_less_22 = 0
        self.player_won_more_21 = 0
        self.player_loss_less_18 = 0
        self.player_loss_less_22 = 0
        self.player_busted = 0

        # Casino metrics

        self.casino_winning_times = 0
        self.casino_winning_hands = []
        self.casino_losing_hands = []
        self.dealer_won_less_17 = 0
        self.dealer_won_less_22 = 0
        self.dealer_won_more_21 = 0  # When player splits one hand busted and others not
        self.dealer_loss_less_17 = 0  # Player natural bj
        self.dealer_loss_less_22 = 0
        self.dealer_busted = 0


    @property
    def casino_house_edge(self):
        """
            - (player net profit / player total bet) * 100 %
        """
        return round(-self.player_won_money * 100 / self.player_total_bet, 4)


    @property
    def player_winning_values(self):
        return [hand.best_value for hand in self.player_winning_hands]


    @property
    def player_losing_values(self):
        return [hand.best_value for hand in self.player_losing_hands]


    @property
    def casino_winning_values(self):
        return [hand.best_value for hand in self.casino_winning_hands]


    @property
    def casino_losing_values(self):
        return [hand.best_value for hand in self.casino_losing_hands]


    @property
    def player_mean_winning_value(self):
        return round(np.mean(self.player_winning_values), 2)


    @property
    def player_mean_losing_value(self):
        return round(np.mean(self.player_losing_values), 2)


    @property
    def casino_mean_winning_value(self):
        return round(np.mean(self.casino_winning_values), 2)


    @property
    def casino_mean_losing_value(self):
        return round(np.mean(self.casino_losing_values), 2)


    @property
    def card_appearances(self):
        total_count_dict = defaultdict(int)

        for counter in self.all_cards:
            for suit, count in counter.items():
                total_count_dict [suit] += count

        return total_count_dict

    @property
    def player_winning_value_count(self):
        final_count = {22:0}
        hand_values = [ hand.best_value for hand in self.player_winning_hands]
        value_count = Counter(hand_values)

        for k,v in value_count.items():
            if k <= 21:
                final_count [k] = int(v)
            elif k > 21:
                final_count [22] += int(v)

        return final_count


    @property
    def player_losing_value_count(self):
        final_count = {22: 0}
        hand_values = [hand.best_value for hand in self.player_losing_hands]
        value_count = Counter(hand_values)

        for k, v in value_count.items():
            if k <= 21:
                final_count[k] = int(v)
            else:
                final_count[22] += int(v)

        return final_count

    @property
    def casino_winning_value_count(self):
        final_count = {22: 0}
        hand_values = [hand.best_value for hand in self.casino_winning_hands]
        value_count = Counter(hand_values)

        for k, v in value_count.items():
            if k <= 21:
                final_count[k] = int(v)
            else:
                final_count[22] += int(v)

        return final_count

    @property
    def casino_losing_value_count(self):
        final_count = {22: 0}
        hand_values = [hand.best_value for hand in self.casino_losing_hands]
        value_count = Counter(hand_values)

        for k, v in value_count.items():
            if k < 21:
                final_count[k] = int(v)
            else:
                final_count[22] += int(v)

        return final_count

    def hand_per_seed_df(self, rd_seed):

        seed_array = [ rd_seed for _ in range(4,23)]

        temp_df = pd.DataFrame({
            "player_winning_value_count": self.player_winning_value_count,
            "player_losing_value_count": self.player_losing_value_count,
            "casino_winning_value_count": self.casino_winning_value_count,
            "casino_losing_value_count": self.casino_losing_value_count,
        }).fillna(0).astype(np.int64)

        temp_df.index.name = "hand_value"
        temp_df.sort_index(inplace=True)
        temp_df.reset_index(inplace=True)
        temp_df["rd_seed"] = seed_array

        return temp_df


    @staticmethod
    def _decode_list_of_counters(list_of_counters):
        temp_dict = defaultdict(int)
        for counter in list_of_counters:
            for hand_value, appearances in counter.items():
                if hand_value <= 21:
                    temp_dict[hand_value] += appearances
                else:
                    temp_dict[22] += appearances

        return temp_dict


    def _record_player_metrics(self,
                               bj_game: BlackJackGame):
        self.player_winning_times += bj_game.player_won_hands
        self.pushes += bj_game.push_hands
        self.doubling_times += bj_game.doubling_time
        self.doubling_winning_times += bj_game.doubling_winning_time
        self.doubling_losing_time += bj_game.doubling_losing_time
        self.doubling_pushes += bj_game.doubling_pushes
        self.player_bj_times += bj_game.player_bj_times
        self.player_bj_won_money += bj_game.player_bj_won_money
        self.player_total_bet += bj_game.player_total_bet
        self.player_won_money += bj_game.player_won_money
        self.player_won_less_18 += bj_game.player_won_less_18
        self.player_won_less_22 += bj_game.player_won_less_22
        self.player_won_more_21 += bj_game.player_won_more_21
        self.player_loss_less_18 += bj_game.player_loss_less_18
        self.player_loss_less_22 += bj_game.player_loss_less_22
        self.player_busted += bj_game.player_busted

        if bj_game.player.first_round_split:
            self.split_times += 1
            self.split_winning_times += bj_game.split_winning_times
            self.split_hands += bj_game.split_hands
            self.player_winning_hands.extend(bj_game.player_split_winning_hands)
            self.player_losing_hands.extend(bj_game.player_split_losing_hands)
        else:
            if bj_game.player_win:
                self.player_winning_hands.append(bj_game.player)
            elif bj_game.dealer_win:
                self.player_losing_hands.append(bj_game.player)


    def _record_casino_metrics(self,
                               bj_game: BlackJackGame):
        self.casino_winning_times += bj_game.dealer_won_hands
        self.dealer_won_less_17 += bj_game.dealer_won_less_17
        self.dealer_won_less_22 += bj_game.dealer_won_less_22
        self.dealer_won_more_21 += bj_game.dealer_won_more_21
        self.dealer_loss_less_17 += bj_game.dealer_loss_less_17
        self.dealer_loss_less_22 += bj_game.dealer_loss_less_22
        self.dealer_busted += bj_game.dealer_busted

        # It has a bug here, the losing values contained pushing hands...
        if bj_game.player.first_round_split:
            if bj_game.dealer_won_hands >= 1:
                self.casino_winning_hands.append(bj_game.dealer)
            elif bj_game.split_winning_times >= 1:          # If lost once, it is considered a lost hand
                self.casino_losing_hands.append(bj_game.dealer)
            else:
                pass                                        # Pushed all hands. Not recorded
        else:
            if bj_game.dealer_win:
                self.casino_winning_hands.append(bj_game.dealer)
            elif bj_game.player_win:
                self.casino_losing_hands.append(bj_game.dealer)
            else:
                pass


    def _record_general_metrics(self,
                                bj_game: BlackJackGame):

        if not bj_game.player.first_round_split:
            self.single_simulation_cards.append(bj_game.player.cards)
        else:
            for hand in bj_game.player.split_hands:
                self.single_simulation_cards.append(hand.cards)

        self.single_simulation_cards.append(bj_game.dealer.cards)


    def _simulate_best_strategy(self,
                                bj_game: BlackJackGame):

        bj_game.player_best_strategy()
        self._record_player_metrics(bj_game)
        self._record_casino_metrics(bj_game)
        self._record_general_metrics(bj_game)


    def _simulate_passive_strategy(self,
                                   bj_game: BlackJackGame):

        bj_game.player_never_hit()
        self._record_player_metrics(bj_game)
        self._record_casino_metrics(bj_game)
        self._record_general_metrics(bj_game)


    def _record_metrics(self,  rd_seed):
        self.player_all_winning_values_count.append(self.player_winning_value_count)
        self.player_all_losing_values_count.append(self.player_losing_value_count)
        self.casino_all_winning_values_count.append(self.casino_winning_value_count)
        self.casino_all_losing_values_count.append(self.casino_losing_value_count)
        self.all_cards.append(Counter([ str(card) for cards in self.single_simulation_cards for card in cards]))
        self.hand_value_per_seed.append(self.hand_per_seed_df(rd_seed))
        self.final_metric_list.append({
            "random_seed": rd_seed,
            "simulation_times": self.simulation_times,
            "casino_edge (%)": self.casino_house_edge,
            "player_winning_times": self.player_winning_times,
            "casino_winning_times": self.casino_winning_times,
            "pushes": self.pushes,
            "player_total_bet": self.player_total_bet,
            "player_won_money": self.player_won_money,
            "player_mean_winning_value": self.player_mean_winning_value,
            "player_mean_losing_value": self.player_mean_losing_value,
            "player_winning_less_18": self.player_won_less_18,
            "player_winning_less_22": self.player_won_less_22,
            "player_winning_more_21": self.player_won_more_21,
            "player_loss_less_18": self.player_loss_less_18,
            "player_loss_less_22": self.player_loss_less_22,
            "player_bust_times":self.player_busted,
            "player_natural_bj": self.player_bj_times,
            "doubling_times": self.doubling_times,
            "doubling_winning_times": self.doubling_winning_times,
            "doubling_losing_times": self.doubling_losing_time,
            "doubling_pushes": self.doubling_pushes,
            "split_times": self.split_times,
            "split_winning_times": self.split_winning_times,
            "casino_mean_winning_value": self.casino_mean_winning_value,
            "casino_mean_losing_value": self.casino_mean_losing_value,
            "casino_winning_less_17":self.dealer_won_less_17,
            "casino_winning_less_22":self.dealer_won_less_22,
            "casino_winning_more_21":self.dealer_won_more_21,
            "casino_loss_less_17":self.dealer_loss_less_17,
            "casino_loss_less_22":self.dealer_loss_less_22,
            "casino_bust_times":self.dealer_busted,
        })


    def _export_results(self):
        pd.DataFrame(self.final_metric_list).to_csv(os.path.join(self.path2results, "metrics.tsv"),
                                                    index=False,
                                                    sep="\t")


        pd.DataFrame({"suit": list(self.card_appearances.keys()),
                      "appearances": list(self.card_appearances.values())
                      }, columns = ["suit", "appearances"]).to_csv(os.path.join(self.path2results, "total_cards_appearance.tsv"),
                                                        index=False,
                                                        sep="\t")
        # #

        cards_per_seed_df = pd.DataFrame({
            "rd_seed": [seed for seed in self.random_seeds for _ in range(52)],
            "suits": [key for counter in self.all_cards for key in list(counter.keys())],
            "appearances": [ value for counter in self.all_cards for value in list(counter.values())],
        }).set_index(["rd_seed", "suits"])


        cards_per_seed_df.to_csv(os.path.join(self.path2results, "cards_per_seed.tsv"),
                              sep="\t")


        value_per_seed_df = pd.concat(self.hand_value_per_seed).set_index(["rd_seed", "hand_value"])
        value_per_seed_df.to_csv(os.path.join(self.path2results, "value_per_seed.tsv"),
                                 sep="\t")

        value_df = pd.DataFrame({
            "player_winning_value_count": self._decode_list_of_counters(self.player_all_winning_values_count),
            "player_losing_value_count": self._decode_list_of_counters(self.player_all_losing_values_count),
            "casino_winning_value_count": self._decode_list_of_counters(self.casino_all_winning_values_count),
            "casino_losing_value_count": self._decode_list_of_counters(self.casino_all_losing_values_count),
        }).sort_index().fillna(0).astype(np.int64)

        value_df.index.name = "hand_value"

        value_df.to_csv(os.path.join(self.path2results, "total_hand_values_count.tsv"),
                            sep="\t")


    def best_strategy_simulation(self):
        """
            This would be the first option to simulate many games for calculating metrics.
        """

        for seed_number, rd_seed in enumerate(self.random_seeds):
            print(f"Simulation: {seed_number} with seed: {rd_seed}")
            self._reset_parameters()
            bj_game = BlackJackGame(rd_seed,
                                    dealer_must_hit=self.dealer_must_hit,
                                    deck_number=self.deck_number,
                                    player_bet_value=self.player_bet_value
                                    )
            for _ in tqdm(range(self.simulation_times)):
                self._simulate_best_strategy(bj_game)
            self._record_metrics(rd_seed)

        self._export_results()


    def passive_strategy_simulation(self):

        for seed_number, rd_seed in enumerate(self.random_seeds):
            print(f"Simulation: {seed_number} with seed: {rd_seed}")
            self._reset_parameters()

            bj_game = BlackJackGame(rd_seed,
                                    dealer_must_hit=self.dealer_must_hit,
                                    deck_number=self.deck_number,
                                    player_bet_value=self.player_bet_value
                                    )
            for _ in tqdm(range(self.simulation_times)):
                self._simulate_passive_strategy(bj_game)
            self._record_metrics(rd_seed)

        self._export_results()

if __name__ == "__main__":
    pass
