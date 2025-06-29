BOARD_MASK = 0xFFFFFFFFFFFFFFFF

WHITE = 1
BLACK = -1

# Masks for board edges to prevent wrapping in bit shifts
LEFT_EDGE  = 0x0101010101010101
RIGHT_EDGE = 0x8080808080808080
TOP_EDGE   = 0xFF00000000000000
BOTTOM_EDGE= 0x00000000000000FF

DIRECTIONS = [8, -8, 1, -1, 9, -9, 7, -7]


def shift(bb: int, direction: int) -> int:
    """Shift bitboard in given direction with edge handling."""
    if direction == 8:  # north
        return (bb & ~TOP_EDGE) >> 8
    if direction == -8:  # south
        return (bb & ~BOTTOM_EDGE) << 8
    if direction == 1:  # east
        return (bb & ~RIGHT_EDGE) >> 1
    if direction == -1:  # west
        return (bb & ~LEFT_EDGE) << 1
    if direction == 9:  # north-east
        return (bb & ~(TOP_EDGE | RIGHT_EDGE)) >> 9
    if direction == -9:  # south-west
        return (bb & ~(BOTTOM_EDGE | LEFT_EDGE)) << 9
    if direction == 7:  # north-west
        return (bb & ~(TOP_EDGE | LEFT_EDGE)) >> 7
    if direction == -7:  # south-east
        return (bb & ~(BOTTOM_EDGE | RIGHT_EDGE)) << 7
    raise ValueError("invalid direction")


class Board:
    """Othello board using bitboard representation."""

    def __init__(self):
        # Initial configuration for black and white discs
        self.black = 0x0000000810000000
        self.white = 0x0000001008000000

    def occupied(self) -> int:
        return self.black | self.white

    def empty(self) -> int:
        return BOARD_MASK & ~self.occupied()

    def legal_moves(self, color: int) -> int:
        empty = self.empty()
        moves = 0
        for i in range(64):
            bit = 1 << i
            if bit & empty and self._flips(color, bit):
                moves |= bit
        return moves

    def _flips(self, color: int, move: int) -> int:
        player = self.black if color == BLACK else self.white
        opponent = self.white if color == BLACK else self.black
        flips = 0
        for d in DIRECTIONS:
            mask = shift(move, d) & opponent
            captured = 0
            while mask:
                captured |= mask
                mask = shift(mask, d)
                if mask & player:
                    flips |= captured
                    break
                if not (mask & opponent):
                    break
                mask &= opponent
        return flips

    def apply_move(self, color: int, move: int) -> bool:
        if not (move & self.empty()):
            return False
        flips = self._flips(color, move)
        if flips == 0:
            return False
        if color == BLACK:
            self.black ^= move | flips
            self.white ^= flips
        else:
            self.white ^= move | flips
            self.black ^= flips
        return True

    def moves_list(self, color: int):
        moves = self.legal_moves(color)
        return [1 << i for i in range(64) if moves & (1 << i)]

    def count(self):
        return bin(self.black).count('1'), bin(self.white).count('1')

