from typing import Optional, Tuple

from src.game import Board, Color

from .base import Strategy


class HumanStrategy(Strategy):
    """Human player strategy"""

    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        valid_moves = board.get_valid_moves(color)
        if not valid_moves:
            return None

        print(f"\nValid moves: {valid_moves}")
        while True:
            try:
                move = input("Enter move (row col): ").strip()
                row, col = map(int, move.split())
                if (row, col) in valid_moves:
                    return (row, col)
                print("Invalid move. Try again.")
            except (ValueError, IndexError):
                print("Invalid input. Enter row and column numbers.")
