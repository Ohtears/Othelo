from typing import Dict, Optional, Tuple

import numpy as np

from src.game.board import Board, Color

from .base import Strategy


class MinimaxAI(Strategy):
    """AI that chooses the move using the minimax algorithm with optional debugging"""

    c_squares_value = -20
    x_square_value = -50
    corner_value = 100
    edge_value = 10
    center_value = 0
    near_edge_value = 5

    def __init__(self, depth: int = 3, debug: bool = False):
        self.depth = depth
        self.weights = None
        self.debug = debug
        self.tree_data = []  
        self.node_counter = 0

    def choose_move(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        valid_moves = board.get_valid_moves(color)
        if not valid_moves:
            return None

        if self.debug:
            self.tree_data = []
            self.node_counter = 0
            print(f"\n{'=' * 80}")
            print(
                f"MINIMAX DECISION TREE - Depth {self.depth} - Playing as {color.name}"
            )
            print(f"{'=' * 80}\n")

        best_move = None
        best_value = float("-inf")
        move_evaluations = []

        for move in valid_moves:
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], color)

            if self.debug:
                print(f"Evaluating move {move}:")

            value = self._minimax(
                temp_board,
                self.depth - 1,
                float("-inf"),
                float("inf"),
                False,
                color,
                depth_level=1,
                parent_move=move,
            )

            move_evaluations.append((move, value))

            if self.debug:
                print(f"  → Final value: {value:.2f}\n")

            if value > best_value:
                best_value = value
                best_move = move

        if self.debug:
            print(f"\n{'=' * 80}")
            print("MOVE EVALUATION SUMMARY:")
            print(f"{'=' * 80}")
            sorted_moves = sorted(move_evaluations, key=lambda x: x[1], reverse=True)
            for i, (move, value) in enumerate(sorted_moves, 1):
                marker = "✓ CHOSEN" if move == best_move else ""
                print(f"{i}. Move {move}: {value:.2f} {marker}")
            print(f"{'=' * 80}\n")

        return best_move

    def _minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        color: Color,
        depth_level: int = 0,
        parent_move: Optional[Tuple[int, int]] = None,
    ) -> float:
        """Minimax with alpha-beta pruning and optional debugging"""

        indent = "  " * depth_level

        if depth == 0:
            eval_score = self._evaluate(board, color)
            if self.debug and depth_level <= 2:  # Only show first 2 levels
                print(f"{indent}[Leaf] Evaluation: {eval_score:.2f}")
            return eval_score

        current_color = color if maximizing else color.opponent()
        valid_moves = board.get_valid_moves(current_color)

        if not valid_moves:
            opponent_moves = board.get_valid_moves(current_color.opponent())
            if not opponent_moves:
                eval_score = self._evaluate(board, color)
                if self.debug and depth_level <= 2:
                    print(f"{indent}[Game Over] Evaluation: {eval_score:.2f}")
                return eval_score

            if self.debug and depth_level <= 2:
                print(f"{indent}[Pass] {current_color.name} has no moves")

            return self._minimax(
                board,
                depth - 1,
                alpha,
                beta,
                not maximizing,
                color,
                depth_level=depth_level,
                parent_move=parent_move,
            )

        if self.debug and depth_level <= 2:
            player = "MAX" if maximizing else "MIN"
            print(
                f"{indent}[{player} - Depth {depth}] {current_color.name} - {len(valid_moves)} moves available"
            )

        if maximizing:
            max_eval = float("-inf")
            for i, move in enumerate(valid_moves):
                if self.debug and depth_level <= 2:
                    print(f"{indent}  Move {i + 1}/{len(valid_moves)}: {move}")

                temp_board = board.copy()
                temp_board.make_move(move[0], move[1], current_color)
                eval_score = self._minimax(
                    temp_board,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    color,
                    depth_level=depth_level + 1,
                    parent_move=move,
                )

                if self.debug and depth_level <= 2:
                    print(f"{indent}  → Returns: {eval_score:.2f}")

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    if self.debug and depth_level <= 2:
                        print(f"{indent}  ✂ PRUNED (α={alpha:.2f} ≥ β={beta:.2f})")
                    break

            return max_eval
        else:
            min_eval = float("inf")
            for i, move in enumerate(valid_moves):
                if self.debug and depth_level <= 2:
                    print(f"{indent}  Move {i + 1}/{len(valid_moves)}: {move}")

                temp_board = board.copy()
                temp_board.make_move(move[0], move[1], current_color)
                eval_score = self._minimax(
                    temp_board,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    color,
                    depth_level=depth_level + 1,
                    parent_move=move,
                )

                if self.debug and depth_level <= 2:
                    print(f"{indent}  → Returns: {eval_score:.2f}")

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    if self.debug and depth_level <= 2:
                        print(f"{indent}  ✂ PRUNED (β={beta:.2f} ≤ α={alpha:.2f})")
                    break

            return min_eval

    def _evaluate(self, board: Board, color: Color) -> float:
        """
        Heuristics

        1. Piece count difference
        2. Positional weights (corners, edges, etc.)
        3. Mobility (number of available moves)

        - Weighted combination of factors
        - Position is most important early/mid game
        - Piece count becomes more important in endgame

        """
        board_size = board.size

        if self.weights is None or len(self.weights) != board_size:
            if board_size == 8:
                self.weights = np.array(
                    [
                        [100, -20, 10, 5, 5, 10, -20, 100],
                        [-20, -50, -2, -2, -2, -2, -50, -20],
                        [10, -2, 5, 1, 1, 5, -2, 10],
                        [5, -2, 1, 0, 0, 1, -2, 5],
                        [5, -2, 1, 0, 0, 1, -2, 5],
                        [10, -2, 5, 1, 1, 5, -2, 10],
                        [-20, -50, -2, -2, -2, -2, -50, -20],
                        [100, -20, 10, 5, 5, 10, -20, 100],
                    ]
                )
            else:
                self.weights = self._generate_positional_weights(board_size)

        # * Positional score
        position_score = 0
        for r in range(board_size):
            for c in range(board_size):
                if board.board[r][c] == color.value:
                    position_score += self.weights[r][c]
                elif board.board[r][c] == color.opponent().value:
                    position_score -= self.weights[r][c]

        # * Piece count difference
        black_count, white_count = board.get_score()
        piece_diff = (
            black_count - white_count
            if color == Color.BLACK
            else white_count - black_count
        )

        # * Mobility (number of available moves)
        my_moves = len(board.get_valid_moves(color))
        opponent_moves = len(board.get_valid_moves(color.opponent()))
        mobility_score = my_moves - opponent_moves

        total_pieces = black_count + white_count
        max_pieces = board_size * board_size
        game_progress = total_pieces / max_pieces

        # Adjust weights based on game phase
        if game_progress < 0.5:
            # * Early game: prioritize position and mobility
            return position_score * 1.0 + piece_diff * 0.5 + mobility_score * 3.0
        elif game_progress < 0.75:
            # * Mid game: balance all factors
            return position_score * 0.8 + piece_diff * 1.0 + mobility_score * 2.0
        else:
            # * End game: piece count is most important
            return position_score * 0.3 + piece_diff * 2.0 + mobility_score * 1.0

    def get_evaluation_breakdown(self, board: Board, color: Color) -> Dict:
        """Get detailed breakdown of evaluation for debugging"""
        board_size = board.size

        if self.weights is None or len(self.weights) != board_size:
            if board_size == 8:
                self.weights = np.array(
                    [
                        [100, -20, 10, 5, 5, 10, -20, 100],
                        [-20, -50, -2, -2, -2, -2, -50, -20],
                        [10, -2, 5, 1, 1, 5, -2, 10],
                        [5, -2, 1, 0, 0, 1, -2, 5],
                        [5, -2, 1, 0, 0, 1, -2, 5],
                        [10, -2, 5, 1, 1, 5, -2, 10],
                        [-20, -50, -2, -2, -2, -2, -50, -20],
                        [100, -20, 10, 5, 5, 10, -20, 100],
                    ]
                )
            else:
                self.weights = self._generate_positional_weights(board_size)

        # Calculate all components
        position_score = 0
        for r in range(board_size):
            for c in range(board_size):
                if board.board[r][c] == color.value:
                    position_score += self.weights[r][c]
                elif board.board[r][c] == color.opponent().value:
                    position_score -= self.weights[r][c]

        black_count, white_count = board.get_score()
        piece_diff = (
            black_count - white_count
            if color == Color.BLACK
            else white_count - black_count
        )

        my_moves = len(board.get_valid_moves(color))
        opponent_moves = len(board.get_valid_moves(color.opponent()))
        mobility_score = my_moves - opponent_moves

        total_pieces = black_count + white_count
        max_pieces = board_size * board_size
        game_progress = total_pieces / max_pieces

        # Determine phase
        if game_progress < 0.5:
            phase = "Early Game"
            weights = (1.0, 0.5, 3.0)
        elif game_progress < 0.75:
            phase = "Mid Game"
            weights = (0.8, 1.0, 2.0)
        else:
            phase = "End Game"
            weights = (0.3, 2.0, 1.0)

        final_score = (
            position_score * weights[0]
            + piece_diff * weights[1]
            + mobility_score * weights[2]
        )

        return {
            "phase": phase,
            "game_progress": f"{game_progress * 100:.1f}%",
            "position_score": position_score,
            "piece_diff": piece_diff,
            "mobility": {
                "my_moves": my_moves,
                "opponent_moves": opponent_moves,
                "score": mobility_score,
            },
            "weights": {
                "position": weights[0],
                "pieces": weights[1],
                "mobility": weights[2],
            },
            "final_score": final_score,
        }

    def _generate_positional_weights(self, board_size: int) -> np.ndarray:
        """Generate positional weights dynamically for any board size"""
        weights = np.zeros((board_size, board_size), dtype=int)

        def edge_score(i):
            if i == 0:
                return self.corner_value
            elif i == 1:
                return self.c_squares_value
            elif i == 2:
                return self.near_edge_value
            else:
                return self.edge_value

        for i in range(board_size):
            weights[0, i] = edge_score(i)
            weights[board_size - 1, i] = edge_score(i)
            weights[i, 0] = edge_score(i)
            weights[i, board_size - 1] = edge_score(i)

        xs = [
            (1, 1),
            (1, board_size - 2),
            (board_size - 2, 1),
            (board_size - 2, board_size - 2),
        ]
        for x, y in xs:
            weights[x, y] = self.x_square_value

        cs = [
            (0, 1),
            (1, 0),
            (0, board_size - 2),
            (1, board_size - 1),
            (board_size - 1, 1),
            (board_size - 2, 0),
            (board_size - 1, board_size - 2),
            (board_size - 2, board_size - 1),
        ]
        for x, y in cs:
            weights[x, y] = self.c_squares_value

        mid = (board_size - 1) / 2
        for i in range(1, board_size - 1):
            for j in range(1, board_size - 1):
                if (i, j) in xs or (i, j) in cs:
                    continue
                dist = abs(i - mid) + abs(j - mid)
                weights[i, j] = round((dist / board_size) * self.near_edge_value)

        return weights
