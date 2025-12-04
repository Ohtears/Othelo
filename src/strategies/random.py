import random
from typing import Optional, Tuple

from src.game import Board, Color

from .base import Strategy


class Random(Strategy):
    """AI that chooses random valid moves"""

    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        valid_moves = board.get_valid_moves(color)
        return random.choice(valid_moves) if valid_moves else None


