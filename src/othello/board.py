"""Bitboard based representation of an Othello board."""

from __future__ import annotations
from dataclasses import dataclass

# Board constants
BOARD_SIZE = 8
TOTAL_SQUARES = BOARD_SIZE * BOARD_SIZE

# Direction shifts for bitboard operations
DIRS = {
    'N': 8,
    'S': -8,
    'E': -1,
    'W': 1,
    'NE': 7,
    'NW': 9,
    'SE': -9,
    'SW': -7,
}

# Masks to handle wrapping on edges
NOT_A_FILE = int(0xfefefefefefefefe)
NOT_H_FILE = int(0x7f7f7f7f7f7f7f7f)

@dataclass(frozen=True)
class BitBoard:
    """Othello board encoded as two 64-bit integers for black and white."""

    black: int
    white: int

    @staticmethod
    def initial() -> "BitBoard":
        """Return a board in the standard initial Othello setup."""
        black = 0x0000000810000000
        white = 0x0000001008000000
        return BitBoard(black, white)

    @staticmethod
    def from_ascii(board_str: str) -> "BitBoard":
        """Create a board from an ASCII diagram.

        The diagram should consist of 8 lines of 8 characters using
        ``B`` for black, ``W`` for white and ``.`` for empty squares.
        """
        lines = [line.strip() for line in board_str.strip().splitlines()]
        if len(lines) != BOARD_SIZE:
            raise ValueError("Board diagram must have 8 lines")
        black = white = 0
        for r, line in enumerate(lines):
            if len(line) != BOARD_SIZE:
                raise ValueError("Each line in board diagram must have 8 characters")
            for c, ch in enumerate(line):
                bit = 1 << (TOTAL_SQUARES - 1 - (r * BOARD_SIZE + c))
                if ch == "B":
                    black |= bit
                elif ch == "W":
                    white |= bit
                elif ch != ".":
                    raise ValueError(f"Invalid character '{ch}' in board diagram")
        return BitBoard(black, white)

    def occupied(self) -> int:
        """Return a bitboard with all occupied squares."""
        return self.black | self.white

    def empty(self) -> int:
        """Return a bitboard with all empty squares."""
        return ~self.occupied() & ((1 << TOTAL_SQUARES) - 1)

    @staticmethod
    def _shift(bitboard: int, direction: str) -> int:
        shift = DIRS[direction]
        if shift > 0:
            bb = bitboard << shift
        else:
            bb = bitboard >> -shift
        if direction in ('E', 'NE', 'SE'):
            bb &= NOT_A_FILE
        if direction in ('W', 'NW', 'SW'):
            bb &= NOT_H_FILE
        return bb

    def legal_moves(self, player: int, opponent: int) -> int:
        """Return bitboard of legal moves for ``player`` against ``opponent``."""
        empty = self.empty()
        moves = 0
        for d in DIRS:
            mask = self._shift(player, d) & opponent
            while mask:
                mask = self._shift(mask, d)
                if mask & player:
                    break
                if mask & empty:
                    moves |= mask & empty
                    break
                mask &= opponent
        return moves

    def flips(self, move: int, player: int, opponent: int) -> int:
        """Return the stones that would be flipped by ``move``."""
        flips = 0
        for d in DIRS:
            mask = 0
            bb = self._shift(move, d)
            while bb & opponent:
                mask |= bb
                bb = self._shift(bb, d)
            if bb & player:
                flips |= mask
        return flips

    def apply_move(self, move: int, black_to_move: bool) -> "BitBoard":
        """Return new board after applying ``move`` for the current player."""
        player = self.black if black_to_move else self.white
        opponent = self.white if black_to_move else self.black
        flips = self.flips(move, player, opponent)
        if not flips:
            raise ValueError("Illegal move")
        player |= move | flips
        opponent &= ~flips
        if black_to_move:
            return BitBoard(player, opponent)
        else:
            return BitBoard(opponent, player)

    def __str__(self) -> str:
        """Return an ASCII representation of the board."""
        s = ""
        for i in range(TOTAL_SQUARES):
            bit = 1 << (TOTAL_SQUARES - 1 - i)
            if self.black & bit:
                s += "B"
            elif self.white & bit:
                s += "W"
            else:
                s += "."
            if (i + 1) % BOARD_SIZE == 0:
                s += "\n"
        return s


def parse_move(move_str: str) -> int:
    """Return bit mask corresponding to ``move_str`` such as 'd3'."""
    col = ord(move_str[0].lower()) - ord('a')
    row = int(move_str[1]) - 1
    pos = row * BOARD_SIZE + col
    return 1 << (TOTAL_SQUARES - 1 - pos)

