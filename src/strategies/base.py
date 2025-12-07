from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.game.board import Board, Color


class Strategy(ABC):
    """Abstract strategy interface for AI players"""

    @abstractmethod
    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        """Choose a move given the current board state"""
        pass
