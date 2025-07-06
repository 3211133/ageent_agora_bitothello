import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, parse_move
from othello.game import Game


def test_apply_move_updates_history_and_clears_future():
    game = Game(board=BitBoard.initial(), black_to_move=True)
    first_history_len = len(game.history)
    move = parse_move("d3")
    expected = game.board.apply_move(move, True)
    game.apply_move(move)
    assert game.board == expected
    assert game.black_to_move is False
    assert len(game.history) == first_history_len + 1
    assert game.history[-1] == (game.board, game.black_to_move)
    assert game.future == []

    # Undo and apply a different move to ensure future is cleared
    assert game.undo() is True
    move2 = parse_move("c4")
    expected2 = game.board.apply_move(move2, True)
    game.apply_move(move2)
    assert game.board == expected2
    assert game.future == []
    assert len(game.history) == 2


def test_undo_reverts_state_and_populates_future():
    game = Game(board=BitBoard.initial(), black_to_move=True)
    move = parse_move("d3")
    game.apply_move(move)
    assert game.undo() is True
    assert game.board == BitBoard.initial()
    assert game.black_to_move is True
    assert len(game.history) == 1
    assert game.future[-1][0] == BitBoard.initial().apply_move(move, True)

    # Cannot undo past initial state
    assert game.undo() is False
    assert len(game.history) == 1


def test_redo_reapplies_move_and_clears_future():
    game = Game(board=BitBoard.initial(), black_to_move=True)
    move = parse_move("d3")
    game.apply_move(move)
    game.undo()
    assert len(game.future) == 1
    assert game.redo() is True
    assert game.board == BitBoard.initial().apply_move(move, True)
    assert game.black_to_move is False
    assert len(game.history) == 2
    assert game.future == []

    # Redo not possible when future is empty
    assert game.redo() is False
