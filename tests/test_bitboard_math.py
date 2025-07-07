"""Mathematical verification tests for bitboard operations."""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, parse_move, DIRS, NOT_A_FILE, NOT_H_FILE


def test_direction_shifts_accuracy():
    """Test that direction shifts work correctly for all 8 directions."""
    # Test from center position d4 (bit 27)
    center_bit = 1 << (63 - 27)  # d4
    
    # Expected positions after shifting
    expected_shifts = {
        'N': 1 << (63 - 19),  # d3
        'S': 1 << (63 - 35),  # d5
        'E': 1 << (63 - 28),  # e4
        'W': 1 << (63 - 26),  # c4
        'NE': 1 << (63 - 20), # e3
        'NW': 1 << (63 - 18), # c3
        'SE': 1 << (63 - 36), # e5
        'SW': 1 << (63 - 34), # c5
    }
    
    for direction, expected in expected_shifts.items():
        shifted = BitBoard._shift(center_bit, direction)
        assert shifted == expected, f"Direction {direction} shift failed"


def test_edge_mask_correctness():
    """Test that edge masks prevent wrapping correctly."""
    # Test A-file mask (NOT_A_FILE)
    a_file = 0x8080808080808080  # All A-file positions
    assert (a_file & NOT_A_FILE) == 0, "NOT_A_FILE should mask out A-file"
    
    # Test H-file mask (NOT_H_FILE)
    h_file = 0x0101010101010101  # All H-file positions
    assert (h_file & NOT_H_FILE) == 0, "NOT_H_FILE should mask out H-file"
    
    # Test that other positions are preserved
    middle_files = 0x7E7E7E7E7E7E7E7E  # Files B-G
    assert (middle_files & NOT_A_FILE) == middle_files
    assert (middle_files & NOT_H_FILE) == middle_files


def test_bit_position_mapping():
    """Test that coordinate-to-bit mapping is mathematically correct."""
    test_cases = [
        ("a1", 0),   # Top-left
        ("h1", 7),   # Top-right
        ("a8", 56),  # Bottom-left
        ("h8", 63),  # Bottom-right
        ("d4", 27),  # Center
        ("e5", 36),  # Center-right
    ]
    
    for coord, expected_pos in test_cases:
        bit = parse_move(coord)
        actual_pos = 63 - (bit.bit_length() - 1)
        assert actual_pos == expected_pos, f"{coord} should map to position {expected_pos}"


def test_bitboard_arithmetic_properties():
    """Test mathematical properties of bitboard operations."""
    board = BitBoard.initial()
    
    # Test that occupied = black | white
    assert board.occupied() == (board.black | board.white)
    
    # Test that empty = ~occupied (within 64-bit range)
    full_board = (1 << 64) - 1
    assert board.empty() == (~board.occupied() & full_board)
    
    # Test that black and white don't overlap
    assert (board.black & board.white) == 0
    
    # Test bit counting
    assert bin(board.black).count('1') == 2
    assert bin(board.white).count('1') == 2
    assert bin(board.occupied()).count('1') == 4
    assert bin(board.empty()).count('1') == 60


def test_move_flip_mathematics():
    """Test the mathematical correctness of stone flipping."""
    board = BitBoard.initial()
    move = parse_move("d3")
    
    # Calculate flips manually for verification
    flips = board.flips(move, board.black, board.white)
    
    # For d3 move, should flip d4 (the white stone)
    expected_flip = parse_move("d4")
    assert flips == expected_flip
    
    # Apply move and verify stone counts
    new_board = board.apply_move(move, True)
    
    old_black_count = bin(board.black).count('1')
    old_white_count = bin(board.white).count('1')
    new_black_count = bin(new_board.black).count('1')
    new_white_count = bin(new_board.white).count('1')
    
    # Black should gain 2 stones (1 placed + 1 flipped)
    assert new_black_count == old_black_count + 2
    # White should lose 1 stone (flipped)
    assert new_white_count == old_white_count - 1
    # Total should increase by 1 (new stone placed)
    assert (new_black_count + new_white_count) == (old_black_count + old_white_count) + 1


def test_legal_moves_algorithm_correctness():
    """Test the mathematical correctness of legal move generation."""
    board = BitBoard.initial()
    legal_moves = board.legal_moves(board.black, board.white)
    
    # Manually verify each legal move
    expected_moves = [parse_move(pos) for pos in ["d3", "c4", "f5", "e6"]]
    expected_mask = 0
    for move in expected_moves:
        expected_mask |= move
    
    assert legal_moves == expected_mask
    
    # Verify that each legal move actually flips stones
    for move in expected_moves:
        flips = board.flips(move, board.black, board.white)
        assert flips != 0, f"Legal move should flip at least one stone"


def test_symmetry_preservation():
    """Test that symmetric boards produce symmetric results."""
    # Create horizontally symmetric board
    board = BitBoard.from_ascii(
        """
........
........
........
...WB...
...BW...
........
........
........
"""
    )
    
    # This is the initial board, which is symmetric
    black_moves = board.legal_moves(board.black, board.white)
    
    # Convert moves to coordinate pairs
    moves = []
    temp_mask = black_moves
    while temp_mask:
        lsb = temp_mask & -temp_mask
        pos = 63 - (lsb.bit_length() - 1)
        row, col = divmod(pos, 8)
        moves.append((row, col))
        temp_mask ^= lsb
    
    # Check that for each move (r,c), there's a symmetric move (r, 7-c)
    symmetric_moves = [(r, 7-c) for r, c in moves]
    assert set(moves) == set(symmetric_moves), "Legal moves should be symmetric"


def test_bitwise_operation_consistency():
    """Test consistency of bitwise operations across different scenarios."""
    boards = [
        BitBoard.initial(),
        BitBoard.from_ascii("""
BBBBBBBB
........
........
........
........
........
........
WWWWWWWW
"""),
        BitBoard.from_ascii("""
B.W.B.W.
.W.B.W.B
W.B.W.B.
.B.W.B.W
B.W.B.W.
.W.B.W.B
W.B.W.B.
.B.W.B.W
"""),
    ]
    
    for board in boards:
        # Test De Morgan's laws
        occupied = board.occupied()
        empty = board.empty()
        
        # ~(A | B) = ~A & ~B
        full_mask = (1 << 64) - 1
        assert (~occupied & full_mask) == empty
        
        # Test distributive property: A & (B | C) = (A & B) | (A & C)
        # Using arbitrary mask for testing
        test_mask = 0x0F0F0F0F0F0F0F0F
        left_side = occupied & (board.black | board.white)
        right_side = (occupied & board.black) | (occupied & board.white)
        assert left_side == right_side


def test_boundary_conditions():
    """Test behavior at board boundaries."""
    # Test corner positions
    corners = [
        (0, 0),   # a1
        (0, 7),   # h1
        (7, 0),   # a8
        (7, 7),   # h8
    ]
    
    for row, col in corners:
        bit = 1 << (63 - (row * 8 + col))
        
        # Test all direction shifts from corners
        for direction in DIRS:
            shifted = BitBoard._shift(bit, direction)
            
            # Verify that shifts don't wrap to opposite side
            if shifted != 0:  # If shift produced a result
                shifted_pos = 63 - (shifted.bit_length() - 1)
                shifted_row, shifted_col = divmod(shifted_pos, 8)
                
                # Check that we didn't wrap around
                if direction in ['E', 'NE', 'SE']:
                    assert shifted_col > col or shifted_col == 0, f"Eastward shift wrapped: {direction}"
                if direction in ['W', 'NW', 'SW']:
                    assert shifted_col < col or shifted_col == 7, f"Westward shift wrapped: {direction}"


def test_large_number_arithmetic():
    """Test that 64-bit arithmetic works correctly."""
    # Test with maximum values
    max_64bit = (1 << 64) - 1
    
    # Create full board
    full_black = max_64bit
    full_white = 0
    board = BitBoard(full_black, full_white)
    
    assert board.occupied() == max_64bit
    assert board.empty() == 0
    assert bin(board.occupied()).count('1') == 64
    
    # Test with alternating pattern
    checkerboard = 0x5555555555555555  # Alternating bits
    board2 = BitBoard(checkerboard, ~checkerboard & max_64bit)
    
    assert board2.occupied() == max_64bit
    assert bin(board2.black).count('1') == 32
    assert bin(board2.white).count('1') == 32


def test_performance_critical_operations():
    """Test performance-critical bit operations for correctness."""
    # Test LSB extraction (used frequently in move generation)
    test_values = [0x1, 0x8, 0x100, 0x8000000000000000]
    
    for value in test_values:
        lsb = value & -value
        assert lsb == value, f"LSB extraction failed for {hex(value)}"
    
    # Test bit scanning
    for i in range(64):
        bit = 1 << i
        position = bit.bit_length() - 1
        assert position == i, f"Bit position calculation failed for bit {i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
