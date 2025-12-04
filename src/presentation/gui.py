import sys
from typing import Optional, Tuple

import pygame


class OthelloGUI:
    """Pygame GUI for Othello game"""

    # Colors
    BACKGROUND = (34, 139, 34)  # Forest green
    GRID_COLOR = (0, 0, 0)
    BLACK_PIECE = (0, 0, 0)
    WHITE_PIECE = (255, 255, 255)
    VALID_MOVE = (100, 200, 100)
    HIGHLIGHT = (255, 255, 0)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (70, 130, 180)
    BUTTON_HOVER = (100, 160, 210)

    def __init__(self, board, player1, player2, cell_size=70):
        """Initialize the GUI

        Args:
            board: Board instance
            player1: Player instance (first player)
            player2: Player instance (second player)
            cell_size: Size of each cell in pixels
        """
        pygame.init()

        self.board = board
        self.players = [player1, player2]
        self.current_player_idx = 0
        self.cell_size = cell_size
        self.board_size = board.size
        self.margin = 50
        self.info_height = 150

        # Calculate window dimensions
        self.board_width = self.board_size * cell_size
        self.board_height = self.board_size * cell_size
        self.window_width = self.board_width + 2 * self.margin
        self.window_height = self.board_height + 2 * self.margin + self.info_height

        # Create window
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Othello")

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Game state
        self.game_over = False
        self.winner = None
        self.consecutive_passes = 0
        self.last_move = None
        self.show_valid_moves = True
        self.ai_thinking = False

        # Button for toggling valid moves
        self.toggle_button_rect = pygame.Rect(
            self.margin, self.board_height + 2 * self.margin + 80, 200, 40
        )

        # Button for new game
        self.new_game_button_rect = pygame.Rect(
            self.margin + 220, self.board_height + 2 * self.margin + 80, 150, 40
        )

        self.clock = pygame.time.Clock()

    def get_board_pos(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos

        # Check if click is within board bounds
        if (
            self.margin <= x < self.margin + self.board_width
            and self.margin <= y < self.margin + self.board_height
        ):
            col = (x - self.margin) // self.cell_size
            row = (y - self.margin) // self.cell_size
            return (row, col)
        return None

    def draw_board(self):
        """Draw the game board"""
        # Background
        self.screen.fill(self.BACKGROUND)

        # Draw grid
        for i in range(self.board_size + 1):
            # Vertical lines
            start_x = self.margin + i * self.cell_size
            pygame.draw.line(
                self.screen,
                self.GRID_COLOR,
                (start_x, self.margin),
                (start_x, self.margin + self.board_height),
                2,
            )

            # Horizontal lines
            start_y = self.margin + i * self.cell_size
            pygame.draw.line(
                self.screen,
                self.GRID_COLOR,
                (self.margin, start_y),
                (self.margin + self.board_width, start_y),
                2,
            )

        # Draw valid moves if enabled and it's a human player's turn
        current_player = self.players[self.current_player_idx]
        if (
            self.show_valid_moves
            and not self.game_over
            and hasattr(current_player.strategy, "__class__")
            and current_player.strategy.__class__.__name__ == "HumanStrategy"
        ):
            valid_moves = self.board.get_valid_moves(current_player.color)
            for row, col in valid_moves:
                center_x = self.margin + col * self.cell_size + self.cell_size // 2
                center_y = self.margin + row * self.cell_size + self.cell_size // 2
                pygame.draw.circle(
                    self.screen,
                    self.VALID_MOVE,
                    (center_x, center_y),
                    self.cell_size // 6,
                )

        # Draw pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell_value = self.board.board[row][col]
                if cell_value != 0:  # Not empty
                    center_x = self.margin + col * self.cell_size + self.cell_size // 2
                    center_y = self.margin + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 5

                    # Highlight last move
                    if self.last_move and self.last_move == (row, col):
                        pygame.draw.circle(
                            self.screen,
                            self.HIGHLIGHT,
                            (center_x, center_y),
                            radius + 3,
                            3,
                        )

                    # Draw piece
                    color = self.BLACK_PIECE if cell_value == 1 else self.WHITE_PIECE
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                    # Add border
                    pygame.draw.circle(
                        self.screen, self.GRID_COLOR, (center_x, center_y), radius, 2
                    )

    def draw_info(self):
        """Draw game information (scores, current player, etc.)"""
        black_score, white_score = self.board.get_score()

        # Scores
        score_text = f"Black: {black_score}  White: {white_score}"
        score_surface = self.font_medium.render(score_text, True, self.TEXT_COLOR)
        score_rect = score_surface.get_rect(center=(self.window_width // 2, 20))
        self.screen.blit(score_surface, score_rect)

        # Current player info
        if not self.game_over:
            current_player = self.players[self.current_player_idx]
            if self.ai_thinking:
                status = "AI thinking..."
            else:
                status = f"{current_player.name}'s turn"
            status_surface = self.font_small.render(status, True, self.TEXT_COLOR)
            status_rect = status_surface.get_rect(
                center=(
                    self.window_width // 2,
                    self.board_height + 2 * self.margin + 20,
                )
            )
            self.screen.blit(status_surface, status_rect)
        else:
            # Game over message
            if self.winner:
                message = f"{self.winner} wins!"
            else:
                message = "It's a tie!"
            message_surface = self.font_large.render(message, True, self.TEXT_COLOR)
            message_rect = message_surface.get_rect(
                center=(
                    self.window_width // 2,
                    self.board_height + 2 * self.margin + 20,
                )
            )
            self.screen.blit(message_surface, message_rect)

        # Draw buttons
        self.draw_button(
            self.toggle_button_rect,
            "Valid Moves: ON" if self.show_valid_moves else "Valid Moves: OFF",
        )
        self.draw_button(self.new_game_button_rect, "New Game")

    def draw_button(self, rect, text):
        """Draw a button"""
        mouse_pos = pygame.mouse.get_pos()
        color = self.BUTTON_HOVER if rect.collidepoint(mouse_pos) else self.BUTTON_COLOR

        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, rect, 2, border_radius=5)

        text_surface = self.font_small.render(text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_human_move(self, board_pos: Tuple[int, int]) -> bool:
        """Handle a move from a human player"""
        current_player = self.players[self.current_player_idx]
        row, col = board_pos

        if self.board.is_valid_move(row, col, current_player.color):
            self.board.make_move(row, col, current_player.color)
            self.last_move = (row, col)
            self.consecutive_passes = 0
            return True
        return False

    def handle_ai_move(self) -> bool:
        """Handle a move from an AI player"""
        current_player = self.players[self.current_player_idx]

        self.ai_thinking = True
        self.draw()
        pygame.display.flip()

        # Add small delay for visual feedback
        pygame.time.wait(300)

        move = current_player.make_move(self.board)
        self.ai_thinking = False

        if move is None:
            self.consecutive_passes += 1
            return False
        else:
            self.board.make_move(move[0], move[1], current_player.color)
            self.last_move = move
            self.consecutive_passes = 0
            return True

    def check_game_over(self):
        """Check if the game is over"""
        if self.consecutive_passes >= 2:
            self.game_over = True
            black_score, white_score = self.board.get_score()

            if black_score > white_score:
                self.winner = "Black"
            elif white_score > black_score:
                self.winner = "White"
            else:
                self.winner = None  # Tie

    def reset_game(self):
        """Reset the game to initial state"""
        from src.game.board import Board

        self.board = Board(self.board_size)
        self.current_player_idx = 0
        self.game_over = False
        self.winner = None
        self.consecutive_passes = 0
        self.last_move = None

    def next_turn(self):
        """Move to the next turn"""
        # Check for game over before switching players
        self.check_game_over()
        if self.game_over:
            return

        self.current_player_idx = 1 - self.current_player_idx

        # Check if current player has valid moves
        current_player = self.players[self.current_player_idx]
        valid_moves = self.board.get_valid_moves(current_player.color)

        if not valid_moves:
            self.consecutive_passes += 1
            self.next_turn()  # Skip to next player

    def draw(self):
        """Draw everything"""
        self.draw_board()
        self.draw_info()

    def run(self):
        """Main game loop"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    mouse_pos = pygame.mouse.get_pos()

                    # Check button clicks
                    if self.toggle_button_rect.collidepoint(mouse_pos):
                        self.show_valid_moves = not self.show_valid_moves
                    elif self.new_game_button_rect.collidepoint(mouse_pos):
                        self.reset_game()
                    else:
                        # Check board clicks for human players
                        current_player = self.players[self.current_player_idx]
                        if (
                            hasattr(current_player.strategy, "__class__")
                            and current_player.strategy.__class__.__name__
                            == "HumanStrategy"
                        ):
                            board_pos = self.get_board_pos(mouse_pos)
                            if board_pos:
                                if self.handle_human_move(board_pos):
                                    self.next_turn()

                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    # Allow new game button in game over state
                    mouse_pos = pygame.mouse.get_pos()
                    if self.new_game_button_rect.collidepoint(mouse_pos):
                        self.reset_game()

            # Handle AI moves
            if not self.game_over:
                current_player = self.players[self.current_player_idx]
                if (
                    hasattr(current_player.strategy, "__class__")
                    and current_player.strategy.__class__.__name__ != "HumanStrategy"
                ):
                    self.handle_ai_move()
                    self.next_turn()

            # Draw
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS

        pygame.quit()
        sys.exit()
