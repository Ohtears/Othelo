from enum import Enum
from typing import List, Tuple
import numpy as np


class Color(Enum):
    """Player colors"""

    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self):
        return Color.WHITE if self == Color.BLACK else Color.BLACK


class Board:
    """Othello board state and game rules"""

    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self, size: int = 8):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self._initialize_board()

    def _initialize_board(self):
        """Set up initial position"""
        mid = self.size // 2
        self.board[mid - 1][mid - 1] = Color.WHITE.value
        self.board[mid][mid] = Color.WHITE.value
        self.board[mid - 1][mid] = Color.BLACK.value
        self.board[mid][mid - 1] = Color.BLACK.value

    def get_valid_moves(self, color: Color) -> List[Tuple[int, int]]:
        """Get all valid moves for a player"""
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(row, col, color):
                    valid_moves.append((row, col))
        return valid_moves

    def is_valid_move(self, row: int, col: int, color: Color) -> bool:
        """Check if a move is valid"""
        if self.board[row][col] != Color.EMPTY.value:
            return False

        for dr, dc in self.DIRECTIONS:
            if self._would_flip(row, col, dr, dc, color):
                return True
        return False

    def _would_flip(self, row: int, col: int, dr: int, dc: int, color: Color) -> bool:
        """Check if placing a piece would flip opponent pieces"""
        r, c = row + dr, col + dc
        found_opponent = False

        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == Color.EMPTY.value:
                return False
            if self.board[r][c] == color.opponent().value:
                found_opponent = True
            elif self.board[r][c] == color.value:
                return found_opponent
            r += dr
            c += dc
        return False

    def make_move(self, row: int, col: int, color: Color) -> bool:
        """Execute a move and flip pieces"""
        if not self.is_valid_move(row, col, color):
            return False

        self.board[row][col] = color.value

        for dr, dc in self.DIRECTIONS:
            if self._would_flip(row, col, dr, dc, color):
                self._flip_pieces(row, col, dr, dc, color)
        return True

    def _flip_pieces(self, row: int, col: int, dr: int, dc: int, color: Color):
        """Flip opponent pieces in a direction"""
        r, c = row + dr, col + dc
        while self.board[r][c] == color.opponent().value:
            self.board[r][c] = color.value
            r += dr
            c += dc

    def get_score(self) -> Tuple[int, int]:
        """Get current score (black, white)"""
        black = np.sum(self.board == Color.BLACK.value)
        white = np.sum(self.board == Color.WHITE.value)
        return (black, white)

    def copy(self):
        """Create a deep copy of the board"""
        new_board = Board(self.size)
        new_board.board = self.board.copy()
        return new_board

    def display(self):
        """Display the board"""
        print("  " + " ".join(str(i) for i in range(self.size)))
        for i, row in enumerate(self.board):
            symbols = [self._get_symbol(cell) for cell in row]
            print(f"{i} " + " ".join(symbols))

    def _get_symbol(self, value: int) -> str:
        if value == Color.BLACK.value:
            return "●"
        elif value == Color.WHITE.value:
            return "○"
        return "·"

    def get_size(self) -> int:
        return self.size