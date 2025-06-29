"""Simple Tkinter based GUI for playing Othello."""

import tkinter as tk
from .board import BitBoard
from .ai import choose_move

SIZE = 50

class OthelloGUI:
    def __init__(self, vs_ai: bool = False) -> None:
        self.vs_ai = vs_ai
        self.board = BitBoard.initial()
        self.black_to_move = True
        self.root = tk.Tk()
        self.root.title("Othello")
        self.canvas = tk.Canvas(self.root, width=SIZE * BOARD_SIZE, height=SIZE * BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
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
        legal = self.board.legal_moves(
            self.board.black if self.black_to_move else self.board.white,
            self.board.white if self.black_to_move else self.board.black,
        )
        bb = legal
        while bb:
            lsb = bb & -bb
            idx = (lsb.bit_length() - 1)
            pos = 63 - idx
            row, col = divmod(pos, 8)
            x1, y1 = col * SIZE + SIZE // 2 - 5, row * SIZE + SIZE // 2 - 5
            x2, y2 = x1 + 10, y1 + 10
            self.canvas.create_oval(x1, y1, x2, y2, outline="yellow")
            bb ^= lsb

    def handle_click(self, event) -> None:
        col = event.x // SIZE
        row = event.y // SIZE
        pos = row * 8 + col
        move = 1 << (63 - pos)
        player = self.board.black if self.black_to_move else self.board.white
        opponent = self.board.white if self.black_to_move else self.board.black
        if move & self.board.legal_moves(player, opponent):
            self.board = self.board.apply_move(move, self.black_to_move)
            self.black_to_move = not self.black_to_move
            self.after_move()
        else:
            print("Illegal move")

    def after_move(self) -> None:
        if self.vs_ai and not self.black_to_move:
            move = choose_move(self.board, self.black_to_move)
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
                self.canvas.unbind("<Button-1>")
                return
            if self.vs_ai and not self.black_to_move:
                self.after_move()

    def run(self) -> None:
        self.root.mainloop()


def play_gui(vs_ai: bool = False) -> None:
    """Entry point for playing the GUI version."""
    OthelloGUI(vs_ai).run()

if __name__ == "__main__":
    play_gui(vs_ai=True)
