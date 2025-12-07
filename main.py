from src.game.board import Board, Color
from src.game.player import Player
from src.presentation import OthelloGUI
from src.strategies.greedy_ai import GreedyAI  # noqa: F401
from src.strategies.human import HumanStrategy  # noqa: F401
from src.strategies.minimax import MinimaxAI  # noqa: F401
from src.strategies.random import Random  # noqa: F401

if __name__ == "__main__":
    board = Board()

    player1 = Player(Color.BLACK, HumanStrategy(), "Human")
    player2 = Player(Color.WHITE, MinimaxAI(debug=False, depth=3), "AI (Minimax)")

    gui = OthelloGUI(board, player1, player2)
    gui.run()
