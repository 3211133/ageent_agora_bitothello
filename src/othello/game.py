from __future__ import annotations
from dataclasses import dataclass, field

from .board import BitBoard


@dataclass
class Game:
    """Game state holding the board and turn information."""

    board: BitBoard = field(default_factory=BitBoard.initial)
    black_to_move: bool = True
    history: list[tuple[BitBoard, bool]] = field(default_factory=list)
    future: list[tuple[BitBoard, bool]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.history:
            self.history.append((self.board, self.black_to_move))

    def legal_moves(self) -> int:
        player = self.board.black if self.black_to_move else self.board.white
        opponent = self.board.white if self.black_to_move else self.board.black
        return self.board.legal_moves(player, opponent)

    def apply_move(self, move: int) -> None:
        self.board = self.board.apply_move(move, self.black_to_move)
        self.black_to_move = not self.black_to_move
        self.history.append((self.board, self.black_to_move))
        self.future.clear()

    def undo(self) -> bool:
        if len(self.history) <= 1:
            return False
        self.future.append(self.history.pop())
        self.board, self.black_to_move = self.history[-1]
        return True

    def redo(self) -> bool:
        if not self.future:
            return False
        self.board, self.black_to_move = self.future.pop()
        self.history.append((self.board, self.black_to_move))
        return True


def save_state(board: BitBoard, black_to_move: bool, path: str = "othello.sav") -> None:
    """Save ``board`` and turn information to ``path``."""
    with open(path, "w") as f:
        f.write(f"{board.black}\n{board.white}\n{1 if black_to_move else 0}\n")


def load_state(path: str = "othello.sav") -> tuple[BitBoard, bool]:
    """Load board and turn information from ``path``."""
    with open(path) as f:
        lines = f.read().splitlines()
    if len(lines) != 3:
        raise ValueError("Invalid save file")
    board = BitBoard(int(lines[0]), int(lines[1]))
    black_to_move = bool(int(lines[2]))
    return board, black_to_move
