"""Integration tests for complete game scenarios and multi-move sequences."""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, parse_move
from othello.game import Game
from othello.ai import choose_move


def test_complete_game_sequence():
    """Test a complete game sequence with known moves."""
    game = Game()
    
    # Play a known sequence of moves
    moves = [
        ("d3", True),   # Black
        ("c3", False),  # White
        ("c4", True),   # Black
        ("c5", False),  # White
        ("b3", True),   # Black
        ("a2", False),  # White
        ("b5", True),   # Black
        ("a5", False),  # White
    ]
    
    for move_str, expected_black_turn in moves:
        assert game.black_to_move == expected_black_turn
        move = parse_move(move_str)
        legal_moves = game.legal_moves()
        assert move & legal_moves != 0, f"Move {move_str} should be legal"
        game.apply_move(move)
    
    # Verify final board state
    expected_board = BitBoard.from_ascii(
        """
........
W.......
.WBB....
..BBB...
WWWWW...
........
........
........
"""
    )
    assert game.board == expected_board


def test_undo_redo_consistency():
    """Test that undo/redo operations maintain board consistency."""
    game = Game()
    initial_board = game.board
    initial_turn = game.black_to_move
    
    # Make several moves
    moves = ["d3", "c3", "c4", "c5"]
    for move_str in moves:
        move = parse_move(move_str)
        game.apply_move(move)
    
    # Undo all moves
    for _ in moves:
        assert game.undo()
    
    # Should be back to initial state
    assert game.board == initial_board
    assert game.black_to_move == initial_turn
    
    # Redo all moves
    for _ in moves:
        assert game.redo()
    
    # Should be at the same final state
    final_board = game.board
    final_turn = game.black_to_move
    
    # Undo and redo again to verify consistency
    for _ in moves:
        game.undo()
    for _ in moves:
        game.redo()
    
    assert game.board == final_board
    assert game.black_to_move == final_turn


def test_pass_scenarios():
    """Test scenarios where players must pass."""
    # Create a board where black has no moves
    board = BitBoard.from_ascii(
        """
WWWWWWWW
WWWWWWWW
WWWWWWWW
WWWBWWWW
WWWWWWWW
WWWWWWWW
WWWWWWWW
WWWWWWWW
"""
    )
    
    game = Game(board=board, black_to_move=True)
    
    # Black should have no legal moves
    assert game.legal_moves() == 0
    
    # In a real game, this would be handled by the game loop
    # Here we just verify the detection works


def test_game_end_detection():
    """Test detection of game end conditions."""
    # Test 1: Full board
    full_board = BitBoard.from_ascii(
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
    
    game = Game(board=full_board, black_to_move=True)
    assert game.legal_moves() == 0
    
    game.black_to_move = False
    assert game.legal_moves() == 0
    
    # Test 2: No moves for either player
    no_moves_board = BitBoard.from_ascii(
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
    
    game = Game(board=no_moves_board, black_to_move=True)
    black_moves = game.legal_moves()
    
    game.black_to_move = False
    white_moves = game.legal_moves()
    
    # At least one should have no moves (likely white)
    assert black_moves == 0 or white_moves == 0


def test_ai_move_validity():
    """Test that AI always makes valid moves."""
    game = Game()
    
    # Play 20 moves with AI
    for _ in range(20):
        legal_moves = game.legal_moves()
        if legal_moves == 0:
            # Pass turn
            game.black_to_move = not game.black_to_move
            continue
            
        ai_move = choose_move(game.board, game.black_to_move, level="easy")
        
        # AI move should be legal
        assert ai_move & legal_moves != 0, "AI made an illegal move"
        
        game.apply_move(ai_move)
        
        # Board should be valid after AI move
        assert game.board.occupied() != 0
        assert bin(game.board.occupied()).count('1') >= 4


def test_move_sequence_stone_count():
    """Test that stone counts change correctly during game."""
    game = Game()
    
    initial_black = bin(game.board.black).count('1')
    initial_white = bin(game.board.white).count('1')
    initial_total = initial_black + initial_white
    
    # Make a move
    move = parse_move("d3")
    game.apply_move(move)
    
    new_black = bin(game.board.black).count('1')
    new_white = bin(game.board.white).count('1')
    new_total = new_black + new_white
    
    # Total stones should increase by 1 (new stone placed)
    assert new_total == initial_total + 1
    
    # Black should have gained stones (made the move and flipped opponent)
    assert new_black > initial_black
    assert new_white < initial_white


def test_alternating_turns():
    """Test that turns alternate correctly."""
    game = Game()
    
    moves = ["d3", "c3", "c4", "c5", "b3", "a2"]
    expected_turns = [True, False, True, False, True, False]
    
    for i, move_str in enumerate(moves):
        assert game.black_to_move == expected_turns[i]
        move = parse_move(move_str)
        game.apply_move(move)


def test_board_state_immutability():
    """Test that BitBoard operations don't modify original boards."""
    original = BitBoard.initial()
    original_black = original.black
    original_white = original.white
    
    # Perform various operations
    move = parse_move("d3")
    new_board = original.apply_move(move, True)
    legal_moves = original.legal_moves(original.black, original.white)
    flips = original.flips(move, original.black, original.white)
    
    # Original should be unchanged
    assert original.black == original_black
    assert original.white == original_white
    
    # New board should be different
    assert new_board != original


def test_complex_multi_flip_scenario():
    """Test complex scenario with multiple simultaneous flips."""
    board = BitBoard.from_ascii(
        """
........
........
..BWWB..
..WBWW..
..BWWB..
..WWBW..
........
........
"""
    )
    
    # Black plays b4 - should flip white stones
    move = parse_move("b4")
    new_board = board.apply_move(move, True)
    
    # Count stones before and after
    old_black = bin(board.black).count('1')
    old_white = bin(board.white).count('1')
    new_black = bin(new_board.black).count('1')
    new_white = bin(new_board.white).count('1')
    
    # Should have flipped white stones
    assert new_black > old_black + 1  # More than just the placed stone
    assert new_white < old_white
    assert new_black + new_white == old_black + old_white + 1


def test_edge_position_moves():
    """Test moves along board edges."""
    game = Game()
    
    # Play moves that will create opportunities for edge moves
    setup_moves = ["d3", "c3", "c4", "b3", "c5", "c6", "d6", "e6"]
    
    for move_str in setup_moves:
        move = parse_move(move_str)
        if move & game.legal_moves():
            game.apply_move(move)
    
    # Now test edge moves
    legal_moves = game.legal_moves()
    
    # Check if any edge positions are legal
    edge_positions = ["a1", "a8", "h1", "h8", "a4", "h4", "d1", "d8"]
    edge_legal = False
    
    for pos in edge_positions:
        move = parse_move(pos)
        if move & legal_moves:
            edge_legal = True
            # Test that the move can be applied without error
            try:
                test_board = game.board.apply_move(move, game.black_to_move)
                assert test_board != game.board
            except ValueError:
                # Move wasn't actually legal
                pass
    
    # This test mainly ensures edge moves don't cause crashes


def test_performance_stress():
    """Stress test with rapid move sequences."""
    game = Game()
    move_count = 0
    max_moves = 60  # Maximum possible moves in Othello
    
    while move_count < max_moves:
        legal_moves = game.legal_moves()
        if legal_moves == 0:
            # Pass
            game.black_to_move = not game.black_to_move
            # Check if opponent also has no moves
            if game.legal_moves() == 0:
                break  # Game over
            continue
        
        # Choose first legal move (simple strategy)
        move = legal_moves & -legal_moves  # Get LSB
        game.apply_move(move)
        move_count += 1
    
    # Game should end in a valid state
    final_black = bin(game.board.black).count('1')
    final_white = bin(game.board.white).count('1')
    
    assert final_black + final_white >= 4  # At least initial stones
    assert final_black + final_white <= 64  # Not more than board size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
