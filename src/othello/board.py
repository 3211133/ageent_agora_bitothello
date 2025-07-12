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
        """Return a board in the standard initial Othello setup.
        
        Args:
            size: Board size (must be even and within reasonable limits)
            
        Returns:
            BitBoard with initial Othello setup
            
        Raises:
            ValueError: If size is invalid
            TypeError: If size is not an integer
        """
        # Input validation
        if not isinstance(size, int):
            raise TypeError(f"Size must be an integer, got {type(size).__name__}")
        
        if size < 4 or size > 26:
            raise ValueError(f"Board size {size} out of valid range (4-26)")
        
        if size % 2 != 0:
            raise ValueError(f"Board size {size} must be even")
        
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
    """Return bit mask corresponding to ``move_str`` such as 'd3'.
    
    Args:
        move_str: Move in algebraic notation (e.g., 'd3', 'A1')
        size: Board size for bounds validation
        
    Returns:
        Bit mask for the move position
        
    Raises:
        ValueError: If move format is invalid or out of bounds
        TypeError: If inputs are not of expected types
    """
    # Input type validation
    if not isinstance(move_str, str):
        raise TypeError(f"Move must be a string, got {type(move_str).__name__}")
    
    if not isinstance(size, int):
        raise TypeError(f"Size must be an integer, got {type(size).__name__}")
    
    # Size bounds validation
    if size < 4 or size > 26:  # Reasonable board size limits
        raise ValueError(f"Board size {size} out of valid range (4-26)")
    
    if size % 2 != 0:
        raise ValueError(f"Board size {size} must be even")
    
    # Move string validation
    if not move_str or not move_str.strip():
        raise ValueError("Move string cannot be empty")
    
    move_str = move_str.strip().lower()
    
    # Format validation: should be letter + number(s)
    if len(move_str) < 2:
        raise ValueError(f"Invalid move format '{move_str}'. Expected format: letter + number (e.g., 'd3')")
    
    # Validate first character is a letter
    if not move_str[0].isalpha():
        raise ValueError(f"Invalid move format '{move_str}'. First character must be a letter")
    
    # Validate remaining characters are digits
    if not move_str[1:].isdigit():
        raise ValueError(f"Invalid move format '{move_str}'. Row must be a number")
    
    # Parse column (letter)
    col_char = move_str[0]
    col = ord(col_char) - ord('a')
    
    # Validate column bounds
    if col < 0 or col >= size:
        max_col = chr(ord('a') + size - 1)
        raise ValueError(f"Column '{col_char}' out of bounds. Valid columns: a-{max_col}")
    
    # Parse row (number)
    try:
        row = int(move_str[1:]) - 1  # Convert to 0-based
    except ValueError:
        raise ValueError(f"Invalid row number in '{move_str}'")
    
    # Validate row bounds
    if row < 0 or row >= size:
        raise ValueError(f"Row {row + 1} out of bounds. Valid rows: 1-{size}")
    
    # Calculate position and validate
    pos = row * size + col
    total = size * size
    
    if pos >= total:
        raise ValueError(f"Position calculation error: {pos} >= {total}")
    
    return 1 << (total - 1 - pos)
