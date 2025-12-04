from .board import Board
from .player import Player


class Game:
    """Othello game controller"""

    def __init__(self, player1: Player, player2: Player):
        self.board = Board()
        self.players = [player1, player2]
        self.current_player_idx = 0

    def play(self):
        """Play a complete game"""
        consecutive_passes = 0

        while consecutive_passes < 2:
            current_player = self.players[self.current_player_idx]

            self.board.display()
            black, white = self.board.get_score()
            print(f"\nScore - Black: {black}, White: {white}")
            print(f"\n{current_player.name}'s turn")

            move = current_player.make_move(self.board)

            if move is None:
                print(f"{current_player.name} passes (no valid moves)")
                consecutive_passes += 1
            else:
                self.board.make_move(move[0], move[1], current_player.color)
                consecutive_passes = 0

            self.current_player_idx = 1 - self.current_player_idx

        self._show_final_results()

    def _show_final_results(self):
        """Display game results"""
        self.board.display()
        black, white = self.board.get_score()
        print("\n=== GAME OVER ===")
        print(f"Final Score - Black: {black}, White: {white}")

        if black > white:
            print("Black wins!")
        elif white > black:
            print("White wins!")
        else:
            print("It's a tie!")
