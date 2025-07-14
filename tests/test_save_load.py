import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, DEFAULT_BOARD_SIZE
from othello.game import save_state, load_state
from pathlib import Path
import pytest


def test_save_load_default_size():
    """Test save/load functionality with default board size."""
    board = BitBoard.initial()
    filename = "test_default.sav"
    save_state(board, True, filename)
    
    # Verify file is created in saves directory (security verification)
    assert (Path('saves') / filename).exists()
    
    loaded_board, black_to_move = load_state(filename)
    assert loaded_board == board
    assert black_to_move is True
    assert loaded_board.size == DEFAULT_BOARD_SIZE  # 8


def test_save_load_custom_sizes():
    """Test save/load functionality with various custom board sizes."""
    test_sizes = [4, 6, 10, 12, 26]
    
    for size in test_sizes:
        board = BitBoard.initial(size)
        filename = f"test_size_{size}.sav"
        save_state(board, False, filename)
        
        # Verify file exists
        assert (Path('saves') / filename).exists()
        
        loaded_board, black_to_move = load_state(filename)
        assert loaded_board == board
        assert black_to_move is False
        assert loaded_board.size == size  # Size preservation verification


def test_new_save_format():
    """Test that new save format includes 4 lines including board size."""
    board = BitBoard.initial(6)
    filename = "test_format.sav"
    save_state(board, True, filename)
    
    # Read file directly to verify format
    with open(Path('saves') / filename, 'r') as f:
        lines = f.read().splitlines()
    
    assert len(lines) == 4
    assert int(lines[0]) == board.black  # Black pieces
    assert int(lines[1]) == board.white  # White pieces
    assert int(lines[2]) == 1  # Black to move
    assert int(lines[3]) == 6  # Board size


def test_backward_compatibility_legacy_format():
    """Test loading legacy 3-line save files (backward compatibility)."""
    # Create a legacy format file manually (3 lines without size)
    board = BitBoard.initial()  # 8x8 board
    filename = "legacy_format.sav"
    
    # Write legacy format (3 lines)
    legacy_content = f"{board.black}\n{board.white}\n1\n"
    with open(Path('saves') / filename, 'w') as f:
        f.write(legacy_content)
    
    # Should load successfully with default size
    loaded_board, black_to_move = load_state(filename)
    assert loaded_board == board
    assert black_to_move is True
    assert loaded_board.size == DEFAULT_BOARD_SIZE  # Should default to 8


def test_invalid_board_size_in_save():
    """Test handling of invalid board sizes in save files."""
    board = BitBoard.initial()
    filename = "invalid_size.sav"
    
    # Create file with invalid board size
    invalid_content = f"{board.black}\n{board.white}\n1\n3\n"  # Size 3 is invalid (odd)
    with open(Path('saves') / filename, 'w') as f:
        f.write(invalid_content)
    
    # Should raise ValueError for invalid size
    with pytest.raises(ValueError, match="Invalid board size: 3"):
        load_state(filename)


def test_invalid_save_file_formats():
    """Test handling of various invalid save file formats."""
    # Test file with too many lines
    filename = "too_many_lines.sav"
    content = "1\n2\n1\n8\n5\n"  # 5 lines
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="expected 3 or 4 lines, got 5"):
        load_state(filename)
    
    # Test file with too few lines
    filename = "too_few_lines.sav"
    content = "1\n2\n"  # 2 lines
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="expected 3 or 4 lines, got 2"):
        load_state(filename)


def test_corrupted_save_files():
    """Test handling of corrupted save file data."""
    # Test non-integer values in new format
    filename = "corrupted_new.sav"
    content = "abc\n123\n1\n8\n"  # Invalid black pieces
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="Corrupted save file \\(new format\\)"):
        load_state(filename)
    
    # Test non-integer values in legacy format  
    filename = "corrupted_legacy.sav"
    content = "123\nabc\n1\n"  # Invalid white pieces
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="Corrupted save file \\(legacy format\\)"):
        load_state(filename)


def test_board_size_edge_cases():
    """Test board size validation edge cases."""
    board = BitBoard.initial()
    filename = "edge_cases.sav"
    
    # Test minimum invalid size (too small)
    content = f"{board.black}\n{board.white}\n1\n2\n"
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="Invalid board size: 2"):
        load_state(filename)
    
    # Test maximum invalid size (too large)
    content = f"{board.black}\n{board.white}\n1\n28\n"
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="Invalid board size: 28"):
        load_state(filename)
    
    # Test odd size (invalid)
    content = f"{board.black}\n{board.white}\n1\n7\n"
    with open(Path('saves') / filename, 'w') as f:
        f.write(content)
    
    with pytest.raises(ValueError, match="Invalid board size: 7"):
        load_state(filename)


def test_migration_from_legacy_to_new_format():
    """Test migration from legacy format to new format."""
    # Create legacy save
    board = BitBoard.initial()
    legacy_filename = "migration_test.sav"
    
    # Manually create legacy format
    legacy_content = f"{board.black}\n{board.white}\n1\n"
    with open(Path('saves') / legacy_filename, 'w') as f:
        f.write(legacy_content)
    
    # Load legacy format
    loaded_board, black_to_move = load_state(legacy_filename)
    assert loaded_board.size == DEFAULT_BOARD_SIZE
    
    # Save in new format
    new_filename = "migrated.sav" 
    save_state(loaded_board, black_to_move, new_filename)
    
    # Verify new format has 4 lines
    with open(Path('saves') / new_filename, 'r') as f:
        lines = f.read().splitlines()
    
    assert len(lines) == 4
    assert int(lines[3]) == DEFAULT_BOARD_SIZE


# Backward compatibility test alias
test_save_load = test_save_load_default_size
