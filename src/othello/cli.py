"""Command line interface for playing Othello."""

from .board import BitBoard


def parse_move(move_str: str) -> int:
    """Return bit mask corresponding to ``move_str`` such as 'd3'."""
    col = ord(move_str[0].lower()) - ord('a')
    row = int(move_str[1]) - 1
    pos = row * 8 + col
    return 1 << (63 - pos)


def run_game() -> None:
    """Run an interactive two-player game in the terminal."""
    board = BitBoard.initial()
    black_to_move = True
    while True:
        print(board)
        player = 'Black' if black_to_move else 'White'
        legal = board.legal_moves(
            board.black if black_to_move else board.white,
            board.white if black_to_move else board.black,
        )
        if legal == 0:
            print(f"{player} has no moves. Pass.")
            black_to_move = not black_to_move
            if board.legal_moves(
                board.black if black_to_move else board.white,
                board.white if black_to_move else board.black,
            ) == 0:
                print("No moves for both players. Game over.")
                break
            continue
        move_str = input(f"{player} move (e.g., d3) or 'q' to quit: ")
        if move_str.lower() == 'q':
            break
        try:
            move = parse_move(move_str)
            board = board.apply_move(move, black_to_move)
            black_to_move = not black_to_move
        except ValueError as e:
            print(f"Illegal move: {e}. Please try again.")
    b_count = bin(board.black).count('1')
    w_count = bin(board.white).count('1')
    print(f"Final score - Black: {b_count}, White: {w_count}")


def main() -> None:
    """Entry point used by ``python -m othello.cli``."""
    run_game()
