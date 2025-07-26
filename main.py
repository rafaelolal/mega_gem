from collections import Counter
from math import comb
from typing import Optional


class MegaGem:
    def __init__(self) -> None:
        self.card_count = 6
        self.max_value_chart = 5
        self.card_colors = "GBMPY"
        self.hidden_cards = {
            color: self.card_count for color in self.card_colors
        }
        self.in_display = {color: 0 for color in self.card_colors}
        self.in_collections = {color: 0 for color in self.card_colors}
        self.charts = {
            "A": [0, 4, 8, 12, 16, 20],
            "B": [20, 16, 12, 8, 4, 0],
            "C": [0, 2, 5, 9, 14, 20],
            "D": [20, 18, 15, 11, 6, 0],
            "E": [0, 4, 10, 18, 6, 0],
        }
        self.cards_per_player = [-1, -1, 5, 4, 3]
        self.ratio_in_hand: Optional[float] = None
        self.chart: Optional[str] = None

    def get_input(self) -> None:
        self.chart = input("Value chart: ").upper()
        players = int(input("Number of players: "))

        assert players in range(3, 6)

        total_hand = players * self.cards_per_player[players]
        self.ratio_in_hand = total_hand / (
            self.card_count * len(self.card_colors)
        )
        self.in_display.update(Counter(list(input("Your hand: ").upper())))

        # Remove/discount the cards from my hand
        for color, count in self.in_display.items():
            self.hidden_cards[color] -= count

    def get_expected_value(self, gem: str) -> list[tuple[int, float]]:
        assert self.ratio_in_hand is not None
        assert self.chart is not None
        # help: https://www.gigacalculator.com/calculators/binomial-probability-calculator.php
        # Calculate P(see < X < card_count)
        probs_to_display: list[float] = []
        for x in range(
            self.in_display[gem] + 1,
            self.in_display[gem] + self.hidden_cards[gem] + 1,
        ):
            probs_to_display.append(
                self.binomial_pmf(x, self.card_count, self.ratio_in_hand)
            )

        # Calculate expected value of cards to see
        # to_display_weighted_average = 0
        # for i, p in enumerate(probs_to_display):
        #     to_display_weighted_average += (seen_cards + 1 + i) * p
        # expected_see = self.in_display[gem] + to_display_weighted_average

        # Calculate expected value
        # expected_floor = int(expected_see)
        # expected_ceil = min(expected_floor + 1, self.max_value_chart)
        # floor_value = self.charts[self.chart][expected_floor]
        # ceil_value = self.charts[self.chart][expected_ceil]
        # factor = expected_see - expected_floor
        # expected_value = floor_value + factor * (ceil_value - floor_value)

        # return the price and probability of seeing tha value
        return [
            (
                self.charts[self.chart][
                    min(self.in_display[gem] + i + 1, self.max_value_chart)
                ],
                probs_to_display[i],
            )
            for i in range(len(probs_to_display))
        ]

    def add_to_display(self, gem: str, count: int = 1) -> None:
        self.in_display[gem] += count
        self.hidden_cards[gem] -= count

    def add_to_collection(self, gem: str, count: int = 1) -> None:
        self.in_collections[gem] += count
        self.hidden_cards[gem] -= count

    def remove_from_display(self, gem: str, count: int = 1) -> None:
        self.in_display[gem] -= count
        self.hidden_cards[gem] += count

    def remove_from_collection(self, gem: str, count: int = 1) -> None:
        self.in_collections[gem] -= count
        self.hidden_cards[gem] += count

    @staticmethod
    def binomial_pmf(k: int, n: int, p: float) -> float:
        combination = comb(n, k)  # n choose k
        return combination * (p**k) * ((1 - p) ** (n - k))


def main() -> None:
    mega = MegaGem()

    print(
        "Commands: `D<gems>` add to display, `C<gems>` for collection, `U` undo"
    )
    print(f"Value charts: {', '.join(mega.charts.keys())}")
    print(f"Gems: {', '.join(mega.card_colors)}")

    mega.get_input()
    prev_value = {color: 0.0 for color in mega.card_colors}
    command_history: list[tuple[str, str]] = []
    while True:
        action = input(">> ").upper()
        command, gems = action[0], action[1:]
        if command == "D":
            for gem in gems:
                mega.add_to_display(gem)
            command_history.append((command, gems))
        elif command == "C":
            for gem in gems:
                mega.add_to_collection(gem)
            command_history.append((command, gems))
        elif command == "U":
            prev_command, gems = command_history.pop()
            if prev_command == "D":
                for gem in gems:
                    mega.remove_from_display(gem)
            elif prev_command == "C":
                for gem in gems:
                    mega.remove_from_collection(gem)

        # Print expected values
        # expected_values = {
        #     color: mega.get_expected_value(color) for color in mega.card_colors
        # }
        # max_value = max(t[0] for t in expected_values.values())
        # min_value = min(t[0] for t in expected_values.values())

        for color in mega.card_colors:
            assert mega.chart is not None

            current_value = mega.charts[mega.chart][mega.in_display[color]]
            # value_change = ""
            # if color in prev_value:
            # if current_value > prev_value[color]:
            # value_change = "+"
            # elif current_value < prev_value[color]:
            # value_change = "-"

            # Update previous value
            # prev_value[color] = current_value

            # Color coding for highest and lowest values
            # if current_value == max_value:
            #     color_code = "\033[92m"  # green
            #     end_code = "\033[0m"
            # elif current_value == min_value:
            #     color_code = "\033[91m"  # red
            #     end_code = "\033[0m"
            # else:
            #     color_code = ""
            #     end_code = ""

            # print(
            #     f"{color_code}{color}: {value_change}{current_value:.2f} {mean:.2f}%{end_code}\tD: {mega.in_display[color]} C: {mega.in_collections[color]} H: {mega.hidden_cards[color]}"
            # )
            #
            expected_values = mega.get_expected_value(color)
            prob_to_stay = (1 - sum(e[1] for e in expected_values)) * 100
            out = f"{color}: {current_value} [{prob_to_stay:.2f}%]\t"
            out += "\t".join(
                f"{value} ({prob * 100:.2f}%)"
                for value, prob in expected_values
            )
            print(out)


if __name__ == "__main__":
    main()
