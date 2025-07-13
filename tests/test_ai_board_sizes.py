"""Test AI compatibility with different board sizes."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.board import BitBoard, parse_move
from othello.ai import choose_move, _generate_weights, _evaluate


class TestAIBoardSizeCompatibility:
    """Test suite for AI compatibility with different board sizes."""
    
    def test_ai_basic_functionality_4x4(self):
        """Test AI basic functionality on 4x4 board."""
        board = BitBoard.initial(4)
        
        # Test all difficulty levels
        for level in ["easy", "hard", "expert"]:
            # Black's turn
            move = choose_move(board, True, level)
            assert move != 0, f"AI should find a move on 4x4 board (level: {level})"
            
            # Verify move is legal
            legal_moves = board.legal_moves(board.black, board.white)
            assert move & legal_moves, f"AI move should be legal (level: {level})"
    
    def test_ai_basic_functionality_6x6(self):
        """Test AI basic functionality on 6x6 board."""
        board = BitBoard.initial(6)
        
        # Test all difficulty levels
        for level in ["easy", "hard", "expert"]:
            # Black's turn
            move = choose_move(board, True, level)
            assert move != 0, f"AI should find a move on 6x6 board (level: {level})"
            
            # Verify move is legal
            legal_moves = board.legal_moves(board.black, board.white)
            assert move & legal_moves, f"AI move should be legal (level: {level})"
    
    def test_ai_basic_functionality_10x10(self):
        """Test AI basic functionality on 10x10 board."""
        board = BitBoard.initial(10)
        
        # Test all difficulty levels  
        for level in ["easy", "hard", "expert"]:
            # Black's turn
            move = choose_move(board, True, level)
            assert move != 0, f"AI should find a move on 10x10 board (level: {level})"
            
            # Verify move is legal
            legal_moves = board.legal_moves(board.black, board.white)
            assert move & legal_moves, f"AI move should be legal (level: {level})"
    
    def test_weight_generation_different_sizes(self):
        """Test that weight generation works for different board sizes."""
        sizes = [4, 6, 8, 10, 12]
        
        for size in sizes:
            weights = _generate_weights(size)
            
            # Check correct length
            assert len(weights) == size * size, f"Weights should have {size*size} elements for {size}x{size} board"
            
            # Check corner values are high
            corners = [0, size - 1, size * (size - 1), size * size - 1]  # Top-left, top-right, bottom-left, bottom-right
            for corner in corners:
                assert weights[corner] == 100, f"Corner {corner} should have value 100 on {size}x{size} board"
    
    def test_evaluation_function_different_sizes(self):
        """Test that board evaluation works for different sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Should not crash and return reasonable values
            score = _evaluate(board)
            assert isinstance(score, int), f"Evaluation should return integer for {size}x{size} board"
            
            # Initial position should be roughly balanced (score close to 0)
            assert abs(score) < 200, f"Initial position should be roughly balanced for {size}x{size} board, got {score}"
    
    def test_ai_performance_stress_test(self):
        """Test AI performance under different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Make several moves to test mid-game performance
            for _ in range(min(size, 6)):  # Limit moves based on size
                try:
                    # Try expert level (most computationally intensive)
                    move = choose_move(board, True, "expert")
                    if move == 0:
                        break  # No legal moves
                    
                    # Apply the move
                    board = board.apply_move(move, True)
                    
                    # Switch players for next iteration 
                    board_white_move = choose_move(board, False, "expert")
                    if board_white_move == 0:
                        break  # No legal moves
                    
                    board = board.apply_move(board_white_move, False)
                    
                except Exception as e:
                    pytest.fail(f"AI failed on {size}x{size} board: {e}")
    
    def test_opening_book_graceful_fallback(self):
        """Test that opening book gracefully falls back for non-8x8 boards."""
        # Opening book only works for 8x8, should not crash for other sizes
        sizes = [4, 6, 10, 12]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Should not crash when consulting opening book
            move = choose_move(board, True, "expert")
            assert move != 0, f"AI should find move without opening book on {size}x{size} board"
            
            # Verify it's a legal move
            legal_moves = board.legal_moves(board.black, board.white)
            assert move & legal_moves, f"AI move should be legal without opening book on {size}x{size} board"
    
    def test_parse_move_compatibility(self):
        """Test that parse_move works correctly with different board sizes."""
        # Test coordinate parsing for different sizes
        test_cases = [
            (4, "a1", 0),  # Top-left corner
            (4, "d4", 15), # Bottom-right corner
            (6, "a1", 0),
            (6, "f6", 35),
            (8, "a1", 0),
            (8, "h8", 63),
            (10, "a1", 0),
            (10, "j10", 99),
        ]
        
        for size, move_str, expected_bit_position in test_cases:
            move_bit = parse_move(move_str, size)
            
            # Convert bit to position to verify
            total_squares = size * size
            bit_position = move_bit.bit_length() - 1
            array_index = total_squares - 1 - bit_position
            
            assert array_index == expected_bit_position, f"Move {move_str} on {size}x{size} board should map to position {expected_bit_position}, got {array_index}"
    
    def test_weight_caching(self):
        """Test that weight caching works correctly."""
        # Clear cache first by accessing _weight_cache
        from othello.ai import _weight_cache
        _weight_cache.clear()
        
        # Generate weights for a size
        weights1 = _generate_weights(6)
        weights2 = _generate_weights(6)
        
        # Should be the same object (cached)
        assert weights1 is weights2, "Weights should be cached and return same object"
        
        # Different sizes should be different objects
        weights_8 = _generate_weights(8)
        assert weights1 is not weights_8, "Different sizes should have different weight objects"
    
    def test_ai_no_legal_moves_handling(self):
        """Test AI behavior when no legal moves are available."""
        # Create a board state with no legal moves for black
        # This is a contrived example but tests the edge case
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            # Create a board where all edges are filled (contrived scenario)
            black = 0
            white = 0
            
            # Fill some positions to create a scenario with potentially no moves
            total = size * size
            for i in range(min(total // 2, 10)):  # Fill some arbitrary positions
                bit = 1 << (total - 1 - i)
                if i % 2 == 0:
                    black |= bit
                else:
                    white |= bit
            
            board = BitBoard(black, white, size)
            
            # Even if no legal moves, AI should return 0 gracefully
            move = choose_move(board, True, "expert")
            legal_moves = board.legal_moves(board.black, board.white)
            
            if legal_moves == 0:
                assert move == 0, f"AI should return 0 when no legal moves on {size}x{size} board"
            else:
                assert move & legal_moves, f"AI move should be legal if legal moves exist on {size}x{size} board"


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running AI board size compatibility tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All AI board size compatibility tests passed!")
    else:
        print("❌ Some AI board size compatibility tests failed!")
        sys.exit(1)