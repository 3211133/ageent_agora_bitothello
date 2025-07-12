"""Bitboard based representation of an Othello board."""

from __future__ import annotations
from dataclasses import dataclass

# Board constants
# CHANGED: support configurable board sizes via ``DEFAULT_BOARD_SIZE``.
DEFAULT_BOARD_SIZE = 8

# Direction keys used for shifting
DIR_KEYS = ("N", "S", "E", "W", "NE", "NW", "SE", "SW")

# Masks for the default 8x8 board (used for backwards compatibility)
NOT_A_FILE_DEFAULT = int(0x7F7F7F7F7F7F7F7F)
NOT_H_FILE_DEFAULT = int(0xFEFEFEFEFEFEFEFE)

# Backwards compatibility constants for the default 8x8 board
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
NOT_A_FILE = NOT_A_FILE_DEFAULT
NOT_H_FILE = NOT_H_FILE_DEFAULT

@dataclass(frozen=True)
class BitBoard:
    """Othello board encoded as two integers for black and white."""

    black: int
    white: int
    size: int = DEFAULT_BOARD_SIZE

    @staticmethod
    def initial(size: int = DEFAULT_BOARD_SIZE) -> "BitBoard":
        """Return a board in the standard initial Othello setup."""
        mid = size // 2
        total = size * size
        def pos(r: int, c: int) -> int:
            return 1 << (total - 1 - (r * size + c))

        black = pos(mid - 1, mid) | pos(mid, mid - 1)
        white = pos(mid - 1, mid - 1) | pos(mid, mid)
        return BitBoard(black, white, size)

    @staticmethod
    def from_ascii(board_str: str) -> "BitBoard":
        """Create a board from an ASCII diagram."""

        lines = [line.strip() for line in board_str.strip().splitlines()]
        size = len(lines)
        if any(len(line) != size for line in lines):
            raise ValueError("Board diagram must be square")
        total = size * size

        def pos(r: int, c: int) -> int:
            return 1 << (total - 1 - (r * size + c))

        black = white = 0
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                bit = pos(r, c)
                if ch == "B":
                    black |= bit
                elif ch == "W":
                    white |= bit
                elif ch != ".":
                    raise ValueError(f"Invalid character '{ch}' in board diagram")
        return BitBoard(black, white, size)

    def occupied(self) -> int:
        """Return a bitboard with all occupied squares."""
        return self.black | self.white

    def empty(self) -> int:
        """Return a bitboard with all empty squares."""
        mask = (1 << (self.size * self.size)) - 1
        return ~self.occupied() & mask

    @staticmethod
    def _file_mask(size: int, col: int) -> int:
        mask = 0
        total = size * size
        for r in range(size):
            mask |= 1 << (total - 1 - (r * size + col))
        return mask

    def _a_file_mask(self) -> int:
        return self._file_mask(self.size, 0)

    def _h_file_mask(self) -> int:
        return self._file_mask(self.size, self.size - 1)

    @staticmethod
    def _shift(bitboard: int, direction: str, size: int = DEFAULT_BOARD_SIZE) -> int:
        total = size * size
        mask = (1 << total) - 1

        if direction in ("E", "NE", "SE"):
            if bitboard & BitBoard._file_mask(size, size - 1):
                return 0
        if direction in ("W", "NW", "SW"):
            if bitboard & BitBoard._file_mask(size, 0):
                return 0

        shifts = {
            "N": size,
            "S": -size,
            "E": -1,
            "W": 1,
            "NE": size - 1,
            "NW": size + 1,
            "SE": -(size + 1),
            "SW": -(size - 1),
        }
        shift = shifts[direction]
        if shift > 0:
            bb = (bitboard << shift) & mask
        else:
            bb = (bitboard >> -shift) & mask
        return bb

    def legal_moves(self, player: int, opponent: int) -> int:
        """Return bitboard of legal moves for ``player`` against ``opponent``."""
        empty = self.empty()
        moves = 0
        candidates = empty
        while candidates:
            move = candidates & -candidates
            for d in DIR_KEYS:
                bb = BitBoard._shift(move, d, self.size)
                if bb & opponent:
                    bb = BitBoard._shift(bb, d, self.size)
                    while bb & opponent:
                        bb = BitBoard._shift(bb, d, self.size)
                    if bb & player:
                        moves |= move
                        break
            candidates ^= move
        return moves

    def flips(self, move: int, player: int, opponent: int) -> int:
        """Return the stones that would be flipped by ``move``."""
        flips = 0
        for d in DIR_KEYS:
            mask = 0
            bb = BitBoard._shift(move, d, self.size)
            while bb & opponent:
                mask |= bb
                bb = BitBoard._shift(bb, d, self.size)
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
            return BitBoard(player, opponent, self.size)
        else:
            return BitBoard(opponent, player, self.size)

    def __str__(self) -> str:
        """Return an ASCII representation of the board."""
        s = ""
        total = self.size * self.size
        for i in range(total):
            bit = 1 << (total - 1 - i)
            if self.black & bit:
                s += "B"
            elif self.white & bit:
                s += "W"
            else:
                s += "."
            if (i + 1) % self.size == 0:
                s += "\n"
        return s


def parse_move(move_str: str, size: int = DEFAULT_BOARD_SIZE) -> int:
    """Return bit mask corresponding to ``move_str`` such as 'd3'."""
    col = ord(move_str[0].lower()) - ord('a')
    row = int(move_str[1:]) - 1
    pos = row * size + col
    total = size * size
    return 1 << (total - 1 - pos)
