"""Simple Tkinter based GUI for playing Othello."""

# TODO: improve GUI layout and graphics

import tkinter as tk
from tkinter import messagebox

# Handle both relative and absolute imports for direct execution
try:
    from .board import BitBoard, BOARD_SIZE, TOTAL_SQUARES
    from .ai import choose_move
    from . import scoreboard
except (ImportError, ValueError):
    # Direct execution fallback
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from othello.board import BitBoard, BOARD_SIZE, TOTAL_SQUARES
    from othello.ai import choose_move
    import scoreboard

SIZE = 50

class OthelloGUI:
    def __init__(self, vs_ai: bool = False, ai_level: str = "easy") -> None:
        self.vs_ai = vs_ai
        self.ai_level = ai_level
        self.board = BitBoard.initial()
        self.black_to_move = True
        self.root = tk.Tk()
        self.root.title("Othello")
        self.canvas = tk.Canvas(self.root, width=SIZE * BOARD_SIZE, height=SIZE * BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.status_label = tk.Label(self.root, text="", fg="red")
        self.status_label.pack()
        self.draw_board()

    def draw_board(self) -> None:
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1, y1 = col * SIZE, row * SIZE
                x2, y2 = x1 + SIZE, y1 + SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")
                bit = 1 << (63 - (row * BOARD_SIZE + col))
                if self.board.black & bit:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                elif self.board.white & bit:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
        # TODO: implement get_legal_moves to return coordinates
        legal_moves = self.get_legal_moves(
            self.board.black if self.black_to_move else self.board.white,
            self.board.white if self.black_to_move else self.board.black,
        )
        for row, col in legal_moves:
            x1, y1 = col * SIZE + SIZE // 2 - 5, row * SIZE + SIZE // 2 - 5
            x2, y2 = x1 + 10, y1 + 10
            self.canvas.create_oval(x1, y1, x2, y2, outline="yellow")

    def get_legal_moves(self, player: int, opponent: int) -> list[tuple[int, int]]:
        """Return list of legal move coordinates for ``player``."""
        moves = self.board.legal_moves(player, opponent)
        result = []
        while moves:
            lsb = moves & -moves
            idx = lsb.bit_length() - 1
            pos = TOTAL_SQUARES - 1 - idx
            row, col = divmod(pos, BOARD_SIZE)
            result.append((row, col))
            moves ^= lsb
        return result

    def handle_click(self, event) -> None:
        col = event.x // SIZE
        row = event.y // SIZE
        pos = row * BOARD_SIZE + col
        move = 1 << (63 - pos)
        player = self.board.black if self.black_to_move else self.board.white
        opponent = self.board.white if self.black_to_move else self.board.black
        if move & self.board.legal_moves(player, opponent):
            self.board = self.board.apply_move(move, self.black_to_move)
            self.black_to_move = not self.black_to_move
            self.status_label.config(text="")  # Clear the status label after a valid move
            self.after_move()
        else:
            # Display illegal move message
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text="Illegal move")

    def after_move(self) -> None:
        if self.vs_ai and not self.black_to_move:
            move = choose_move(self.board, self.black_to_move, level=self.ai_level)
            if move:
                self.board = self.board.apply_move(move, self.black_to_move)
            self.black_to_move = not self.black_to_move
        self.draw_board()
        player_moves = self.board.legal_moves(
            self.board.black if self.black_to_move else self.board.white,
            self.board.white if self.black_to_move else self.board.black,
        )
        if player_moves == 0:
            self.black_to_move = not self.black_to_move
            opponent_moves = self.board.legal_moves(
                self.board.black if self.black_to_move else self.board.white,
                self.board.white if self.black_to_move else self.board.black,
            )
            if opponent_moves == 0:
                b = bin(self.board.black).count("1")
                w = bin(self.board.white).count("1")
                self.canvas.create_text(
                    SIZE * 4,
                    SIZE * 4,
                    text=f"Game over\nB:{b} W:{w}",
                    fill="red",
                    font=("Helvetica", 20),
                )
                winner = "Black" if b > w else "White" if w > b else None
                scores = scoreboard.update_scores(winner)
                messagebox.showinfo("Scoreboard", scoreboard.format_scores(scores))
                self.canvas.unbind("<Button-1>")
                return
            if self.vs_ai and not self.black_to_move:
                self.after_move()

    def run(self) -> None:
        self.root.mainloop()


def play_gui(vs_ai: bool = False, ai_level: str = "easy") -> None:
    """Entry point for playing the GUI version."""
    OthelloGUI(vs_ai, ai_level).run()
# TODO: expose additional GUI options via CLI

if __name__ == "__main__":
    play_gui(vs_ai=True)
