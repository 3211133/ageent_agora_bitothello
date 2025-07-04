import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.cli import run_game


def test_timer_expires_immediately():
    board = run_game(ai_vs_ai=True, time_limit=0.0)
    assert board == BitBoard.initial()
