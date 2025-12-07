# Othello Game with AI Testing Framework

A Python implementation of Othello (Reversi) with multiple AI strategies and a comprehensive testing framework. Features a GUI for playing games and a headless testing system for comparing AI performance.

## Table of Contents

- [Installation](#installation)
- [Playing the Game (GUI)](#playing-the-game-gui)
- [Testing AI Strategies](#testing-ai-strategies)
- [Analyzing Results](#analyzing-results)
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

board = Board()

# Human vs AI
player1 = Player(Color.BLACK, HumanStrategy(), "Human")
player2 = Player(Color.WHITE, MinimaxAI(depth=3), "AI")

# Or AI vs AI
# player1 = Player(Color.BLACK, MinimaxAI(depth=3), "AI 1")
# player2 = Player(Color.WHITE, GreedyAI(), "AI 2")

gui = OthelloGUI(board, player1, player2)
gui.run()
```

### GUI Controls

- **Click** on a valid square to make a move (human players)
- **Valid Moves Button** - Toggle showing valid move indicators
- **New Game Button** - Start a new game
- **Close Window** - Exit the game

---

## Testing AI Strategies

The testing framework runs games **without the GUI** and stores results in a SQLite database with full metadata (strategy configurations, heuristics, etc.).

### File Overview

| File | Purpose |
|------|---------|
| `test_framework.py` | Core testing engine, classes, pytest tests |
| `test_configs.py` | Pre-defined test scenarios, easy CLI |
| `results_analyzer.py` | View and analyze test results |

### Using test_configs.py

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
| `minimax_dn` | MinimaxAI | depth=n | Minimax with depth n |

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

---

## Available AI Strategies

### 1. RandomAI

Selects moves randomly from valid options.

```python
from src.strategies.random_ai import RandomAI
player = Player(Color.BLACK, RandomAI())
```

---

### 2. GreedyAI

Chooses the move that flips the most opponent pieces immediately.

```python
from src.strategies.greedy_ai import GreedyAI
player = Player(Color.BLACK, GreedyAI())
```

---

### 3. MinimaxAI

Uses minimax algorithm with alpha-beta pruning.

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

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Always run from project root:

```bash
cd /path/to/Othelo
python main.py
python -m tests.results_analyzer
python -m tests.test_configs
```

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
