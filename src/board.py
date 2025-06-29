from dataclasses import dataclass
from typing import Tuple, List

# Bitboard indexes: 0 (LSB) = A1, 7 = H1, 8 = A2, ..., 63 = H8
# We'll use Python ints as 64-bit bitboards

# Direction masks for shifting
MASK_LEFT = 0xfefefefefefefefe
MASK_RIGHT = 0x7f7f7f7f7f7f7f7f
MASK_TOP = 0xffffffffffffff00
MASK_BOTTOM = 0x00ffffffffffffff

DIRECTIONS = {
    'N': 8,
    'S': -8,
    'E': -1,
    'W': 1,
    'NE': 7,
    'NW': 9,
    'SE': -9,
    'SW': -7,
}

@dataclass
class Board:
    black: int
    white: int

    @staticmethod
    def initial() -> 'Board':
        # Starting position: d5=black, e4=black, d4=white, e5=white
        black = (1 << 28) | (1 << 35)
        white = (1 << 27) | (1 << 36)
        return Board(black, white)

    def occupied(self) -> int:
        return self.black | self.white

    def empty(self) -> int:
        return ~self.occupied() & ((1 << 64) - 1)

    def side(self, color: str) -> int:
        return self.black if color == 'black' else self.white

    def opponent(self, color: str) -> int:
        return self.white if color == 'black' else self.black

    def set_side(self, color: str, bb: int) -> None:
        if color == 'black':
            self.black = bb
        else:
            self.white = bb

    def legal_moves(self, color: str) -> int:
        own = self.side(color)
        opp = self.opponent(color)
        empty = self.empty()
        moves = 0
        for dir, shift in DIRECTIONS.items():
            mask = self._shift(own, shift)
            capture = self._shift(mask & opp, shift)
            for _ in range(5):
                next_mask = self._shift(capture & opp, shift)
                capture |= next_mask
            moves |= self._shift(capture & empty, shift)
        return moves

    def apply_move(self, color: str, move: int) -> bool:
        if not (self.legal_moves(color) & move):
            return False
        own = self.side(color)
        opp = self.opponent(color)
        flipped = 0
        for dir, shift in DIRECTIONS.items():
            mask = self._shift(move, shift)
            capture = 0
            while mask and (mask & opp):
                capture |= mask
                mask = self._shift(mask, shift)
            if mask & own:
                flipped |= capture
        own |= move | flipped
        opp &= ~flipped
        self.set_side(color, own)
        if color == 'black':
            self.white = opp
        else:
            self.black = opp
        return True

    @staticmethod
    def _shift(bb: int, shift: int) -> int:
        if shift > 0:
            if shift == 8:
                return (bb << 8) & MASK_BOTTOM
            elif shift == 9:
                return (bb << 9) & MASK_LEFT & MASK_BOTTOM
            elif shift == 7:
                return (bb << 7) & MASK_RIGHT & MASK_BOTTOM
            elif shift == 1:
                return (bb << 1) & MASK_LEFT
        else:
            shift = -shift
            if shift == 8:
                return (bb >> 8) & MASK_TOP
            elif shift == 9:
                return (bb >> 9) & MASK_RIGHT & MASK_TOP
            elif shift == 7:
                return (bb >> 7) & MASK_LEFT & MASK_TOP
            elif shift == 1:
                return (bb >> 1) & MASK_RIGHT
        return 0

    def to_array(self) -> List[List[str]]:
        board = [['.' for _ in range(8)] for _ in range(8)]
        for i in range(64):
            mask = 1 << i
            if self.black & mask:
                board[i // 8][i % 8] = 'B'
            elif self.white & mask:
                board[i // 8][i % 8] = 'W'
        return board

    def __str__(self) -> str:
        arr = self.to_array()
        rows = []
        for r in arr[::-1]:
            rows.append(' '.join(r))
        return '\n'.join(rows)
