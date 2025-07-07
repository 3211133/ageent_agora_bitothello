"""Comprehensive tests for BitBoard functionality focusing on board processing accuracy."""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, parse_move


def mask_from_ascii(board_str: str) -> int:
    """Convert ASCII board diagram to bitmask for testing."""
    lines = [line.strip() for line in board_str.strip().splitlines()]
    mask = 0
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch != ".":
                bit = 1 << (63 - (r * 8 + c))
                mask |= bit
    return mask


def test_complex_board_legal_moves():
    """Test legal move generation on a complex mid-game board."""
    board = BitBoard.from_ascii(
        """
........
..BBB...
.BWWWB..
.BWBWB..
.BWWWB..
..BBB...
........
........
"""
    )
    
    # Test black legal moves
    black_moves = board.legal_moves(board.black, board.white)
    expected_black = mask_from_ascii(
        """
........
.X...X..
........
........
........
.X...X..
........
........
"""
    )
    assert black_moves == expected_black


def test_corner_capture_sequence():
    """Test accurate stone flipping when capturing corners."""
    # Create a realistic scenario where a corner move is actually legal
    board = BitBoard.from_ascii(
        """
........
.BWWWWW.
.BWWWWW.
.BWWWWW.
.BWWWWW.
.BWWWWW.
.BWWWWW.
........
"""
    )

    # Black plays h1 (corner) - this is actually legal in this position
    move = parse_move("h1")
    new_board = board.apply_move(move, True)  # Black to move

    expected = BitBoard.from_ascii(
        """
.......B
.BWWWWB.
.BWWWBW.
.BWWBWW.
.BWBWWW.
.BBWWWW.
.BWWWWW.
........
"""
    )
    assert new_board == expected


def test_multiple_direction_flips():
    """Test flipping stones in multiple directions simultaneously."""
    board = BitBoard.from_ascii(
        """
..B.B...
.B.W.B..
B.WWW.B.
.WW.WW..
B.WWW.B.
.B.W.B..
..B.B...
........
"""
    )
    
    # Black plays d4 (center) - should flip in all 8 directions
    move = parse_move("d4")
    flips = board.flips(move, board.black, board.white)
    
    expected_flips = mask_from_ascii(
        """
........
........
..X.X...
........
..X.X...
........
........
........
"""
    )
    assert flips == expected_flips


def test_edge_wrapping_prevention():
    """Test that moves don't wrap around board edges incorrectly."""
    board = BitBoard.from_ascii(
        """
B.......
W.......
........
........
........
........
........
.......W
"""
    )
    
    # Test that black at a1 cannot flip white at h8
    black_moves = board.legal_moves(board.black, board.white)
    
    # Should not include any moves that would wrap around
    # Only valid move should be a3 to flip the white at a2
    expected_moves = mask_from_ascii(
        """
........
........
X.......
........
........
........
........
........
"""
    )
    assert black_moves == expected_moves


def test_no_legal_moves_detection():
    """Test detection when a player has no legal moves."""
    board = BitBoard.from_ascii(
        """
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBWWBBB
BBBWWBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
"""
    )
    
    # Both players should have no legal moves in this position
    white_moves = board.legal_moves(board.white, board.black)
    assert white_moves == 0
    
    black_moves = board.legal_moves(board.black, board.white)
    assert black_moves == 0


def test_full_board_no_moves():
    """Test behavior when board is completely full."""
    board = BitBoard.from_ascii(
        """
BBBBWWWW
BBBBWWWW
BBBBWWWW
BBBBWWWW
WWWWBBBB
WWWWBBBB
WWWWBBBB
WWWWBBBB
"""
    )
    
    # Neither player should have legal moves
    assert board.legal_moves(board.black, board.white) == 0
    assert board.legal_moves(board.white, board.black) == 0
    
    # Board should be completely occupied
    assert board.empty() == 0
    assert board.occupied() == (1 << 64) - 1


def test_single_stone_isolation():
    """Test behavior with isolated single stones."""
    board = BitBoard.from_ascii(
        """
B.......
........
........
........
........
........
........
.......W
"""
    )
    
    # Neither player should have legal moves (no adjacent opponent stones)
    assert board.legal_moves(board.black, board.white) == 0
    assert board.legal_moves(board.white, board.black) == 0


def test_long_line_flips():
    """Test flipping long lines of stones."""
    board = BitBoard.from_ascii(
        """
B.......
W.......
W.......
W.......
W.......
W.......
W.......
........
"""
    )
    
    # Black plays a8
    move = parse_move("a8")
    new_board = board.apply_move(move, True)
    
    expected = BitBoard.from_ascii(
        """
B.......
B.......
B.......
B.......
B.......
B.......
B.......
B.......
"""
    )
    assert new_board == expected


def test_diagonal_line_flips():
    """Test flipping along diagonal lines."""
    board = BitBoard.from_ascii(
        """
........
.B......
..B.....
...B....
....B...
.....B..
......B.
.......W
"""
    )
    
    # White plays a1
    move = parse_move("a1")
    new_board = board.apply_move(move, False)  # White to move
    
    expected = BitBoard.from_ascii(
        """
W.......
.W......
..W.....
...W....
....W...
.....W..
......W.
.......W
"""
    )
    assert new_board == expected


def test_board_symmetry():
    """Test that board operations maintain expected symmetries."""
    # Create a symmetric board
    board = BitBoard.from_ascii(
        """
........
..BWWB..
.WBBBBW.
.WBWWBW.
.WBWWBW.
.WBBBBW.
..BWWB..
........
"""
    )
    
    # Legal moves should also be symmetric
    black_moves = board.legal_moves(board.black, board.white)
    
    # Convert back to check symmetry
    moves_board = ""
    for i in range(64):
        bit = 1 << (63 - i)
        if black_moves & bit:
            moves_board += "X"
        else:
            moves_board += "."
        if (i + 1) % 8 == 0:
            moves_board += "\n"
    
    # Should have symmetric pattern of legal moves
    lines = moves_board.strip().split('\n')
    assert len(lines) == 8
    
    # Check horizontal symmetry (left-right)
    for line in lines:
        assert line == line[::-1]


def test_occupied_and_empty_consistency():
    """Test that occupied() and empty() are consistent complements."""
    board = BitBoard.from_ascii(
        """
B.W.B.W.
.W.B.W.B
W.B.W.B.
.B.W.B.W
B.W.B.W.
.W.B.W.B
W.B.W.B.
.B.W.B.W
"""
    )
    
    occupied = board.occupied()
    empty = board.empty()
    
    # They should be perfect complements
    assert (occupied | empty) == (1 << 64) - 1
    assert (occupied & empty) == 0
    
    # Count should add up to 64
    assert bin(occupied).count('1') + bin(empty).count('1') == 64


def test_move_validation_edge_cases():
    """Test move validation for edge cases."""
    board = BitBoard.initial()
    
    # Test invalid moves that should raise ValueError
    invalid_moves = [
        parse_move("a1"),  # Corner with no flips
        parse_move("h8"),  # Opposite corner
        parse_move("d4"),  # Occupied square
        parse_move("e4"),  # Occupied square
    ]
    
    for move in invalid_moves:
        with pytest.raises(ValueError):
            board.apply_move(move, True)


def test_bit_manipulation_accuracy():
    """Test that bit manipulation operations are accurate."""
    board = BitBoard.initial()
    
    # Test that bit positions correspond to correct board positions
    # d4 should be bit position 27 (counting from 0, top-left)
    d4_bit = parse_move("d4")
    expected_bit = 1 << (63 - 27)  # 63 - (3*8 + 3)
    assert d4_bit == expected_bit
    
    # Test that the initial board has exactly 4 stones
    assert bin(board.black).count('1') == 2
    assert bin(board.white).count('1') == 2
    assert bin(board.occupied()).count('1') == 4


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])
