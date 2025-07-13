"""Test AI edge cases and potential compatibility issues."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.board import BitBoard, parse_move
from othello.ai import choose_move, _generate_weights, _evaluate


class TestAIEdgeCases:
    """Test AI edge cases and compatibility issues."""
    
    def test_extreme_board_sizes(self):
        """Test AI with extreme board sizes (minimum and large)."""
        # Test minimum size (4x4)
        board_4x4 = BitBoard.initial(4)
        for level in ["easy", "hard", "expert"]:
            move = choose_move(board_4x4, True, level)
            legal = board_4x4.legal_moves(board_4x4.black, board_4x4.white)
            if legal != 0:  # If there are legal moves
                assert move & legal, f"AI move should be legal on 4x4 board (level: {level})"
        
        # Test large size (16x16)
        board_16x16 = BitBoard.initial(16)
        for level in ["easy", "hard", "expert"]:
            move = choose_move(board_16x16, True, level)
            legal = board_16x16.legal_moves(board_16x16.black, board_16x16.white)
            if legal != 0:  # If there are legal moves
                assert move & legal, f"AI move should be legal on 16x16 board (level: {level})"
    
    def test_weight_generation_edge_cases(self):
        """Test weight generation for edge cases."""
        # Test minimum size
        weights_4 = _generate_weights(4)
        assert len(weights_4) == 16
        assert weights_4[0] == 100  # Corner
        assert weights_4[3] == 100  # Corner
        assert weights_4[12] == 100  # Corner  
        assert weights_4[15] == 100  # Corner
        
        # Test larger odd-ish scenarios
        weights_6 = _generate_weights(6)
        assert len(weights_6) == 36
        assert weights_6[0] == 100  # Top-left corner
        assert weights_6[5] == 100  # Top-right corner
        assert weights_6[30] == 100  # Bottom-left corner
        assert weights_6[35] == 100  # Bottom-right corner
    
    def test_evaluation_consistency(self):
        """Test that evaluation function is consistent across board sizes."""
        sizes = [4, 6, 8, 10, 12]
        
        for size in sizes:
            board = BitBoard.initial(size)
            
            # Test evaluation doesn't crash
            score = _evaluate(board)
            assert isinstance(score, int)
            
            # Test evaluation symmetry - initial position should be close to 0
            # (both players have equal positions)
            assert abs(score) < 200, f"Initial position should be roughly balanced on {size}x{size}, got {score}"
    
    def test_weight_caching_robustness(self):
        """Test that weight caching handles multiple sizes correctly."""
        from othello.ai import _weight_cache
        
        # Clear cache
        _weight_cache.clear()
        
        # Generate weights for multiple sizes
        sizes = [4, 6, 8, 10, 12]
        weight_objects = []
        
        for size in sizes:
            weights = _generate_weights(size)
            weight_objects.append(weights)
            
            # Verify cache contains this size
            assert size in _weight_cache
            assert _weight_cache[size] is weights
        
        # Verify all sizes are cached correctly
        for i, size in enumerate(sizes):
            cached_weights = _generate_weights(size)
            assert cached_weights is weight_objects[i], f"Cache should return same object for size {size}"
    
    def test_ai_with_near_full_boards(self):
        """Test AI behavior with nearly full boards of different sizes."""
        sizes = [4, 6, 8]
        
        for size in sizes:
            # Create a board that's nearly full
            total = size * size
            black = 0
            white = 0
            
            # Fill most squares, leaving a few empty
            empty_squares = 4
            for i in range(total - empty_squares):
                bit = 1 << (total - 1 - i)
                if i % 2 == 0:
                    black |= bit
                else:
                    white |= bit
            
            board = BitBoard(black, white, size)
            
            # AI should handle near-full boards gracefully
            for level in ["easy", "hard", "expert"]:
                move = choose_move(board, True, level)
                legal = board.legal_moves(board.black, board.white)
                
                if legal == 0:
                    assert move == 0, f"AI should return 0 when no legal moves on nearly full {size}x{size} board"
                else:
                    assert move & legal, f"AI should choose legal move on nearly full {size}x{size} board (level: {level})"
    
    def test_opening_book_size_handling(self):
        """Test that opening book only applies to 8x8 boards."""
        # The opening book should only be consulted for 8x8 boards
        # For other sizes, AI should work without opening book
        
        non_8x8_sizes = [4, 6, 10, 12]
        
        for size in non_8x8_sizes:
            board = BitBoard.initial(size)
            
            # Expert level should work without opening book
            move = choose_move(board, True, "expert")
            legal = board.legal_moves(board.black, board.white)
            
            assert move != 0, f"AI should find move without opening book on {size}x{size} board"
            assert move & legal, f"AI move should be legal without opening book on {size}x{size} board"
    
    def test_bit_manipulation_correctness(self):
        """Test that bit manipulation works correctly for different board sizes."""
        sizes = [4, 6, 8, 10, 12]
        
        for size in sizes:
            # Test parse_move for corners and center
            total = size * size
            
            # Test corner moves
            corner_moves = [
                ("a1", 0),  # Top-left
                (f"{chr(ord('a') + size - 1)}1", size - 1),  # Top-right
                (f"a{size}", (size - 1) * size),  # Bottom-left
                (f"{chr(ord('a') + size - 1)}{size}", total - 1),  # Bottom-right
            ]
            
            for move_str, expected_position in corner_moves:
                try:
                    move_bit = parse_move(move_str, size)
                    bit_position = move_bit.bit_length() - 1
                    array_index = total - 1 - bit_position
                    
                    assert array_index == expected_position, f"Move {move_str} on {size}x{size} should map to position {expected_position}, got {array_index}"
                except (ValueError, IndexError) as e:
                    pytest.fail(f"Failed to parse move {move_str} on {size}x{size} board: {e}")
    
    def test_ai_consistency_across_levels(self):
        """Test that AI levels are consistent across different board sizes."""
        sizes = [4, 6, 8, 10]
        
        for size in sizes:
            board = BitBoard.initial(size)
            legal = board.legal_moves(board.black, board.white)
            
            if legal == 0:
                continue  # Skip if no legal moves
            
            # All levels should return legal moves
            for level in ["easy", "hard", "expert"]:
                move = choose_move(board, True, level)
                assert move & legal, f"AI level {level} should choose legal move on {size}x{size} board"
            
            # Easy should pick any legal move (random)
            easy_move = choose_move(board, True, "easy")
            assert easy_move & legal
            
            # Hard should pick a move (greedy strategy)
            hard_move = choose_move(board, True, "hard")
            assert hard_move & legal
            
            # Expert should pick a move (positional strategy)
            expert_move = choose_move(board, True, "expert")
            assert expert_move & legal


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running AI edge case tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All AI edge case tests passed!")
    else:
        print("❌ Some AI edge case tests failed!")
        sys.exit(1)