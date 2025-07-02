import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.cli import save_state, load_state


def test_save_load(tmp_path):
    board = BitBoard.initial()
    path = tmp_path / "game.sav"
    save_state(board, True, path)
    loaded_board, black_to_move = load_state(path)
    assert loaded_board == board
    assert black_to_move is True
