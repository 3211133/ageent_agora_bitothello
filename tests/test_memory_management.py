"""Memory management tests for game history system."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.game import Game
from othello.board import BitBoard, parse_move


class TestMemoryManagement:
    """Test suite for memory management in game history system."""
    
    def test_default_memory_limits(self):
        """Test that default memory limits are set correctly."""
        game = Game()
        assert game.max_history_size == 100
        assert game.max_future_size == 50
    
    def test_custom_memory_limits(self):
        """Test creating game with custom memory limits."""
        game = Game(max_history_size=50, max_future_size=25)
        assert game.max_history_size == 50
        assert game.max_future_size == 25
    
    def test_history_size_limiting(self):
        """Test that history size is limited to prevent memory leaks."""
        # Create game with small history limit for testing
        game = Game(max_history_size=5)
        
        # Make more moves than the history limit
        moves = ['d3', 'c3', 'd2', 'c4', 'e3', 'f3', 'g3', 'h3', 'b3', 'a3']
        
        for move_str in moves:
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
            except ValueError:
                # Skip invalid moves
                continue
        
        # History should be limited to max_history_size
        assert len(game.history) <= game.max_history_size
        # Should still have at least one entry for undo functionality
        assert len(game.history) >= 1
    
    def test_future_stack_size_limiting(self):
        """Test that future stack size is limited to prevent memory leaks."""
        # Create game with small limits for testing
        game = Game(max_history_size=20, max_future_size=3)
        
        # Make several moves to build history
        moves = ['d3', 'c3', 'd2', 'c4', 'e3', 'f3']
        for move_str in moves:
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
            except ValueError:
                continue
        
        # Perform many undos to test future stack limiting
        undo_count = 0
        while game.undo() and undo_count < 10:
            undo_count += 1
        
        # Future stack should be limited to max_future_size
        assert len(game.future) <= game.max_future_size
    
    def test_memory_bounds_under_stress(self):
        """Test memory bounds under stress conditions (many moves and undos)."""
        game = Game(max_history_size=10, max_future_size=5)
        
        # Simulate a long game with many moves
        moves = ['d3', 'c3', 'd2', 'c4', 'e3', 'f3', 'g3', 'c2', 'b3', 'a3',
                'b2', 'a2', 'e2', 'f2', 'g2', 'h2', 'd1', 'c1', 'b1', 'a1']
        
        for move_str in moves:
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
                    
                    # Verify memory bounds after each move
                    assert len(game.history) <= game.max_history_size
                    assert len(game.future) <= game.max_future_size
                    
            except ValueError:
                # Skip invalid moves
                continue
        
        # Perform alternating undos and redos to stress test
        for _ in range(20):
            if game.history and len(game.history) > 1:
                game.undo()
                assert len(game.future) <= game.max_future_size
            if game.future:
                game.redo()
                assert len(game.history) <= game.max_history_size
    
    def test_undo_redo_functionality_preserved(self):
        """Test that undo/redo functionality still works with memory limits."""
        game = Game(max_history_size=5, max_future_size=3)
        
        # Make some moves
        initial_board = game.board
        moves = ['d3', 'c3', 'd2']
        
        for move_str in moves:
            move = parse_move(move_str)
            if move & game.legal_moves():
                game.apply_move(move)
        
        current_board = game.board
        
        # Test undo
        undo_success = game.undo()
        assert undo_success
        assert game.board != current_board
        
        # Test redo
        redo_success = game.redo()
        assert redo_success
        assert game.board == current_board
    
    def test_memory_cleanup_on_new_moves_after_undo(self):
        """Test that future stack is cleared when making new moves after undo."""
        game = Game()
        
        # Make moves to build history
        moves = ['d3', 'c3', 'd2']
        for move_str in moves:
            move = parse_move(move_str)
            if move & game.legal_moves():
                game.apply_move(move)
        
        # Record state before undos
        history_before_undo = len(game.history)
        
        # Undo to populate future stack
        game.undo()
        game.undo()
        assert len(game.future) > 0
        
        # Make a new valid move - should clear future stack
        # Try different moves to find a legal one
        test_moves = ['e3', 'c4', 'b3', 'f3', 'e2', 'c1']
        move_applied = False
        
        for move_str in test_moves:
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
                    move_applied = True
                    break
            except ValueError:
                continue
        
        # Only test future clearing if we successfully applied a move
        if move_applied:
            assert len(game.future) == 0
    
    def test_history_preservation_with_limits(self):
        """Test that essential history is preserved even with limits."""
        game = Game(max_history_size=3)
        
        # Make moves that exceed history limit
        moves = ['d3', 'c3', 'd2', 'c4', 'e3', 'f3']
        valid_moves = 0
        
        for move_str in moves:
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
                    valid_moves += 1
            except ValueError:
                continue
        
        # Should still be able to undo at least once
        if valid_moves > 0:
            assert game.undo()
            assert len(game.history) >= 1
    
    def test_memory_efficient_long_game(self):
        """Test memory efficiency during a long game simulation."""
        game = Game(max_history_size=20, max_future_size=10)
        
        # Simulate many moves (would cause unbounded growth without limits)
        move_count = 0
        max_moves = 100  # Simulate very long game
        
        possible_moves = []
        for row in range(1, 9):
            for col in 'abcdefgh':
                possible_moves.append(f'{col}{row}')
        
        for i in range(max_moves):
            move_str = possible_moves[i % len(possible_moves)]
            try:
                move = parse_move(move_str)
                if move & game.legal_moves():
                    game.apply_move(move)
                    move_count += 1
                    
                    # Memory should stay bounded regardless of game length
                    assert len(game.history) <= game.max_history_size
                    assert len(game.future) <= game.max_future_size
                    
            except ValueError:
                continue
            
            # Occasionally test undo to build future stack
            if i % 10 == 0 and len(game.history) > 1:
                game.undo()
                assert len(game.future) <= game.max_future_size
    
    def test_zero_limits_edge_case(self):
        """Test edge case behavior with very small limits."""
        # Test with minimal limits (edge case)
        game = Game(max_history_size=1, max_future_size=1)
        
        # Should still maintain basic functionality
        move = parse_move('d3')
        if move & game.legal_moves():
            game.apply_move(move)
        
        # History should have at least initial state
        assert len(game.history) >= 1
        assert len(game.history) <= game.max_history_size
    
    def test_large_limits_normal_operation(self):
        """Test that large limits don't interfere with normal operation."""
        game = Game(max_history_size=1000, max_future_size=500)
        
        # Normal game operations should work identically
        move = parse_move('d3')
        if move & game.legal_moves():
            initial_history_len = len(game.history)
            game.apply_move(move)
            assert len(game.history) == initial_history_len + 1
        
        # Undo should work normally
        if len(game.history) > 1:
            game.undo()
            assert len(game.future) == 1


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running memory management tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All memory management tests passed!")
    else:
        print("❌ Some memory management tests failed!")
        sys.exit(1)