# Othello Game with AI Testing Framework

A Python implementation of Othello (Reversi) with multiple AI strategies and a comprehensive testing framework. Features a GUI for playing games and a headless testing system for comparing AI performance.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Playing the Game (GUI)](#playing-the-game-gui)
- [Testing AI Strategies](#testing-ai-strategies)
- [Analyzing Results](#analyzing-results)
- [Project Structure](#project-structure)
- [Available AI Strategies](#available-ai-strategies)
- [Advanced Usage](#advanced-usage)

---

## Installation

### Prerequisites
- Python 3.8+
- pip or uv (package manager)

### Setup

```bash
# Clone or navigate to project directory
cd /path/to/Othelo

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt
```
pygame==2.6.1
numpy==1.24.3
pytest==7.4.0
```

---

## Quick Start

### Play Against AI (GUI)
```bash
# From project root
python main.py
```

### Run Quick Test (5 games, no GUI)
```bash
# From project root
cd tests
python test_configs.py quick
```

### Run All Test Scenarios
```bash
cd tests
python test_configs.py all
```

---

## Playing the Game (GUI)

### Starting a Game

Edit `main.py` to configure players:

```python
from src.game.board import Board, Color
from src.game.player import Player
from src.strategies.human import HumanStrategy
from src.strategies.minimax_ai import MinimaxAI
from src.strategies.greedy_ai import GreedyAI
from src.presentation.gui import OthelloGUI

# Create board
board = Board()

# Human vs AI
player1 = Player(Color.BLACK, HumanStrategy(), "Human")
player2 = Player(Color.WHITE, MinimaxAI(depth=3), "AI")

# Or AI vs AI
# player1 = Player(Color.BLACK, MinimaxAI(depth=3), "AI 1")
# player2 = Player(Color.WHITE, GreedyAI(), "AI 2")

# Run GUI
gui = OthelloGUI(board, player1, player2)
gui.run()
```

### GUI Controls

- **Click** on a valid square to make a move (human players)
- **Valid Moves Button** - Toggle showing valid move indicators
- **New Game Button** - Start a new game
- **Close Window** - Exit the game

### GUI Features

- ✅ Visual board with piece animations
- ✅ Valid move indicators (green circles)
- ✅ Last move highlight (yellow ring)
- ✅ Real-time score display
- ✅ "AI thinking" indicator
- ✅ Game over screen with winner
- ✅ Supports Human vs AI and AI vs AI

---

## Testing AI Strategies

The testing framework runs games **without the GUI** and stores results in a SQLite database with full metadata (strategy configurations, heuristics, etc.).

### File Overview

| File | Purpose | Required? |
|------|---------|-----------|
| `test_framework.py` | Core testing engine, classes, pytest tests | ✅ Yes |
| `test_configs.py` | Pre-defined test scenarios, easy CLI | ⭕ Optional |
| `results_analyzer.py` | View and analyze test results | ⭕ Optional |

### Using test_framework.py Directly

```python
from test_framework import AITester
from src.strategies.minimax_ai import MinimaxAI
from src.strategies.greedy_ai import GreedyAI

# Create tester
tester = AITester("my_results.db")

# Run a match
stats = tester.run_match(
    MinimaxAI, {"depth": 3},      # Player 1
    GreedyAI, {},                  # Player 2
    num_games=10,
    series_name="Minimax vs Greedy"
)

print(stats)
tester.close()
```

### Using test_configs.py (Convenient)

Pre-defined AI configurations and test scenarios.

```bash
# Run all test scenarios (20+ games each)
python test_configs.py all

# Quick test (5 games)
python test_configs.py quick

# Custom matchup between two AIs
python test_configs.py custom minimax_d3 greedy

# See available configurations
python test_configs.py
```

### Available Test Configurations

| Config Key | Strategy | Parameters | Description |
|-----------|----------|------------|-------------|
| `random` | RandomAI | - | Random move selection |
| `greedy` | GreedyAI | - | Maximizes immediate flips |
| `minimax_d2` | MinimaxAI | depth=2 | Fast, shallow search |
| `minimax_d3` | MinimaxAI | depth=3 | Balanced performance |
| `minimax_d4` | MinimaxAI | depth=4 | Stronger, slower |
| `minimax_d5` | MinimaxAI | depth=5 | Very strong, very slow |

### Pre-defined Test Scenarios

When you run `python test_configs.py all`, it executes:

1. **Baseline - Random vs Random** (20 games)
2. **Greedy vs Random** (20 games)
3. **Minimax Depth Study - D2 vs D3** (20 games)
4. **Minimax Depth Study - D3 vs D4** (20 games)
5. **Minimax vs Greedy** (20 games)
6. **Best vs Best - D4 vs D4** (10 games)

### Using Pytest

```bash
# Run all pytest tests
pytest tests/test_framework.py -v

# Run specific test
pytest tests/test_framework.py::TestOthelloAI::test_minimax_vs_greedy -v

# Run with output
pytest tests/test_framework.py -v -s
```

### What Gets Stored in the Database

For each game, the database stores:
- **Game metadata**: timestamp, board size, winner, scores, moves, duration
- **Player configurations**: strategy name, JSON config (depth, heuristics, weights)
- **Series information**: groups of related games
- **Full traceability**: every game is linked to its exact AI configuration

Example of stored config:
```json
{
  "depth": 3,
  "corner_value": 100,
  "mobility_weight": 3.0
}
```

---

## Analyzing Results

### Interactive Analyzer

```bash
python results_analyzer.py test_results.db
```

**Menu Options:**
1. **View all series** - List all test series with IDs
2. **View series details** - Detailed results for a specific series
3. **View strategy rankings** - Overall win rates for all strategies
4. **Compare two strategies** - Head-to-head comparison
5. **Export to CSV** - Export all results for external analysis
6. **Exit**

### Example Session

```bash
$ python results_analyzer.py

Options:
  1. View all series
  2. View series details
  3. View strategy rankings
  4. Compare two strategies
  5. Export to CSV
  6. Exit

Select option: 3

================================================================================
STRATEGY RANKINGS
================================================================================

Rank   Strategy             Config                    W-L-T        Win%     Games   
--------------------------------------------------------------------------------
1      MinimaxAI            {'depth': 4}              45-15-2      75.0     60      
2      MinimaxAI            {'depth': 3}              38-20-4      63.3     60      
3      GreedyAI             {}                        25-30-5      45.5     55      
4      RandomAI             {}                        12-48-2      20.0     60      
```

### Programmatic Analysis

```python
from results_analyzer import ResultsAnalyzer

analyzer = ResultsAnalyzer("test_results.db")

# Get rankings
rankings = analyzer.get_strategy_rankings()
print(rankings)

# Compare strategies
results = analyzer.compare_strategies("MinimaxAI", "GreedyAI")
print(results)

# Export to CSV
analyzer.export_to_csv("all_results.csv")

analyzer.close()
```

---

## Project Structure

```
Othelo/
├── src/
│   ├── __init__.py
│   ├── game/
│   │   ├── __init__.py
│   │   ├── board.py          # Board state and game rules
│   │   ├── player.py         # Player class
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract Strategy interface
│   │   ├── human.py          # Human player
│   │   ├── random_ai.py      # Random AI
│   │   ├── greedy_ai.py      # Greedy AI
│   │   ├── minimax_ai.py     # Minimax with alpha-beta pruning
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── gui.py            # Pygame GUI
├── tests/
│   ├── __init__.py
│   ├── test_framework.py     # Core testing engine
│   ├── test_configs.py       # Test scenarios & configurations
│   ├── results_analyzer.py   # Results analysis tool
├── main.py                   # GUI launcher
├── requirements.txt
├── README.md
└── test_results.db          # SQLite database (created on first run)
```

---

## Available AI Strategies

### 1. RandomAI
Selects moves randomly from valid options.

```python
from src.strategies.random_ai import RandomAI
player = Player(Color.BLACK, RandomAI())
```

**Use case:** Baseline for testing

---

### 2. GreedyAI
Chooses the move that flips the most opponent pieces immediately.

```python
from src.strategies.greedy_ai import GreedyAI
player = Player(Color.BLACK, GreedyAI())
```

**Use case:** Simple but effective heuristic

---

### 3. MinimaxAI
Uses minimax algorithm with alpha-beta pruning and sophisticated evaluation.

```python
from src.strategies.minimax_ai import MinimaxAI

# Configure depth (higher = stronger but slower)
player = Player(Color.BLACK, MinimaxAI(depth=3))
```

**Features:**
- Alpha-beta pruning for efficiency
- Positional weights (corners valuable, X-squares dangerous)
- Mobility heuristic (values moves that create more options)
- Game phase awareness (early/mid/late game strategies)
- Dynamic board size support (auto-generates weights)

**Evaluation factors:**
1. **Positional score** - Corner control, edge positions
2. **Piece count** - Raw material advantage
3. **Mobility** - Number of available moves

**Performance:**
- Depth 2: ~0.1s per move
- Depth 3: ~0.5s per move (recommended)
- Depth 4: ~2-5s per move
- Depth 5: ~10-30s per move

---

## Advanced Usage

### Custom AI Configuration

Create your own AI configs in `test_configs.py`:

```python
AI_CONFIGS = {
    # ... existing configs ...
    
    "minimax_aggressive": AIConfig(
        strategy_class_name="MinimaxAI",
        params={"depth": 4},
        description="Aggressive depth-4 minimax"
    ),
}
```

Then test it:
```bash
python test_configs.py custom minimax_aggressive greedy
```

### Creating Custom Test Scenarios

Add to `TEST_SCENARIOS` in `test_configs.py`:

```python
TEST_SCENARIOS = [
    # ... existing scenarios ...
    
    {
        "name": "My Custom Test",
        "player1": "minimax_d3",
        "player2": "greedy",
        "num_games": 50,
        "description": "Testing my hypothesis"
    },
]
```

### Writing Custom Tests

```python
# my_custom_test.py
from tests.test_framework import AITester
from src.strategies.minimax_ai import MinimaxAI

tester = AITester("custom_results.db")

# Test different depth configurations
for depth in [2, 3, 4, 5]:
    print(f"\nTesting depth {depth}")
    stats = tester.run_match(
        MinimaxAI, {"depth": depth},
        MinimaxAI, {"depth": 3},
        num_games=20,
        series_name=f"Depth {depth} vs Depth 3"
    )
    print(f"Win rate: {stats['wins']}")

tester.close()
```

### Querying the Database Directly

```python
import sqlite3
import json

conn = sqlite3.connect("test_results.db")
cursor = conn.cursor()

# Find all games where MinimaxAI depth=4 won
cursor.execute("""
    SELECT g.*, p.config_json
    FROM games g
    JOIN players p ON g.id = p.game_id
    WHERE p.strategy_name = 'MinimaxAI' 
      AND g.winner = p.color
      AND json_extract(p.config_json, '$.depth') = 4
""")

results = cursor.fetchall()
print(f"Found {len(results)} wins")
conn.close()
```

### Running Tests in Parallel

```python
from multiprocessing import Pool
from tests.test_framework import AITester
from src.strategies.minimax_ai import MinimaxAI

def run_single_match(depth):
    tester = AITester(f"results_depth_{depth}.db")
    stats = tester.run_match(
        MinimaxAI, {"depth": depth},
        MinimaxAI, {"depth": 3},
        num_games=10
    )
    tester.close()
    return stats

# Run multiple depth tests in parallel
with Pool(4) as p:
    results = p.map(run_single_match, [2, 3, 4, 5])
```

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Always run from project root:
```bash
cd /path/to/Othelo
python main.py
python tests/test_configs.py
```

### Pygame Not Running

**Problem:** GUI doesn't appear or crashes

**Solution:**
```bash
# Reinstall pygame
pip uninstall pygame
pip install pygame==2.6.1

# On Linux, may need:
sudo apt-get install python3-pygame
```

### Database Locked

**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:** Close all analyzer instances and retry, or use different database files

### Test Running Slow

**Problem:** Tests take too long

**Solution:**
- Reduce `num_games` in test scenarios
- Lower minimax depth (use depth=2 or 3)
- Use `quick_test()` instead of `run_all_scenarios()`

---

## Contributing

### Adding a New AI Strategy

1. Create new file in `src/strategies/`
2. Inherit from `Strategy` base class
3. Implement `choose_move()` method
4. Add to `test_configs.py`

Example:

```python
# src/strategies/my_ai.py
from src.strategies.base import Strategy
from src.game.board import Board, Color
from typing import Optional, Tuple

class MyAI(Strategy):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        valid_moves = board.get_valid_moves(color)
        if not valid_moves:
            return None
        
        # Your AI logic here
        return valid_moves[0]
```

Then test it:

```python
# In test_configs.py
from src.strategies.my_ai import MyAI

AI_CONFIGS["my_ai"] = AIConfig(
    strategy_class_name="MyAI",
    params={"param1": 10, "param2": 20},
    description="My custom AI"
)
```

---

## License

MIT License - feel free to use and modify

---

## Credits

Built using the Strategy design pattern for clean, extensible AI implementation.

**Technologies:**
- Python 3.8+
- Pygame for GUI
- NumPy for efficient board operations
- SQLite for result storage
- Pytest for testing

---

## Support

For issues or questions:
1. Check this README
2. Review test outputs in database
3. Enable verbose pytest: `pytest -v -s`
4. Check the code - it's well-commented!