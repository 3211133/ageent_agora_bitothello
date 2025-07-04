import random
import sys, os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.ai import choose_move
from othello.cli import run_game, parse_move


def test_ai_move_is_legal():
    random.seed(0)
    board = BitBoard.initial()
    move = choose_move(board, True)
    legal = board.legal_moves(board.black, board.white)
    assert move & legal


def test_ai_vs_ai_completes():
    random.seed(0)
    board = run_game(ai_vs_ai=True)
    assert isinstance(board, BitBoard)
    no_moves_black = board.legal_moves(board.black, board.white)
    no_moves_white = board.legal_moves(board.white, board.black)
    assert no_moves_black == 0 and no_moves_white == 0


def test_hard_ai_chooses_greedy_move():
    board = BitBoard.from_ascii(
        """
........
........
...W....
.BWWW...
...B....
........
........
........
"""
    )
    move = choose_move(board, True, level="hard")
    expected = 1 << (63 - (3 * 8 + 5))  # f4
    assert move == expected


def test_expert_ai_prefers_positional_move():
    board = BitBoard.from_ascii(
        """
........
........
...W....
.BWWW...
...B....
........
........
........
"""
    )
    move = choose_move(board, True, level="expert")
    expected = parse_move("f3")
    assert move == expected


def test_ai_vs_ai_respects_difficulty(monkeypatch):
    """AI vs AI mode should forward the chosen difficulty level."""

    start_board = BitBoard.from_ascii(
        """
........
........
...W....
.BWWW...
...B....
........
........
........
"""
    )

    # Mirror vertically to ensure the greedy move is not the first enumerated
    rows = list(reversed(str(start_board).splitlines()))
    mirrored = BitBoard.from_ascii("\n".join(rows))

    def fake_initial():
        return mirrored

    moves = []

    def capture_move(board, black_to_move, level="easy"):
        move = choose_move(board, black_to_move, level=level)
        moves.append((level, move))
        raise StopIteration

    monkeypatch.setattr("othello.cli.BitBoard.initial", fake_initial)
    monkeypatch.setattr("othello.cli.choose_move", capture_move)
    monkeypatch.setattr("othello.ai.random.choice", lambda seq: seq[0])

    with pytest.raises(StopIteration):
        run_game(ai_vs_ai=True, ai_level="easy")
    easy_move = moves.pop()[1]

    monkeypatch.setattr("othello.cli.choose_move", capture_move)
    with pytest.raises(StopIteration):
        run_game(ai_vs_ai=True, ai_level="hard")
    hard_move = moves.pop()[1]

    monkeypatch.setattr("othello.cli.choose_move", capture_move)
    with pytest.raises(StopIteration):
        run_game(ai_vs_ai=True, ai_level="expert")
    expert_move = moves.pop()[1]

    assert easy_move == parse_move("d7")
    assert hard_move == parse_move("f5")
    assert expert_move == parse_move("f6")

