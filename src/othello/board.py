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

@dataclass
class BitBoard:
    black: int
    white: int

    @staticmethod
    def initial() -> "BitBoard":
        black = 0x0000000810000000
        white = 0x0000001008000000
        return BitBoard(black, white)

    def occupied(self) -> int:
        return self.black | self.white

    def empty(self) -> int:
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
        """Return bitboard of legal moves for the player."""
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
