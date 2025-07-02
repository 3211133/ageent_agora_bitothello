import random
from .board import BitBoard


def _random_move(mask: int) -> int:
    """Return a random set bit from ``mask``."""
    moves = []
    bb = mask
    while bb:
        lsb = bb & -bb
        moves.append(lsb)
        bb ^= lsb
    return random.choice(moves)


def choose_move(board: BitBoard, black_to_move: bool, level: str = "easy") -> int:
    """Return a legal move for the current player.

    ``level`` controls the difficulty:
    ``"easy"`` picks a random move, while ``"hard"`` chooses the move that
    flips the most discs (breaking ties randomly).
    """

    player = board.black if black_to_move else board.white
    opponent = board.white if black_to_move else board.black
    legal = board.legal_moves(player, opponent)
    if legal == 0:
        return 0

    if level == "hard":
        best_moves = []
        max_flips = -1
        bb = legal
        while bb:
            lsb = bb & -bb
            flips = board.flips(lsb, player, opponent)
            count = flips.bit_count()
            if count > max_flips:
                best_moves = [lsb]
                max_flips = count
            elif count == max_flips:
                best_moves.append(lsb)
            bb ^= lsb
        return random.choice(best_moves)

    return _random_move(legal)
