from src.game import Board, Color, Player
from src.presentation import OthelloGUI
from src.strategies import HumanStrategy, Random, MinimaxAI, GreedyAI # noqa: F401

if __name__ == "__main__":
    board = Board()

    player1 = Player(Color.BLACK, HumanStrategy(), "Human")
    player2 = Player(Color.WHITE, MinimaxAI(), "AI (Minimax)")

    gui = OthelloGUI(board, player1, player2)
    gui.run()
