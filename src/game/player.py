from typing import Optional, Tuple

from src.strategies import Strategy

from .board import Board, Color


class Player:
    """Player that uses a strategy to make moves"""

    def __init__(self, color: Color, strategy: Strategy, name: str = ""):
        self.color = color
        self.strategy = strategy
        self.name = name or f"{color.name} ({strategy.__class__.__name__})"

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        return self.strategy.choose_move(board, self.color)
