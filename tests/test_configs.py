"""
Configuration file for AI testing
Define test scenarios and AI configurations here
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class AIConfig:
    """Configuration for an AI strategy"""

    strategy_class_name: str
    params: Dict
    description: str


# Define various AI configurations to test
AI_CONFIGS = {
    "random": AIConfig(
        strategy_class_name="RandomAI", params={}, description="Random move selection"
    ),
    "greedy": AIConfig(
        strategy_class_name="GreedyAI",
        params={},
        description="Greedy - maximizes immediate piece flips",
    ),
    "minimax_d2": AIConfig(
        strategy_class_name="MinimaxAI",
        params={"depth": 2},
        description="Minimax depth 2 - fast but shallow",
    ),
    "minimax_d3": AIConfig(
        strategy_class_name="MinimaxAI",
        params={"depth": 3},
        description="Minimax depth 3 - balanced",
    ),
    "minimax_d4": AIConfig(
        strategy_class_name="MinimaxAI",
        params={"depth": 4},
        description="Minimax depth 4 - stronger but slower",
    ),
    "minimax_d5": AIConfig(
        strategy_class_name="MinimaxAI",
        params={"depth": 5},
        description="Minimax depth 5 - very strong but slow",
    ),
}


# Define test scenarios
TEST_SCENARIOS = [
    {
        "name": "Baseline - Random vs Random",
        "player1": "random",
        "player2": "random",
        "num_games": 20,
        "description": "Baseline performance with random play",
    },
    {
        "name": "Greedy vs Random",
        "player1": "greedy",
        "player2": "random",
        "num_games": 20,
        "description": "Test if greedy heuristic beats random",
    },
    {
        "name": "Minimax Depth Study - D2 vs D3",
        "player1": "minimax_d2",
        "player2": "minimax_d3",
        "num_games": 2,
        "description": "Compare minimax at different depths",
    },
    {
        "name": "Minimax Depth Study - D3 vs D4",
        "player1": "minimax_d3",
        "player2": "minimax_d4",
        "num_games": 2,
        "description": "Compare minimax at different depths",
    },
    {
        "name": "Minimax vs Greedy",
        "player1": "minimax_d3",
        "player2": "greedy",
        "num_games": 2,
        "description": "Test if minimax beats simple greedy",
    },
    {
        "name": "Minimax Depth Study - D4 vs D5",
        "player1": "minimax_d4",
        "player2": "minimax_d5",
        "num_games": 2,
        "description": "Compare minimax at different depths",
    },
    {
        "name": "Minimax Depth Study - D3 vs D5",
        "player1": "minimax_d3",
        "player2": "minimax_d5",
        "num_games": 2,
        "description": "Compare minimax at different depths",
    },
    {
        "name": "Minimax Depth Study - D2 vs D5",
        "player1": "minimax_d2",
        "player2": "minimax_d5",
        "num_games": 2,
        "description": "Compare minimax at different depths",
    }
]


def get_strategy_class(class_name: str):
    """Dynamically import and return strategy class"""
    if class_name == "RandomAI":
        from src.strategies.random import Random as RandomAI

        return RandomAI
    elif class_name == "GreedyAI":
        from src.strategies.greedy_ai import GreedyAI

        return GreedyAI
    elif class_name == "MinimaxAI":
        from src.strategies.minimax import MinimaxAI

        return MinimaxAI
    else:
        raise ValueError(f"Unknown strategy: {class_name}")


def run_all_scenarios():
    """Run all defined test scenarios"""
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    from .test_framework import AITester

    tester = AITester("comprehensive_test_results.db")

    print("=" * 80)
    print("RUNNING COMPREHENSIVE AI TEST SUITE")
    print("=" * 80)

    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n[{i}/{len(TEST_SCENARIOS)}] {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Games: {scenario['num_games']}")
        print("-" * 80)

        config1 = AI_CONFIGS[scenario["player1"]]
        config2 = AI_CONFIGS[scenario["player2"]]

        print(f"Player 1: {config1.description}")
        print(f"Player 2: {config2.description}")
        print()

        strategy1 = get_strategy_class(config1.strategy_class_name)
        strategy2 = get_strategy_class(config2.strategy_class_name)

        stats = tester.run_match(
            strategy1,
            config1.params,
            strategy2,
            config2.params,
            num_games=scenario["num_games"],
            series_name=scenario["name"],
        )

        print(f"\nResults: {stats['wins']}")
        print(f"Average duration: {stats['avg_duration']}s per game")
        print(f"Average moves: {stats['avg_moves']} moves per game")
        print("=" * 80)

    print("\n\nALL TESTS COMPLETE!")
    print("View results in 'comprehensive_test_results.db'")

    tester.close()


def run_custom_test(player1_key: str, player2_key: str, num_games: int = 10):
    """Run a custom test between two AI configurations"""
    import os
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    sys.path.insert(0, project_root)
    from .test_framework import AITester

    tester = AITester()

    config1 = AI_CONFIGS[player1_key]
    config2 = AI_CONFIGS[player2_key]

    strategy1 = get_strategy_class(config1.strategy_class_name)
    strategy2 = get_strategy_class(config2.strategy_class_name)

    print(f"Testing: {config1.description} vs {config2.description}")
    print(f"Running {num_games} games...\n")

    stats = tester.run_match(
        strategy1,
        config1.params,
        strategy2,
        config2.params,
        num_games=num_games,
        series_name=f"{player1_key} vs {player2_key}",
    )

    tester.close()
    return stats


def quick_test():
    """Quick test for development"""
    import os
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    from .test_framework import AITester

    tester = AITester("quick_test.db")

    from src.strategies.greedy_ai import GreedyAI
    from src.strategies.minimax import MinimaxAI

    print("Quick Test: Minimax(d=3) vs Greedy (5 games)")
    tester.run_match(
        MinimaxAI, {"depth": 3}, GreedyAI, {}, num_games=5, series_name="Quick Test"
    )

    tester.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "all":
            run_all_scenarios()
        elif command == "quick":
            quick_test()
        elif command == "custom" and len(sys.argv) == 4:
            # python test_configs.py custom minimax_d3 greedy
            player1 = sys.argv[2]
            player2 = sys.argv[3]
            run_custom_test(player1, player2, num_games=10)
        else:
            print("Usage:")
            print("  python test_configs.py all              # Run all test scenarios")
            print("  python test_configs.py quick            # Quick test")
            print("  python test_configs.py custom <p1> <p2> # Custom matchup")
            print(f"\nAvailable configs: {list(AI_CONFIGS.keys())}")
    else:
        # Default: run all scenarios
        run_all_scenarios()
