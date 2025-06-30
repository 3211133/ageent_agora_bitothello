import sys, os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard
from othello.cli import parse_move


def mask_from_ascii(board_str: str) -> int:
    lines = [line.strip() for line in board_str.strip().splitlines()]
    mask = 0
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch != '.':
                bit = 1 << (63 - (r * 8 + c))
                mask |= bit
    return mask


def test_parse_move_case_insensitive():
    assert parse_move("D3") == 1 << (63 - (2 * 8 + 3))


def test_board_str_initial():
    board = BitBoard.initial()
    expected = (
        "........\n"
        "........\n"
        "........\n"
        "...WB...\n"
        "...BW...\n"
        "........\n"
        "........\n"
        "........\n"
    )
    assert str(board) == expected


def test_flips_for_d3_move():
    board = BitBoard.initial()
    move = parse_move("d3")
    flips = board.flips(move, board.black, board.white)
    expected = mask_from_ascii(
        """
........
........
........
...X....
........
........
........
........
"""
    )
    assert flips == expected


def test_from_ascii_invalid_character():
    diagram = "\n".join([
        "........",
        "........",
        "........",
        "...QB...",
        "...BW...",
        "........",
        "........",
        "........",
    ])
    with pytest.raises(ValueError):
        BitBoard.from_ascii(diagram)
