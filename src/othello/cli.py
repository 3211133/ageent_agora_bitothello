"""Command line interface for playing Othello."""

from .board import BitBoard
from .ai import choose_move
from . import network
import argparse
import socket
import time


def save_state(board: BitBoard, black_to_move: bool, path: str = "othello.sav") -> None:
    """Save ``board`` and turn information to ``path``."""
    with open(path, "w") as f:
        f.write(f"{board.black}\n{board.white}\n{1 if black_to_move else 0}\n")


def load_state(path: str = "othello.sav") -> tuple[BitBoard, bool]:
    """Load board and turn information from ``path``."""
    with open(path) as f:
        lines = f.read().splitlines()
    if len(lines) != 3:
        raise ValueError("Invalid save file")
    board = BitBoard(int(lines[0]), int(lines[1]))
    black_to_move = bool(int(lines[2]))
    return board, black_to_move


def parse_move(move_str: str) -> int:
    """Return bit mask corresponding to ``move_str`` such as 'd3'."""
    col = ord(move_str[0].lower()) - ord('a')
    row = int(move_str[1]) - 1
    pos = row * 8 + col
    return 1 << (63 - pos)


def run_game(
    vs_ai: bool = False,
    ai_vs_ai: bool = False,
    ai_level: str = "easy",
    time_limit: float | None = None,
) -> BitBoard:
    """Run an interactive game in the terminal and return the final board.

    ``vs_ai``  enables human vs computer play (human as black, AI as white).
    ``ai_vs_ai`` runs an automatic game between two AIs.
    ``ai_vs_ai`` takes precedence over ``vs_ai``.
    ``ai_level`` specifies the AI difficulty (``"easy"``, ``"hard`` or ``"expert"``).
    """
    board = BitBoard.initial()
    black_to_move = True
    history = [(board, black_to_move)]
    future: list[tuple[BitBoard, bool]] = []
    time_left = {True: time_limit, False: time_limit} if time_limit is not None else None

    def deduct(player: bool, start: float) -> bool:
        if time_left is None:
            return False
        time_left[player] -= time.time() - start
        if time_left[player] <= 0:
            who = "Black" if player else "White"
            print(f"{who} ran out of time. Game over.")
            return True
        return False

    while True:
        if time_left is not None and time_left[black_to_move] <= 0:
            player = "Black" if black_to_move else "White"
            print(f"{player} ran out of time. Game over.")
            break
        start = time.time()
        acting_player = black_to_move
        print(board)
        player = "Black" if black_to_move else "White"
        legal = board.legal_moves(
            board.black if black_to_move else board.white,
            board.white if black_to_move else board.black,
        )
        if legal == 0:
            print(f"{player} has no moves. Pass.")
            black_to_move = not black_to_move
            if deduct(acting_player, start):
                break
            if board.legal_moves(
                board.black if black_to_move else board.white,
                board.white if black_to_move else board.black,
            ) == 0:
                print("No moves for both players. Game over.")
                break
            continue
        if ai_vs_ai or (vs_ai and not black_to_move):
            move = choose_move(board, black_to_move, level=ai_level)
            if move == 0:  # AI has no legal moves
                print(f"{player} (AI) has no moves. Pass.")
                black_to_move = not black_to_move
                if deduct(acting_player, start):
                    break
                if board.legal_moves(
                    board.black if black_to_move else board.white,
                    board.white if black_to_move else board.black,
                ) == 0:
                    print("No moves for both players. Game over.")
                    break
                continue
            board = board.apply_move(move, black_to_move)
            black_to_move = not black_to_move
            if deduct(acting_player, start):
                break
            continue
        move_str = input(
            f"{player} move (e.g., d3), 'u' to undo, 'r' to redo, 's' to save, 'l' to load, or 'q' to quit: "
        )
        if move_str.lower() == "q":
            if deduct(acting_player, start):
                break
            break
        if move_str.lower() == "u":
            if len(history) > 1:
                future.append((board, black_to_move))
                history.pop()
                board, black_to_move = history[-1]
            else:
                print("Cannot undo")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "r":
            if future:
                board, black_to_move = future.pop()
                history.append((board, black_to_move))
            else:
                print("Cannot redo")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "s":
            save_state(board, black_to_move)
            print("Game saved")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "l":
            try:
                board, black_to_move = load_state()
                history = [(board, black_to_move)]
                future.clear()
                print("Game loaded")
            except Exception as e:
                print(f"Load failed: {e}")
            if deduct(acting_player, start):
                break
            continue
        try:
            move = parse_move(move_str)
            board = board.apply_move(move, black_to_move)
            black_to_move = not black_to_move
            history.append((board, black_to_move))
            future.clear()
        except ValueError as e:
            print(f"Illegal move: {e}. Please try again.")
            if deduct(acting_player, start):
                break
            continue
        if deduct(acting_player, start):
            break
    b_count = bin(board.black).count("1")
    w_count = bin(board.white).count("1")
    print(f"Final score - Black: {b_count}, White: {w_count}")
    return board


def run_network_game(host: str | None = None, connect: str | None = None) -> BitBoard:
    """Play a game against a remote opponent."""
    if host:
        h, p = host.split(":")
        sock = network.host_game(h, int(p))
        my_black = True
    elif connect:
        h, p = connect.split(":")
        sock = network.join_game(h, int(p))
        my_black = False
    else:
        raise ValueError("host or connect must be provided")

    board = BitBoard.initial()
    black_to_move = True

    while True:
        print(board)
        player = "Black" if black_to_move else "White"
        legal = board.legal_moves(
            board.black if black_to_move else board.white,
            board.white if black_to_move else board.black,
        )
        if legal == 0:
            print(f"{player} has no moves. Pass.")
            if black_to_move == my_black:
                network.send_line(sock, "PASS")
            else:
                msg = network.recv_line(sock)
                if msg != "PASS":
                    raise ValueError("Expected PASS")
            black_to_move = not black_to_move
            if board.legal_moves(
                board.black if black_to_move else board.white,
                board.white if black_to_move else board.black,
            ) == 0:
                print("No moves for both players. Game over.")
                break
            continue
        if black_to_move == my_black:
            move_str = input(f"{player} move (e.g., d3) or 'q' to quit: ")
            if move_str.lower() == "q":
                network.send_line(sock, "QUIT")
                break
            move = parse_move(move_str)
            network.send_line(sock, move_str)
        else:
            print("Waiting for opponent...")
            msg = network.recv_line(sock)
            if msg == "QUIT":
                print("Opponent quit.")
                break
            move = parse_move(msg)
        board = board.apply_move(move, black_to_move)
        black_to_move = not black_to_move

    b_count = bin(board.black).count("1")
    w_count = bin(board.white).count("1")
    print(f"Final score - Black: {b_count}, White: {w_count}")
    return board


def main() -> None:
    """Entry point used by ``python -m othello.cli``."""
    parser = argparse.ArgumentParser(description="Play Othello")
    parser.add_argument(
        "--ai", action="store_true", help="Play against the computer (as white)"
    )
    parser.add_argument(
        "--ai-vs-ai",
        action="store_true",
        help="Watch two AIs play automatically",
    )
    parser.add_argument(
        "--ai-level",
        choices=["easy", "hard", "expert"],
        default="easy",
        help="AI difficulty level",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        help="Total time per player in seconds",
    )
    parser.add_argument("--host", help="Host a network game at host:port")
    parser.add_argument("--connect", help="Connect to a network game at host:port")
    args = parser.parse_args()
    if args.host or args.connect:
        run_network_game(host=args.host, connect=args.connect)
    else:
        run_game(
            vs_ai=args.ai,
            ai_vs_ai=args.ai_vs_ai,
            ai_level=args.ai_level,
            time_limit=args.time_limit,
        )

# Backward compatible entry point
play = main
