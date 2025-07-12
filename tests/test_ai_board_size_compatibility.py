"""Tests for AI module board size compatibility."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.ai import choose_move, _generate_weights, _evaluate
from othello.board import BitBoard


class TestAIBoardSizeCompatibility:
    """Test suite for AI module board size compatibility."""
    
    def test_generate_weights_different_sizes(self):
        """Test weight generation for various board sizes."""
        test_sizes = [4, 6, 8, 10, 12]
        
        for size in test_sizes:
            weights = _generate_weights(size)
            
            # Verify correct number of weights
            assert len(weights) == size * size
            
            # Verify corners have highest value (100)
            corners = [0, size - 1, (size - 1) * size, size * size - 1]
            for corner_idx in corners:
                assert weights[corner_idx] == 100, f"Corner {corner_idx} should have weight 100"
            
            # Verify weights are cached
            cached_weights = _generate_weights(size)
            assert weights is cached_weights, "Weights should be cached"
    
    def test_generate_weights_8x8_matches_original(self):
        """Test that 8x8 weights use the original design exactly."""
        from othello.ai import _DEFAULT_WEIGHTS_8X8
        weights = _generate_weights(8)
        
        # Should use the original weights exactly for 8x8
        assert weights == _DEFAULT_WEIGHTS_8X8
        
        # Verify key strategic positions from original design
        assert weights[0] == 100   # Top-left corner
        assert weights[7] == 100   # Top-right corner
        assert weights[56] == 100  # Bottom-left corner  
        assert weights[63] == 100  # Bottom-right corner
        assert weights[1] == -20   # Adjacent to corner
        assert weights[9] == -50   # Diagonal to corner
        
    def test_evaluate_with_different_board_sizes(self):
        """Test evaluation function works with different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Should not raise errors
            score = _evaluate(board)
            
            # Initial position should have neutral or slightly positive score
            # (depends on specific weight distribution)
            assert isinstance(score, int)
            assert -200 <= score <= 200  # Reasonable range for initial position
    
    def test_choose_move_easy_different_sizes(self):
        """Test easy AI works with different board sizes."""
        sizes = [4, 6, 8, 10, 12]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Test black move
            move = choose_move(board, True, "easy")
            legal_moves = board.legal_moves(board.black, board.white)
            
            if legal_moves != 0:
                assert move != 0, f"Should return a move for size {size}"
                assert move & legal_moves, f"Move should be legal for size {size}"
            else:
                assert move == 0, f"Should return 0 when no legal moves for size {size}"
    
    def test_choose_move_hard_different_sizes(self):
        """Test hard AI works with different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Test both players
            for black_to_move in [True, False]:
                move = choose_move(board, black_to_move, "hard")
                player = board.black if black_to_move else board.white
                opponent = board.white if black_to_move else board.black
                legal_moves = board.legal_moves(player, opponent)
                
                if legal_moves != 0:
                    assert move != 0, f"Hard AI should return move for size {size}"
                    assert move & legal_moves, f"Hard AI move should be legal for size {size}"
                else:
                    assert move == 0, f"Hard AI should return 0 when no moves for size {size}"
    
    def test_choose_move_expert_different_sizes(self):
        """Test expert AI works with different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Test both players
            for black_to_move in [True, False]:
                move = choose_move(board, black_to_move, "expert")
                player = board.black if black_to_move else board.white
                opponent = board.white if black_to_move else board.black
                legal_moves = board.legal_moves(player, opponent)
                
                if legal_moves != 0:
                    assert move != 0, f"Expert AI should return move for size {size}"
                    assert move & legal_moves, f"Expert AI move should be legal for size {size}"
                else:
                    assert move == 0, f"Expert AI should return 0 when no moves for size {size}"
    
    def test_opening_book_only_for_8x8(self):
        """Test that opening book is only used for 8x8 boards."""
        # For 8x8, opening book might be consulted
        board_8x8 = BitBoard.initial(8)
        move_8x8 = choose_move(board_8x8, True, "expert")
        
        # For other sizes, should work without opening book
        board_6x6 = BitBoard.initial(6)
        move_6x6 = choose_move(board_6x6, True, "expert")
        
        # Both should return valid moves
        legal_8x8 = board_8x8.legal_moves(board_8x8.black, board_8x8.white)
        legal_6x6 = board_6x6.legal_moves(board_6x6.black, board_6x6.white)
        
        assert move_8x8 & legal_8x8, "8x8 move should be legal"
        assert move_6x6 & legal_6x6, "6x6 move should be legal"
    
    def test_weight_generation_strategic_principles(self):
        """Test that weight generation follows strategic principles."""
        for size in [4, 6, 10, 12]:
            weights = _generate_weights(size)
            
            # Corners should be highest
            corners = [0, size - 1, (size - 1) * size, size * size - 1]
            for corner in corners:
                assert weights[corner] == 100
            
            # Squares adjacent to corners should be penalized (negative)
            if size >= 4:
                # Adjacent to top-left corner
                adjacent_indices = []
                if size > 2:
                    adjacent_indices.extend([1, size, size + 1])  # Right, below, diagonal
                
                for adj_idx in adjacent_indices:
                    if adj_idx < len(weights):
                        assert weights[adj_idx] < 0, f"Adjacent square {adj_idx} should be penalized"
    
    def test_ai_consistency_across_sizes(self):
        """Test that AI behavior is consistent across different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # All difficulty levels should work
            for level in ["easy", "hard", "expert"]:
                move = choose_move(board, True, level)
                legal_moves = board.legal_moves(board.black, board.white)
                
                if legal_moves != 0:
                    assert move & legal_moves, f"{level} AI move should be legal for size {size}"
                    
                    # Expert should consider position
                    if level == "expert":
                        # Apply move and verify board state changes
                        next_board = board.apply_move(move, True)
                        assert next_board != board, "Move should change board state"
    
    def test_edge_cases_board_sizes(self):
        """Test AI with edge case board sizes."""
        # Test minimum size (4x4)
        board_4x4 = BitBoard.initial(4)
        move = choose_move(board_4x4, True, "expert")
        legal = board_4x4.legal_moves(board_4x4.black, board_4x4.white)
        
        if legal != 0:
            assert move & legal, "4x4 move should be legal"
        
        # Test larger size (14x14)
        board_14x14 = BitBoard.initial(14)
        move = choose_move(board_14x14, True, "expert")
        legal = board_14x14.legal_moves(board_14x14.black, board_14x14.white)
        
        if legal != 0:
            assert move & legal, "14x14 move should be legal"
    
    def test_performance_large_boards(self):
        """Test that AI performance is reasonable for large boards."""
        import time
        
        # Test with larger board
        board = BitBoard.initial(12)
        
        start_time = time.time()
        move = choose_move(board, True, "expert")
        end_time = time.time()
        
        # Should complete within reasonable time (1 second)
        assert end_time - start_time < 1.0, "AI should be reasonably fast"
        
        # Move should still be legal
        legal_moves = board.legal_moves(board.black, board.white)
        if legal_moves != 0:
            assert move & legal_moves, "Move should be legal even for large boards"


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
        print("❌ Some AI compatibility tests failed!")
        sys.exit(1)