import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from othello.board import Board

def test_initial_setup():
    b = Board()
    assert b.black != 0
    assert b.white != 0
    assert b.black & b.white == 0


def test_apply_move():
    b = Board()
    moves = b.legal_moves("black")
    assert len(moves) > 0
    move_pos = moves[0]
    b.apply_move("black", move_pos)
    assert (b.black | b.white) & (1 << move_pos)
