import random
from .board import BitBoard


def choose_move(board: BitBoard, black_to_move: bool) -> int:
    """Return a legal move for the current player using a random strategy."""
    player = board.black if black_to_move else board.white
    opponent = board.white if black_to_move else board.black
    legal = board.legal_moves(player, opponent)
    if legal == 0:
        return 0
    moves = []
    bb = legal
    while bb:
        lsb = bb & -bb
        moves.append(lsb)
        bb ^= lsb
    return random.choice(moves)
