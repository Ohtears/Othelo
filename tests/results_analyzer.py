"""
Analyze and visualize test results from the database
"""

import json
import sqlite3
from collections import defaultdict
from typing import Dict, List


class ResultsAnalyzer:
    """Analyze stored test results"""

    def __init__(self, db_path: str = "test_results.db"):
        self.conn = sqlite3.connect(db_path)

    def get_all_series(self) -> List[Dict]:
        """Get all match series"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, timestamp
            FROM match_series
            ORDER BY timestamp DESC
        """)

        series = []
        for row in cursor.fetchall():
            series.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "timestamp": row[3],
                }
            )

        return series

    def get_series_details(self, series_id: int) -> Dict:
        """Get detailed results for a series"""
        cursor = self.conn.cursor()

        # Get series info
        cursor.execute(
            """
            SELECT name, description, timestamp
            FROM match_series
            WHERE id = ?
        """,
            (series_id,),
        )

        series_info = cursor.fetchone()

        # Get all games in series
        cursor.execute(
            """
            SELECT g.*, 
                   p1.strategy_name as p1_strategy, p1.config_json as p1_config,
                   p2.strategy_name as p2_strategy, p2.config_json as p2_config
            FROM games g
            JOIN match_series_games msg ON g.id = msg.game_id
            JOIN players p1 ON g.id = p1.game_id AND p1.color = 'BLACK'
            JOIN players p2 ON g.id = p2.game_id AND p2.color = 'WHITE'
            WHERE msg.series_id = ?
        """,
            (series_id,),
        )

        games = []
        for row in cursor.fetchall():
            games.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "winner": row[3],
                    "black_score": row[4],
                    "white_score": row[5],
                    "total_moves": row[6],
                    "duration": row[7],
                    "black_strategy": row[8],
                    "black_config": json.loads(row[9]),
                    "white_strategy": row[10],
                    "white_config": json.loads(row[11]),
                }
            )

        return {
            "name": series_info[0],
            "description": series_info[1],
            "timestamp": series_info[2],
            "games": games,
        }

    def compare_strategies(self, strategy1: str, strategy2: str) -> Dict:
        """Compare two strategies head-to-head across all games"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT g.winner, g.black_score, g.white_score, 
                   p1.strategy_name, p2.strategy_name,
                   p1.color as p1_color
            FROM games g
            JOIN players p1 ON g.id = p1.game_id
            JOIN players p2 ON g.id = p2.game_id AND p1.color != p2.color
            WHERE (p1.strategy_name = ? AND p2.strategy_name = ?)
               OR (p1.strategy_name = ? AND p2.strategy_name = ?)
        """,
            (strategy1, strategy2, strategy2, strategy1),
        )

        results = {
            strategy1: {"wins": 0, "losses": 0, "ties": 0},
            strategy2: {"wins": 0, "losses": 0, "ties": 0},
        }

        for row in cursor.fetchall():
            winner = row[0]
            p1_strat = row[3]
            p1_color = row[5]

            if winner == "TIE":
                results[strategy1]["ties"] += 1
                results[strategy2]["ties"] += 1
            elif winner == p1_color:
                results[p1_strat]["wins"] += 1
                other = strategy2 if p1_strat == strategy1 else strategy1
                results[other]["losses"] += 1
            else:
                results[p1_strat]["losses"] += 1
                other = strategy2 if p1_strat == strategy1 else strategy1
                results[other]["wins"] += 1

        return results

    def get_strategy_rankings(self) -> List[Dict]:
        """Get win rate rankings for all strategies"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT p.strategy_name, p.config_json,
                   COUNT(*) as total_games,
                   SUM(CASE WHEN g.winner = p.color THEN 1 ELSE 0 END) as wins,
                   SUM(CASE WHEN g.winner = 'TIE' THEN 1 ELSE 0 END) as ties,
                   AVG(g.duration_seconds) as avg_duration
            FROM players p
            JOIN games g ON p.game_id = g.id
            GROUP BY p.strategy_name, p.config_json
            ORDER BY wins DESC
        """)

        rankings = []
        for row in cursor.fetchall():
            total = row[2]
            wins = row[3]
            ties = row[4]
            win_rate = (wins / total * 100) if total > 0 else 0

            rankings.append(
                {
                    "strategy": row[0],
                    "config": json.loads(row[1]),
                    "total_games": total,
                    "wins": wins,
                    "ties": ties,
                    "losses": total - wins - ties,
                    "win_rate": round(win_rate, 1),
                    "avg_duration": round(row[5], 2),
                }
            )

        return sorted(rankings, key=lambda x: x["win_rate"], reverse=True)

    def print_series_summary(self, series_id: int):
        """Print a formatted summary of a series"""
        details = self.get_series_details(series_id)

        print(f"\n{'=' * 80}")
        print(f"Series: {details['name']}")
        print(f"Description: {details['description']}")
        print(f"Timestamp: {details['timestamp']}")
        print(f"{'=' * 80}\n")

        # Count wins
        wins = defaultdict(int)
        for game in details["games"]:
            wins[game["winner"]] += 1

        print(f"Total Games: {len(details['games'])}")
        print("Results:")
        for player, count in wins.items():
            print(
                f"  {player}: {count} wins ({count / len(details['games']) * 100:.1f}%)"
            )

        # Calculate averages
        avg_moves = sum(g["total_moves"] for g in details["games"]) / len(
            details["games"]
        )
        avg_duration = sum(g["duration"] for g in details["games"]) / len(
            details["games"]
        )

        print("\nAverages:")
        print(f"  Moves per game: {avg_moves:.1f}")
        print(f"  Duration per game: {avg_duration:.2f}s")

        print(f"\n{'=' * 80}\n")

    def print_rankings(self):
        """Print strategy rankings"""
        rankings = self.get_strategy_rankings()

        print(f"\n{'=' * 80}")
        print("STRATEGY RANKINGS")
        print(f"{'=' * 80}\n")

        print(
            f"{'Rank':<6} {'Strategy':<20} {'Config':<25} {'W-L-T':<12} {'Win%':<8} {'Games':<8}"
        )
        print("-" * 80)

        for i, rank in enumerate(rankings, 1):
            config_str = str(rank["config"])[:23]
            wlt = f"{rank['wins']}-{rank['losses']}-{rank['ties']}"
            print(
                f"{i:<6} {rank['strategy']:<20} {config_str:<25} "
                f"{wlt:<12} {rank['win_rate']:<8.1f} {rank['total_games']:<8}"
            )

        print(f"\n{'=' * 80}\n")

    def export_to_csv(self, output_file: str = "results.csv"):
        """Export all results to CSV"""
        import csv

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT g.id, g.timestamp, g.board_size, g.winner,
                   g.black_score, g.white_score, g.total_moves, g.duration_seconds,
                   p1.strategy_name as black_strategy, p1.config_json as black_config,
                   p2.strategy_name as white_strategy, p2.config_json as white_config
            FROM games g
            JOIN players p1 ON g.id = p1.game_id AND p1.color = 'BLACK'
            JOIN players p2 ON g.id = p2.game_id AND p2.color = 'WHITE'
        """)

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "game_id",
                    "timestamp",
                    "board_size",
                    "winner",
                    "black_score",
                    "white_score",
                    "total_moves",
                    "duration",
                    "black_strategy",
                    "black_config",
                    "white_strategy",
                    "white_config",
                ]
            )
            writer.writerows(cursor.fetchall())

        print(f"Exported results to {output_file}")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Interactive results viewer"""
    import sys

    db_path = "test_results.db" if len(sys.argv) <= 1 else sys.argv[1]

    analyzer = ResultsAnalyzer(db_path)

    print(f"\n{'=' * 80}")
    print("OTHELLO TEST RESULTS ANALYZER")
    print(f"Database: {db_path}")
    print(f"{'=' * 80}")

    while True:
        print("\nOptions:")
        print("  1. View all series")
        print("  2. View series details")
        print("  3. View strategy rankings")
        print("  4. Compare two strategies")
        print("  5. Export to CSV")
        print("  6. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            series = analyzer.get_all_series()
            if not series:
                print("\nNo series found in database.")
            else:
                print(f"\n{'ID':<6} {'Name':<40} {'Timestamp':<25}")
                print("-" * 80)
                for s in series:
                    print(f"{s['id']:<6} {s['name']:<40} {s['timestamp']:<25}")

        elif choice == "2":
            series_id = int(input("Enter series ID: "))
            analyzer.print_series_summary(series_id)

        elif choice == "3":
            analyzer.print_rankings()

        elif choice == "4":
            strategy1 = input("Enter first strategy name: ")
            strategy2 = input("Enter second strategy name: ")
            results = analyzer.compare_strategies(strategy1, strategy2)
            print(f"\n{strategy1} vs {strategy2}:")
            print(f"  {strategy1}: {results[strategy1]}")
            print(f"  {strategy2}: {results[strategy2]}")

        elif choice == "5":
            filename = input("Enter output filename (default: results.csv): ").strip()
            if not filename:
                filename = "results.csv"
            analyzer.export_to_csv(filename)

        elif choice == "6":
            break

        else:
            print("Invalid option")

    analyzer.close()


if __name__ == "__main__":
    main()
