import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello.board import BitBoard, parse_move


def initial_ascii(size: int) -> str:
    board = [["." for _ in range(size)] for _ in range(size)]
    mid = size // 2
    board[mid - 1][mid] = "B"
    board[mid][mid - 1] = "B"
    board[mid - 1][mid - 1] = "W"
    board[mid][mid] = "W"
    return "\n".join("".join(row) for row in board)


def expected_initial_moves_mask(size: int) -> int:
    mid = size // 2
    coords = [
        (mid - 2, mid - 1),
        (mid - 1, mid - 2),
        (mid, mid + 1),
        (mid + 1, mid),
    ]
    mask = 0
    for r, c in coords:
        if 0 <= r < size and 0 <= c < size:
            move = parse_move(f"{chr(ord('a') + c)}{r + 1}", size)
            mask |= move
    return mask


@pytest.mark.parametrize("size", [6, 10])
def test_initial_setup_varsize(size):
    board = BitBoard.initial(size)
    expected = BitBoard.from_ascii(initial_ascii(size))
    assert board == expected


@pytest.mark.parametrize("size", [6, 10])
def test_legal_moves_initial_varsize(size):
    board = BitBoard.initial(size)
    moves = board.legal_moves(board.black, board.white)
    assert moves == expected_initial_moves_mask(size)


@pytest.mark.parametrize("size", [6, 10])
def test_apply_move_varsize(size):
    board = BitBoard.initial(size)
    moves = board.legal_moves(board.black, board.white)
    move = moves & -moves  # choose one legal move
    flips = board.flips(move, board.black, board.white)
    expected_black = board.black | move | flips
    expected_white = board.white & ~flips
    new_board = board.apply_move(move, True)
    assert new_board.black == expected_black
    assert new_board.white == expected_white
    assert new_board.size == size


@pytest.mark.parametrize("size", [6, 10])
def test_parse_move_case_insensitive_varsize(size):
    assert parse_move("D3", size) == parse_move("d3", size)


@pytest.mark.parametrize("size", [6, 10])
def test_board_str_initial_varsize(size):
    board = BitBoard.initial(size)
    expected_lines = initial_ascii(size).splitlines()
    expected = "\n".join(line for line in expected_lines) + "\n"
    assert str(board) == expected


@pytest.mark.parametrize("size", [6, 10])
def test_flips_for_d3_move_varsize(size):
    board = BitBoard.initial(size)
    moves = board.legal_moves(board.black, board.white)
    move = moves & -moves
    flips = board.flips(move, board.black, board.white)
    mid = size // 2
    expected_flip = parse_move(f"{chr(ord('a') + mid)}{mid + 1}", size)
    assert flips == expected_flip


@pytest.mark.parametrize("size", [6, 10])
def test_from_ascii_invalid_character_varsize(size):
    diagram_lines = ["." * size for _ in range(size)]
    diagram_lines[0] = "Q" + "." * (size - 1)
    diagram = "\n".join(diagram_lines)
    with pytest.raises(ValueError):
        BitBoard.from_ascii(diagram)
