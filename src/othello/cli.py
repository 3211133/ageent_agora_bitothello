"""Command line interface for playing Othello."""

from .board import BitBoard, parse_move, DEFAULT_BOARD_SIZE
from .ai import choose_move
from . import network
from .game import Game, save_state, load_state
from . import scoreboard
import argparse
import socket
import time




def run_game(
    vs_ai: bool = False,
    ai_vs_ai: bool = False,
    ai_level: str = "easy",
    time_limit: float | None = None,
    size: int = DEFAULT_BOARD_SIZE,
) -> BitBoard:
    """Run an interactive game in the terminal and return the final board.

    ``vs_ai``  enables human vs computer play (human as black, AI as white).
    ``ai_vs_ai`` runs an automatic game between two AIs.
    ``ai_vs_ai`` takes precedence over ``vs_ai``.
    ``ai_level`` specifies the AI difficulty (``"easy"``, ``"hard`` or ``"expert"``).
    """
    try:
        board = BitBoard.initial(size)
    except TypeError:
        board = BitBoard.initial()
    game = Game(board=board, black_to_move=True)
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
        if time_left is not None and time_left[game.black_to_move] <= 0:
            player = "Black" if game.black_to_move else "White"
            print(f"{player} ran out of time. Game over.")
            break
        start = time.time()
        acting_player = game.black_to_move
        print(game.board)
        player = "Black" if game.black_to_move else "White"
        legal = game.legal_moves()
        if legal == 0:
            print(f"{player} has no moves. Pass.")
            game.black_to_move = not game.black_to_move
            if deduct(acting_player, start):
                break
            if game.legal_moves() == 0:
                print("No moves for both players. Game over.")
                break
            continue
        if ai_vs_ai or (vs_ai and not game.black_to_move):
            move = choose_move(game.board, game.black_to_move, level=ai_level)
            if move == 0:  # AI has no legal moves
                print(f"{player} (AI) has no moves. Pass.")
                game.black_to_move = not game.black_to_move
                if deduct(acting_player, start):
                    break
                if game.legal_moves() == 0:
                    print("No moves for both players. Game over.")
                    break
                continue
            game.apply_move(move)
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
            if not game.undo():
                print("Cannot undo")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "r":
            if not game.redo():
                print("Cannot redo")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "s":
            save_state(game.board, game.black_to_move)
            print("Game saved")
            if deduct(acting_player, start):
                break
            continue
        if move_str.lower() == "l":
            try:
                board, black = load_state()
                game.board, game.black_to_move = board, black
                game.history[:] = [(board, black)]
                game.future.clear()
                print("Game loaded")
            except Exception as e:
                print(f"Load failed: {e}")
            if deduct(acting_player, start):
                break
            continue
        try:
            move = parse_move(move_str, size)
            game.apply_move(move)
        except ValueError as e:
            print(f"Illegal move: {e}. Please try again.")
            if deduct(acting_player, start):
                break
            continue
        if deduct(acting_player, start):
            break
    b_count = bin(game.board.black).count("1")
    w_count = bin(game.board.white).count("1")
    print(f"Final score - Black: {b_count}, White: {w_count}")
    winner = "Black" if b_count > w_count else "White" if w_count > b_count else None
    scores = scoreboard.update_scores(winner)
    print(scoreboard.format_scores(scores))
    return game.board


def _parse_host_port(host_port: str) -> tuple[str, int]:
    """Safely parse host:port string with validation."""
    if not host_port or ":" not in host_port:
        raise ValueError("Invalid host:port format. Expected 'host:port'")
    
    # Use rsplit to handle IPv6 addresses
    parts = host_port.rsplit(":", 1)
    if len(parts) != 2:
        raise ValueError("Invalid host:port format. Expected 'host:port'")
    
    host, port_str = parts
    
    # Validate host is not empty
    if not host.strip():
        raise ValueError("Host cannot be empty")
    
    # Validate and parse port
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of valid range (1-65535)")
        return host.strip(), port
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError(f"Invalid port number: {port_str}")
        raise


def _validate_network_move(msg: str, size: int) -> int:
    """Validate and parse a move received from network with security checks.
    
    Args:
        msg: Raw message received from network
        size: Board size for validation
        
    Returns:
        Validated move bit mask
        
    Raises:
        ValueError: If message is invalid or contains suspicious content
        TypeError: If inputs are not of expected types
    """
    # Input type validation
    if not isinstance(msg, str):
        raise TypeError(f"Network message must be a string, got {type(msg).__name__}")
    
    # Basic security checks
    if len(msg) > 10:  # Reasonable limit for move strings
        raise ValueError(f"Network message too long: {len(msg)} characters")
    
    # Check for suspicious content
    suspicious_chars = ['\0', '\r', '\t', '\b', '\f', '\v']
    for char in suspicious_chars:
        if char in msg:
            raise ValueError(f"Network message contains suspicious character: {repr(char)}")
    
    # Check for potential injection patterns
    if any(pattern in msg.lower() for pattern in ['script', 'eval', 'exec', 'import']):
        raise ValueError("Network message contains suspicious content")
    
    # Validate as move using existing parse_move function
    try:
        return parse_move(msg, size)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid move format in network message: {e}")


def run_network_game(host: str | None = None, connect: str | None = None, size: int = DEFAULT_BOARD_SIZE) -> BitBoard:
    """Play a game against a remote opponent.
    
    SECURITY WARNING: Network communication is unencrypted and unauthenticated.
    - All game data is transmitted in plaintext
    - Anyone can join game sessions without authorization
    - Communications can be intercepted and modified
    - Only use on trusted networks
    - For production use, implement TLS encryption and authentication
    """
    if host:
        try:
            h, p = _parse_host_port(host)
            sock = network.host_game(h, p)
            my_black = True
        except ValueError as e:
            raise ValueError(f"Invalid host format: {e}")
    elif connect:
        try:
            h, p = _parse_host_port(connect)
            sock = network.join_game(h, p, timeout=30.0)
            my_black = False
        except ValueError as e:
            raise ValueError(f"Invalid connect format: {e}")
    else:
        raise ValueError("host or connect must be provided")

    try:
        board = BitBoard.initial(size)
    except TypeError:
        board = BitBoard.initial()
    game = Game(board=board, black_to_move=True)

    while True:
        print(game.board)
        player = "Black" if game.black_to_move else "White"
        legal = game.legal_moves()
        if legal == 0:
            print(f"{player} has no moves. Pass.")
            if game.black_to_move == my_black:
                network.send_line(sock, "PASS")
            else:
                msg = network.recv_line(sock)
                if msg != "PASS":
                    raise ValueError("Expected PASS")
            game.black_to_move = not game.black_to_move
            if game.legal_moves() == 0:
                print("No moves for both players. Game over.")
                break
            continue
        if game.black_to_move == my_black:
            move_str = input(f"{player} move (e.g., d3) or 'q' to quit: ")
            if move_str.lower() == "q":
                network.send_line(sock, "QUIT")
                break
            try:
                move = parse_move(move_str, size)
            except (ValueError, TypeError) as e:
                print(f"Invalid move: {e}")
                continue
            network.send_line(sock, move_str)
        else:
            print("Waiting for opponent...")
            msg = network.recv_line(sock)
            if msg == "QUIT":
                print("Opponent quit.")
                break
            
            # Validate received network message
            try:
                move = _validate_network_move(msg, size)
            except (ValueError, TypeError) as e:
                print(f"Invalid move received from opponent: {e}")
                print("Terminating game due to protocol violation.")
                break
        game.apply_move(move)

    b_count = bin(game.board.black).count("1")
    w_count = bin(game.board.white).count("1")
    print(f"Final score - Black: {b_count}, White: {w_count}")
    winner = "Black" if b_count > w_count else "White" if w_count > b_count else None
    scores = scoreboard.update_scores(winner)
    print(scoreboard.format_scores(scores))
    return game.board


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
    parser.add_argument(
        "--size",
        type=int,
        default=DEFAULT_BOARD_SIZE,
        help="Board size (even number)",
    )
    parser.add_argument("--host", help="Host a network game at host:port")
    parser.add_argument("--connect", help="Connect to a network game at host:port")
    args = parser.parse_args()
    if args.host or args.connect:
        run_network_game(host=args.host, connect=args.connect, size=args.size)
    else:
        run_game(
            vs_ai=args.ai,
            ai_vs_ai=args.ai_vs_ai,
            ai_level=args.ai_level,
            time_limit=args.time_limit,
            size=args.size,
        )

# Backward compatible entry point
play = main
