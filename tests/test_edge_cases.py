import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from othello.board import BitBoard


def test_illegal_move_rejected():
    board = BitBoard.initial()
    # a1 is illegal on the initial board
    move = 1 << (63 - 0)
    with pytest.raises(ValueError):
        board.apply_move(move, True)


def test_game_end_detected():
    board = BitBoard((1 << 64) - 1, 0)
    assert board.legal_moves(board.black, board.white) == 0
    assert board.legal_moves(board.white, board.black) == 0
