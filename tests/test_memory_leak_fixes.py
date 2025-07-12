"""Tests for memory leak fixes in Game class history management."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.game import Game
from othello.board import BitBoard, parse_move


class TestMemoryLeakFixes:
    """Test suite for memory usage improvements in Game class."""
    
    def test_history_bounded_on_moves(self):
        """Test that history is bounded during normal gameplay."""
        game = Game(max_history_size=5)  # Small limit for testing
        
        # Initial state counts as 1 history entry
        assert len(game.history) == 1
        
        # Apply more moves than the history limit
        moves = ['d3', 'c3', 'e3', 'f3', 'c4', 'b4', 'e4', 'f4']
        board_size = game.board.size
        
        for move_str in moves:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                game.black_to_move = not game.black_to_move
                continue
                
            try:
                move = parse_move(move_str, board_size)
                if move & legal_moves:  # Only apply legal moves
                    game.apply_move(move)
            except ValueError:
                continue  # Skip illegal moves
        
        # History should be bounded to max_history_size
        assert len(game.history) <= game.max_history_size
        
    def test_future_bounded_on_undos(self):
        """Test that future stack is bounded during undo operations."""
        game = Game(max_future_size=3)  # Small limit for testing
        
        # Apply several moves first
        moves = ['d3', 'c3', 'e3', 'f3', 'c4']
        board_size = game.board.size
        
        for move_str in moves:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                game.black_to_move = not game.black_to_move
                continue
                
            try:
                move = parse_move(move_str, board_size)
                if move & legal_moves:
                    game.apply_move(move)
            except ValueError:
                continue
        
        # Perform more undos than the future limit
        undo_count = 0
        while game.undo() and undo_count < 10:  # Try many undos
            undo_count += 1
        
        # Future stack should be bounded
        assert len(game.future) <= game.max_future_size
        
    def test_memory_usage_stress_test(self):
        """Stress test for memory usage with many moves and undos."""
        game = Game(max_history_size=50, max_future_size=25)
        
        # Simulate a long game with many moves
        move_count = 0
        max_moves = 200  # Attempt many more moves than history limit
        
        while move_count < max_moves:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                game.black_to_move = not game.black_to_move
                legal_moves = game.legal_moves()
                if legal_moves == 0:
                    break  # Game over
            
            # Take the first legal move
            move = legal_moves & -legal_moves  # Get lowest set bit
            try:
                game.apply_move(move)
                move_count += 1
            except ValueError:
                break  # No more legal moves
            
            # Occasionally undo to test future stack
            if move_count % 10 == 0:
                game.undo()
                game.undo()  # Undo twice
        
        # Verify bounds are respected
        assert len(game.history) <= game.max_history_size
        assert len(game.future) <= game.max_future_size
        
    def test_configuration_parameters(self):
        """Test that configuration parameters work correctly."""
        # Test custom limits
        game1 = Game(max_history_size=20, max_future_size=10)
        assert game1.max_history_size == 20
        assert game1.max_future_size == 10
        
        # Test default limits
        game2 = Game()
        assert game2.max_history_size == 100
        assert game2.max_future_size == 50
        
    def test_undo_redo_functionality_preserved(self):
        """Test that undo/redo still works correctly with bounds."""
        game = Game(max_history_size=10, max_future_size=5)
        
        # Apply some moves
        moves = ['d3', 'c3', 'e3']
        board_size = game.board.size
        
        for move_str in moves:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                continue
            try:
                move = parse_move(move_str, board_size)
                if move & legal_moves:
                    game.apply_move(move)
            except ValueError:
                continue
        
        initial_history_len = len(game.history)
        
        # Test undo
        assert game.undo() == True
        assert len(game.history) == initial_history_len - 1
        assert len(game.future) == 1
        
        # Test redo
        assert game.redo() == True
        assert len(game.history) == initial_history_len
        assert len(game.future) == 0
        
    def test_edge_cases_history_bounds(self):
        """Test edge cases for history bounding."""
        # Very small history limit
        game = Game(max_history_size=1)
        
        # Should always have at least 1 entry for undo to work
        assert len(game.history) == 1
        
        # Apply a move
        legal_moves = game.legal_moves()
        if legal_moves != 0:
            move = legal_moves & -legal_moves
            game.apply_move(move)
            
            # Should still have exactly max_history_size entries
            assert len(game.history) == game.max_history_size
            
    def test_edge_cases_future_bounds(self):
        """Test edge cases for future stack bounding."""
        game = Game(max_future_size=1)
        
        # Apply some moves
        for _ in range(3):
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                break
            move = legal_moves & -legal_moves
            try:
                game.apply_move(move)
            except ValueError:
                break
        
        # Undo multiple times
        game.undo()
        game.undo()
        
        # Future should be bounded
        assert len(game.future) <= game.max_future_size
        
    def test_no_memory_leak_on_branch_after_undo(self):
        """Test that making moves after undo doesn't cause memory issues."""
        game = Game(max_history_size=5, max_future_size=3)
        
        # Apply moves, undo, then apply different moves (branching)
        moves1 = ['d3', 'c3', 'e3']
        board_size = game.board.size
        
        for move_str in moves1:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                continue
            try:
                move = parse_move(move_str, board_size)
                if move & legal_moves:
                    game.apply_move(move)
            except ValueError:
                continue
        
        # Undo some moves
        game.undo()
        game.undo()
        
        # Apply different moves (this should clear future and branch)
        moves2 = ['f3', 'c4', 'b4']
        for move_str in moves2:
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                continue
            try:
                move = parse_move(move_str, board_size)
                if move & legal_moves:
                    game.apply_move(move)
            except ValueError:
                continue
        
        # Future should be cleared after branching
        assert len(game.future) == 0
        # History should still be bounded
        assert len(game.history) <= game.max_history_size
        
    def test_memory_bounds_with_passes(self):
        """Test memory bounds work correctly with pass moves."""
        game = Game(max_history_size=5)
        
        # Force a position where passes might occur
        # Apply moves until we get a pass situation
        move_count = 0
        while move_count < 20:  # Limit iterations
            legal_moves = game.legal_moves()
            if legal_moves == 0:
                # Pass - switch players but don't add to history
                game.black_to_move = not game.black_to_move
                legal_moves = game.legal_moves()
                if legal_moves == 0:
                    break  # Game over - both players pass
            else:
                move = legal_moves & -legal_moves
                try:
                    game.apply_move(move)
                    move_count += 1
                except ValueError:
                    break
        
        # Verify bounds regardless of passes
        assert len(game.history) <= game.max_history_size


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running memory leak fix tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All memory leak fix tests passed!")
    else:
        print("❌ Some memory tests failed!")
        sys.exit(1)