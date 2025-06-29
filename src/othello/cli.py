import string
from .board import Board, BLACK, WHITE


def bit_to_coord(bit: int) -> str:
    idx = (bit.bit_length() - 1)
    row, col = divmod(idx, 8)
    return f"{string.ascii_lowercase[col]}{row + 1}"


def coord_to_bit(coord: str) -> int:
    col = string.ascii_lowercase.index(coord[0].lower())
    row = int(coord[1]) - 1
    idx = row * 8 + col
    return 1 << idx


def print_board(board: Board):
    print("  a b c d e f g h")
    for row in range(8):
        line = [str(row + 1)]
        for col in range(8):
            idx = row * 8 + col
            mask = 1 << idx
            if board.black & mask:
                line.append('B')
            elif board.white & mask:
                line.append('W')
            else:
                line.append('.')
        print(' '.join(line))


def play():
    board = Board()
    color = BLACK
    while True:
        print_board(board)
        moves = board.moves_list(color)
        if not moves:
            color = -color
            if not board.moves_list(color):
                break
            continue
        move_str = input(f"Enter move for {'Black' if color == BLACK else 'White'} (e.g. d3, q to quit): ")
        if move_str.lower() == 'q':
            break
        try:
            move = coord_to_bit(move_str)
        except Exception:
            print("Invalid format")
            continue
        if move not in moves:
            print("Illegal move")
            continue
        board.apply_move(color, move)
        color = -color
    b, w = board.count()
    print_board(board)
    print(f"Game over. Black: {b} White: {w}")

