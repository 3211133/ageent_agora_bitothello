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
    board = BitBoard.from_ascii(
        """
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
BBBBBBBB
"""
    )
    assert board.legal_moves(board.black, board.white) == 0
    assert board.legal_moves(board.white, board.black) == 0


def test_legal_moves_on_edge_positions():
    board = BitBoard.from_ascii(
        """
........
...WWW..
.B.W....
.BWWWWB.
.BBBWWB.
.BBWWWB.
.BWWBBB.
.BBBBBW.
"""
    )
    white_moves = board.legal_moves(board.white, board.black)
    black_moves = board.legal_moves(board.black, board.white)
    assert white_moves != 0
    assert black_moves != 0
