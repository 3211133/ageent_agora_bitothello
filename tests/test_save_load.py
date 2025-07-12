import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.game import save_state, load_state


def test_save_load(tmp_path):
    """Test save/load functionality with secure path handling."""
    board = BitBoard.initial()
    # Use just the filename - the secure implementation will save to saves/ directory
    filename = "test_game.sav"
    save_state(board, True, filename)
    loaded_board, black_to_move = load_state(filename)
    assert loaded_board == board
    assert black_to_move is True
