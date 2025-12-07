import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pytest


@dataclass
class GameMetadata:
    """Metadata for a game configuration"""

    player1_strategy: str
    player1_config: Dict
    player2_strategy: str
    player2_config: Dict
    board_size: int
    timestamp: str

    def to_dict(self):
        return asdict(self)


@dataclass
class GameResult:
    """Result of a single game"""

    winner: str  # "BLACK", "WHITE", or "TIE"
    black_score: int
    white_score: int
    total_moves: int
    duration_seconds: float

    def to_dict(self):
        return asdict(self)


class GameEngine:
    """Headless game engine for testing (no GUI)"""

    def __init__(self, board, player1, player2):
        self.board = board
        self.players = [player1, player2]
        self.current_player_idx = 0
        self.move_count = 0

    def play_game(self) -> Tuple[GameResult, List[Tuple[int, int]]]:
        """Play a complete game and return results"""
        import time

        start_time = time.time()

        consecutive_passes = 0
        move_history = []

        while consecutive_passes < 2:
            current_player = self.players[self.current_player_idx]

            # Get valid moves
            valid_moves = self.board.get_valid_moves(current_player.color)

            if not valid_moves:
                consecutive_passes += 1
                self.current_player_idx = 1 - self.current_player_idx
                continue

            # Make move
            move = current_player.make_move(self.board)

            if move is None:
                consecutive_passes += 1
            else:
                self.board.make_move(move[0], move[1], current_player.color)
                move_history.append(move)
                self.move_count += 1
                consecutive_passes = 0

            self.current_player_idx = 1 - self.current_player_idx

        duration = time.time() - start_time

        # Get final scores
        black_score, white_score = self.board.get_score()

        if black_score > white_score:
            winner = "BLACK"
        elif white_score > black_score:
            winner = "WHITE"
        else:
            winner = "TIE"

        result = GameResult(
            winner=winner,
            black_score=black_score,
            white_score=white_score,
            total_moves=self.move_count,
            duration_seconds=round(duration, 2),
        )

        return result, move_history


class ResultsDatabase:
    """SQLite database for storing test results"""

    def __init__(self, db_path: str = "test_results.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()

        # Games table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                board_size INTEGER NOT NULL,
                winner TEXT NOT NULL,
                black_score INTEGER NOT NULL,
                white_score INTEGER NOT NULL,
                total_moves INTEGER NOT NULL,
                duration_seconds REAL NOT NULL
            )
        """)

        # Players table (stores strategy configurations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                color TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                config_json TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        """)

        # Match series table (for running multiple games)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_series_games (
                series_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                FOREIGN KEY (series_id) REFERENCES match_series(id),
                FOREIGN KEY (game_id) REFERENCES games(id),
                PRIMARY KEY (series_id, game_id)
            )
        """)

        self.conn.commit()

    def save_game(
        self,
        metadata: GameMetadata,
        result: GameResult,
        series_id: Optional[int] = None,
    ) -> int:
        """Save a game result to the database"""
        cursor = self.conn.cursor()

        # Insert game
        cursor.execute(
            """
            INSERT INTO games (timestamp, board_size, winner, black_score, 
                             white_score, total_moves, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metadata.timestamp,
                metadata.board_size,
                result.winner,
                result.black_score,
                result.white_score,
                result.total_moves,
                result.duration_seconds,
            ),
        )

        game_id = cursor.lastrowid

        # Insert player configurations
        cursor.execute(
            """
            INSERT INTO players (game_id, color, strategy_name, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (
                game_id,
                "BLACK",
                metadata.player1_strategy,
                json.dumps(metadata.player1_config),
            ),
        )

        cursor.execute(
            """
            INSERT INTO players (game_id, color, strategy_name, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (
                game_id,
                "WHITE",
                metadata.player2_strategy,
                json.dumps(metadata.player2_config),
            ),
        )

        # Link to series if provided
        if series_id:
            cursor.execute(
                """
                INSERT INTO match_series_games (series_id, game_id)
                VALUES (?, ?)
            """,
                (series_id, game_id),
            )

        self.conn.commit()
        return game_id  # type: ignore

    def create_series(self, name: str, description: str = "") -> int:
        """Create a new match series"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO match_series (name, description, timestamp)
            VALUES (?, ?, ?)
        """,
            (name, description, datetime.now().isoformat()),
        )

        self.conn.commit()
        return cursor.lastrowid  # type: ignore

    def get_series_stats(self, series_id: int) -> Dict:
        """Get statistics for a match series"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT g.winner, COUNT(*) as wins
            FROM games g
            JOIN match_series_games msg ON g.id = msg.game_id
            WHERE msg.series_id = ?
            GROUP BY g.winner
        """,
            (series_id,),
        )

        wins = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT 
                AVG(g.duration_seconds) as avg_duration,
                AVG(g.total_moves) as avg_moves,
                COUNT(*) as total_games
            FROM games g
            JOIN match_series_games msg ON g.id = msg.game_id
            WHERE msg.series_id = ?
        """,
            (series_id,),
        )

        stats = cursor.fetchone()

        return {
            "wins": wins,
            "avg_duration": round(stats[0], 2) if stats[0] else 0,
            "avg_moves": round(stats[1], 2) if stats[1] else 0,
            "total_games": stats[2],
        }

    def get_strategy_performance(self, strategy_name: str) -> Dict:
        """Get overall performance statistics for a strategy"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT 
                p.color,
                g.winner,
                COUNT(*) as games
            FROM players p
            JOIN games g ON p.game_id = g.id
            WHERE p.strategy_name = ?
            GROUP BY p.color, g.winner
        """,
            (strategy_name,),
        )

        results = cursor.fetchall()

        stats = {
            "as_black": {"wins": 0, "losses": 0, "ties": 0},
            "as_white": {"wins": 0, "losses": 0, "ties": 0},
        }

        for color, winner, count in results:
            if winner == color:
                stats[f"as_{color.lower()}"]["wins"] = count
            elif winner == "TIE":
                stats[f"as_{color.lower()}"]["ties"] = count
            else:
                stats[f"as_{color.lower()}"]["losses"] = count

        return stats

    def close(self):
        """Close database connection"""
        self.conn.close()


class AITester:
    """Helper class for running AI tests"""

    def __init__(self, db_path: str = "test_results.db"):
        self.db = ResultsDatabase(db_path)

    def run_match(
        self,
        player1_class,
        player1_config: Dict,
        player2_class,
        player2_config: Dict,
        num_games: int = 10,
        board_size: int = 8,
        series_name: Optional[str] = None,
    ) -> Dict:
        """
        Run multiple games between two AI configurations

        Args:
            player1_class: Strategy class for player 1
            player1_config: Configuration dict for player 1
            player2_class: Strategy class for player 2
            player2_config: Configuration dict for player 2
            num_games: Number of games to play
            board_size: Size of the board
            series_name: Optional name for this match series
        """
        from src.game.board import Board, Color
        from src.game.player import Player

        series_id = None
        if series_name:
            description = f"{player1_class.__name__}{player1_config} vs {player2_class.__name__}{player2_config}"
            series_id = self.db.create_series(series_name, description)

        results = []

        for i in range(num_games):
            # Alternate who plays black/white
            if i % 2 == 0:
                p1_color, p2_color = Color.BLACK, Color.WHITE
            else:
                p1_color, p2_color = Color.WHITE, Color.BLACK

            # Create board and players
            board = Board(board_size)
            player1 = Player(p1_color, player1_class(**player1_config))
            player2 = Player(p2_color, player2_class(**player2_config))

            # Play game
            engine = GameEngine(board, player1, player2)
            result, move_history = engine.play_game()

            # Create metadata
            metadata = GameMetadata(
                player1_strategy=player1_class.__name__,
                player1_config=player1_config,
                player2_strategy=player2_class.__name__,
                player2_config=player2_config,
                board_size=board_size,
                timestamp=datetime.now().isoformat(),
            )

            # Save to database
            game_id = self.db.save_game(metadata, result, series_id)
            results.append((game_id, result))

            print(
                f"Game {i + 1}/{num_games}: {result.winner} wins "
                f"({result.black_score}-{result.white_score}) "
                f"in {result.total_moves} moves"
            )

        # Get series stats if this was a series
        if series_id:
            stats = self.db.get_series_stats(series_id)
            print("\nSeries Results:")
            print(f"  Total Games: {stats['total_games']}")
            print(f"  Wins: {stats['wins']}")
            print(f"  Avg Duration: {stats['avg_duration']}s")
            print(f"  Avg Moves: {stats['avg_moves']}")
            return stats

        return {"results": results}

    def close(self):
        """Close database connection"""
        self.db.close()


# ============================================================================
# PYTEST TEST CASES
# ============================================================================


class TestOthelloAI:
    """Pytest test cases for AI strategies"""

    @pytest.fixture
    def board(self):
        """Create a fresh board for each test"""
        from src.game.board import Board

        return Board()

    @pytest.fixture
    def tester(self):
        """Create AI tester"""
        tester = AITester("test_results.db")
        yield tester
        tester.close()

    def test_random_vs_random(self, tester):
        """Test Random AI vs Random AI"""
        from src.strategies.random import Random as RandomAI

        stats = tester.run_match(
            RandomAI,
            {},
            RandomAI,
            {},
            num_games=10,
            series_name="Random vs Random Test",
        )

        assert stats["total_games"] == 10

    def test_greedy_vs_random(self, tester):
        """Test Greedy AI vs Random AI - Greedy should win more"""
        from src.strategies.greedy_ai import GreedyAI
        from src.strategies.random import Random as RandomAI

        stats = tester.run_match(
            GreedyAI,
            {},
            RandomAI,
            {},
            num_games=10,
            series_name="Greedy vs Random Test",
        )

        # Greedy should win more than it loses
        greedy_wins = stats["wins"].get("BLACK", 0) + stats["wins"].get("WHITE", 0)
        assert greedy_wins >= 7, "Greedy AI should win at least 70% of games vs Random"

    def test_minimax_depths(self, tester):
        """Compare Minimax performance at different depths"""
        from src.strategies.minimax import MinimaxAI

        # Depth 2 vs Depth 4
        stats = tester.run_match(
            MinimaxAI,
            {"depth": 2},
            MinimaxAI,
            {"depth": 4},
            num_games=2,
            series_name="Minimax Depth Comparison",
        )

        print(f"\nDepth comparison results: {stats}")
        assert stats["total_games"] == 2

    def test_minimax_vs_greedy(self, tester):
        """Test Minimax vs Greedy - Minimax should win"""
        from src.strategies.greedy_ai import GreedyAI
        from src.strategies.minimax import MinimaxAI

        stats = tester.run_match(
            MinimaxAI,
            {"depth": 3},
            GreedyAI,
            {},
            num_games=2,
            series_name="Minimax vs Greedy Test",
        )

        # Minimax should win most games
        minimax_wins = stats["wins"].get("BLACK", 0) + stats["wins"].get("WHITE", 0)
        assert minimax_wins >= 2, "Minimax should win against Greedy"

    def test_board_validity(self, board):
        """Test basic board operations"""
        from src.game.board import Color

        # Check initial state
        black_score, white_score = board.get_score()
        assert black_score == 2
        assert white_score == 2

        # Check valid moves exist
        valid_moves = board.get_valid_moves(Color.BLACK)
        assert len(valid_moves) == 4  # Standard opening has 4 valid moves

    def test_game_completion(self, board):
        """Test that a game can be played to completion"""
        from src.game.board import Color
        from src.game.player import Player
        from src.strategies.random import Random as RandomAI

        player1 = Player(Color.BLACK, RandomAI())
        player2 = Player(Color.WHITE, RandomAI())

        engine = GameEngine(board, player1, player2)
        result, moves = engine.play_game()

        # Game should complete
        assert result.winner in ["BLACK", "WHITE", "TIE"]
        assert result.total_moves > 0
        assert result.black_score + result.white_score <= 64
