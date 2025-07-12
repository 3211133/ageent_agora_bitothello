import json
import os
import random
from .board import BitBoard, parse_move

# Opening book loaded from ``opening_book.json`` if available
_BOOK_PATH = os.path.join(os.path.dirname(__file__), "opening_book.json")
_opening_book: dict[str, str] | None = None


def _load_opening_book() -> dict[str, str]:
    """Load opening book from JSON file if not already loaded."""
    global _opening_book
    if _opening_book is None:
        try:
            with open(_BOOK_PATH) as f:
                _opening_book = json.load(f)
        except OSError:
            _opening_book = {}
    return _opening_book

# Default positional weights for 8x8 board. Corners are highly valued while 
# squares adjacent to corners are penalised. Values chosen heuristically.
_DEFAULT_WEIGHTS_8X8 = [
    100, -20, 10, 5, 5, 10, -20, 100,
    -20, -50, -2, -2, -2, -2, -50, -20,
    10, -2, 5, 1, 1, 5, -2, 10,
    5, -2, 1, 0, 0, 1, -2, 5,
    5, -2, 1, 0, 0, 1, -2, 5,
    10, -2, 5, 1, 1, 5, -2, 10,
    -20, -50, -2, -2, -2, -2, -50, -20,
    100, -20, 10, 5, 5, 10, -20, 100,
]

# Cache for dynamically generated weight tables
_weight_cache: dict[int, list[int]] = {}


def _generate_weights(size: int) -> list[int]:
    """Generate positional weights for a board of given size.
    
    Uses the same strategic principles as the 8x8 board:
    - Corners are highly valued (100)
    - Squares adjacent to corners are penalized (-20 to -50)  
    - Edge squares have moderate value (5-10)
    - Center squares have neutral to slightly positive value (0-5)
    
    Args:
        size: Board size (must be even, 4 <= size <= 26)
        
    Returns:
        List of weights for each square (row-major order)
    """
    if size in _weight_cache:
        return _weight_cache[size]
    
    if size == 8:
        _weight_cache[size] = _DEFAULT_WEIGHTS_8X8[:]
        return _weight_cache[size]
    
    weights = [0] * (size * size)
    
    for row in range(size):
        for col in range(size):
            idx = row * size + col
            
            # Distance from edges
            dist_from_edge = min(row, col, size - 1 - row, size - 1 - col)
            
            # Corner squares (highest value)
            if (row == 0 or row == size - 1) and (col == 0 or col == size - 1):
                weights[idx] = 100
            
            # Squares adjacent to corners (penalized)
            elif dist_from_edge == 0 and (
                (row <= 1 or row >= size - 2) or (col <= 1 or col >= size - 2)
            ):
                # Adjacent to corner
                if ((row == 0 or row == size - 1) and (col == 1 or col == size - 2)) or \
                   ((col == 0 or col == size - 1) and (row == 1 or row == size - 2)):
                    weights[idx] = -20
                # Diagonal to corner  
                elif (row == 1 or row == size - 2) and (col == 1 or col == size - 2):
                    weights[idx] = -50
                else:
                    weights[idx] = -2
            
            # Edge squares (moderate value)
            elif dist_from_edge == 0:
                weights[idx] = 10 if size >= 6 else 5
            
            # Second row/column from edge
            elif dist_from_edge == 1:
                if (row == 1 or row == size - 2) and (col == 1 or col == size - 2):
                    weights[idx] = -2  # Near corner penalty
                else:
                    weights[idx] = 5 if size >= 8 else 1
            
            # Inner squares (neutral to slightly positive)
            else:
                weights[idx] = min(dist_from_edge, 5)
    
    _weight_cache[size] = weights
    return weights


def _evaluate(board: BitBoard) -> int:
    """Return a positional evaluation of ``board`` from black's perspective.
    
    Uses board size-specific positional weights that follow strategic principles:
    corners are highly valued, adjacent squares are penalized, edges have 
    moderate value, and center squares are neutral to slightly positive.
    
    Args:
        board: BitBoard to evaluate
        
    Returns:
        Score from black's perspective (positive favors black)
    """
    weights = _generate_weights(board.size)
    total_squares = board.size * board.size
    
    score = 0
    bb = board.black
    while bb:
        lsb = bb & -bb
        bit_position = lsb.bit_length() - 1
        # Convert bit position to array index (MSB first)
        weight_idx = total_squares - 1 - bit_position
        score += weights[weight_idx]
        bb ^= lsb

    bb = board.white
    while bb:
        lsb = bb & -bb
        bit_position = lsb.bit_length() - 1
        # Convert bit position to array index (MSB first)  
        weight_idx = total_squares - 1 - bit_position
        score -= weights[weight_idx]
        bb ^= lsb

    return score


def _random_move(mask: int) -> int:
    """Return a random set bit from ``mask``."""
    # NOTE: uses Python's random.choice over collected moves
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

    # Consult opening book for known positions (8x8 boards only)
    if board.size == 8:
        book = _load_opening_book()
        key = f"{board.black}-{board.white}-{1 if black_to_move else 0}"
        move_str = book.get(key)
        if move_str:
            move = parse_move(move_str, board.size)
            if move & legal:
                return move

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
