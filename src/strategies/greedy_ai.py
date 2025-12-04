from typing import Optional, Tuple

from src.game import Board, Color

from .base import Strategy


class GreedyAI(Strategy):
    """AI that chooses the move that flips the most pieces"""

    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        valid_moves = board.get_valid_moves(color)
        if not valid_moves:
            return None

        best_move = None
        best_score = -1

        for move in valid_moves:
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], color)
            score = self._evaluate(temp_board, color)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _evaluate(self, board: Board, color: Color) -> int:
        """Simple evaluation: count pieces"""
        black, white = board.get_score()
        return black if color == Color.BLACK else white
