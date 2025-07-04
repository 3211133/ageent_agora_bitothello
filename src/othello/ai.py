import random
from .board import BitBoard

# Positional weights used for the evaluation function. Corners are highly
# valued while squares adjacent to corners are penalised. The values were
# chosen heuristically.
_WEIGHTS = [
    100, -20, 10, 5, 5, 10, -20, 100,
    -20, -50, -2, -2, -2, -2, -50, -20,
    10, -2, 5, 1, 1, 5, -2, 10,
    5, -2, 1, 0, 0, 1, -2, 5,
    5, -2, 1, 0, 0, 1, -2, 5,
    10, -2, 5, 1, 1, 5, -2, 10,
    -20, -50, -2, -2, -2, -2, -50, -20,
    100, -20, 10, 5, 5, 10, -20, 100,
]


def _evaluate(board: BitBoard) -> int:
    """Return a positional evaluation of ``board`` from black's perspective."""

    score = 0
    bb = board.black
    while bb:
        lsb = bb & -bb
        idx = lsb.bit_length() - 1
        score += _WEIGHTS[63 - idx]
        bb ^= lsb

    bb = board.white
    while bb:
        lsb = bb & -bb
        idx = lsb.bit_length() - 1
        score -= _WEIGHTS[63 - idx]
        bb ^= lsb

    return score


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
    ``"easy"`` picks a random move,
    ``"hard"`` chooses the move that flips the most discs, and
    ``"expert"`` uses a positional evaluation (breaking ties randomly).
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

    if level == "expert":
        best_score = None
        best_moves = []
        bb = legal
        while bb:
            lsb = bb & -bb
            next_board = board.apply_move(lsb, black_to_move)
            score = _evaluate(next_board)
            if not black_to_move:
                score = -score
            if best_score is None or score > best_score:
                best_score = score
                best_moves = [lsb]
            elif score == best_score:
                best_moves.append(lsb)
            bb ^= lsb
        return random.choice(best_moves)

    return _random_move(legal)
