import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from othello.board import BitBoard


def test_initial_setup():
    b = BitBoard.initial()
    assert b.black == 0x0000000810000000
    assert b.white == 0x0000001008000000


def test_legal_moves_initial():
    b = BitBoard.initial()
    moves = b.legal_moves(b.black, b.white)
    expected = (1 << (63-19)) | (1 << (63-26)) | (1 << (63-37)) | (1 << (63-44))
    assert moves == expected


def test_apply_move():
    b = BitBoard.initial()
    move = 1 << (63-19)  # c4
    new_b = b.apply_move(move, True)
    assert bin(new_b.black).count('1') == 4
    assert bin(new_b.white).count('1') == 1
