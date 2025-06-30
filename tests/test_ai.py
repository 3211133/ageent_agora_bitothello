import random
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.ai import choose_move
from othello.cli import run_game


def test_ai_move_is_legal():
    random.seed(0)
    board = BitBoard.initial()
    move = choose_move(board, True)
    legal = board.legal_moves(board.black, board.white)
    assert move & legal


def test_ai_vs_ai_completes():
    random.seed(0)
    run_game(ai_vs_ai=True)
