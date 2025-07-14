from __future__ import annotations
from dataclasses import dataclass, field
import os
from pathlib import Path

from .board import BitBoard


@dataclass
class Game:
    """Game state holding the board and turn information."""

    # TODO: track cumulative scores between games

    board: BitBoard = field(default_factory=BitBoard.initial)
    black_to_move: bool = True
    history: list[tuple[BitBoard, bool]] = field(default_factory=list)
    future: list[tuple[BitBoard, bool]] = field(default_factory=list)
    max_history_size: int = 100  # Maximum number of moves to keep in history
    max_future_size: int = 50    # Maximum number of undo states to keep in future stack

    def __post_init__(self) -> None:
        if not self.history:
            self.history.append((self.board, self.black_to_move))

    def legal_moves(self) -> int:
        player = self.board.black if self.black_to_move else self.board.white
        opponent = self.board.white if self.black_to_move else self.board.black
        return self.board.legal_moves(player, opponent)

    def apply_move(self, move: int) -> None:
        self.board = self.board.apply_move(move, self.black_to_move)
        self.black_to_move = not self.black_to_move
        self.history.append((self.board, self.black_to_move))
        
        # Bound history size to prevent memory leaks
        if len(self.history) > self.max_history_size:
            # Remove oldest entries, but keep at least one for undo functionality
            entries_to_remove = len(self.history) - self.max_history_size
            self.history = self.history[entries_to_remove:]
        
        self.future.clear()

    def undo(self) -> bool:
        if len(self.history) <= 1:
            return False
        self.future.append(self.history.pop())
        
        # Bound future stack size to prevent memory leaks from excessive undos
        if len(self.future) > self.max_future_size:
            # Remove oldest redo states
            entries_to_remove = len(self.future) - self.max_future_size
            self.future = self.future[entries_to_remove:]
        
        self.board, self.black_to_move = self.history[-1]
        return True

    def redo(self) -> bool:
        if not self.future:
            return False
        self.board, self.black_to_move = self.future.pop()
        self.history.append((self.board, self.black_to_move))
        return True


def _validate_save_path(filename: str | Path) -> Path:
    """Validate and sanitize save file path to prevent path traversal attacks.
    
    Args:
        filename: User-provided filename
        
    Returns:
        Sanitized Path object within safe directory
        
    Raises:
        ValueError: If filename is invalid or unsafe
    """
    # Convert to string for validation
    filename_str = str(filename)
    
    if not filename_str or not filename_str.strip():
        raise ValueError("Filename cannot be empty")
    
    # Check for absolute paths (security risk)
    if os.path.isabs(filename_str):
        raise ValueError("Absolute paths are not allowed")
    
    # Check for path separators (directory traversal attempt)
    if '/' in filename_str or '\\' in filename_str:
        raise ValueError("Path separators are not allowed in filename")
    
    # Check for parent directory references
    if '..' in filename_str:
        raise ValueError("Parent directory references are not allowed")
    
    # Remove any directory components and keep only the filename (defense in depth)
    safe_filename = Path(filename).name
    
    if not safe_filename:
        raise ValueError("Invalid filename")
    
    # Check for dangerous patterns
    if safe_filename.startswith('.'):
        raise ValueError("Filename cannot start with '.'")
    
    # Additional security checks for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        if char in safe_filename:
            raise ValueError(f"Filename contains dangerous character: {char}")
    
    # Validate file extension
    if not safe_filename.endswith(('.sav', '.othello')):
        safe_filename += '.sav'
    
    # Ensure saves directory exists
    saves_dir = Path('saves')
    saves_dir.mkdir(exist_ok=True)
    
    # Construct safe path
    safe_path = saves_dir / safe_filename
    
    # Final security check - ensure path is within saves directory
    try:
        safe_path.resolve().relative_to(saves_dir.resolve())
    except ValueError:
        raise ValueError("Path traversal attempt detected")
    
    return safe_path


def save_state(board: BitBoard, black_to_move: bool, path: str | Path = "othello.sav") -> None:
    """Save ``board`` and turn information to ``path``.
    
    The file will be saved in the 'saves' directory with path traversal protection.
    Only the filename portion of the path is used for security.
    
    Save format (version 2 with board size preservation):
    Line 1: Black pieces bitboard (integer)
    Line 2: White pieces bitboard (integer) 
    Line 3: Current player (1 for black, 0 for white)
    Line 4: Board size (integer)
    
    Args:
        board: Game board state to save
        black_to_move: Current player turn
        path: Filename for the save file (directory components ignored for security)
        
    Raises:
        ValueError: If filename is invalid or unsafe
        OSError: If file cannot be written
    """
    safe_path = _validate_save_path(path)
    
    try:
        with open(safe_path, "w") as f:
            # New format: include board size as 4th line for preservation
            f.write(f"{board.black}\n{board.white}\n{1 if black_to_move else 0}\n{board.size}\n")
    except OSError as e:
        raise OSError(f"Failed to save game state: {e}")


def load_state(path: str | Path = "othello.sav") -> tuple[BitBoard, bool]:
    """Load board and turn information from ``path``.
    
    The file will be loaded from the 'saves' directory with path traversal protection.
    Only the filename portion of the path is used for security.
    
    Supports both legacy (3-line) and new (4-line) save formats:
    - Legacy format: black, white, turn (defaults to 8x8 board)
    - New format: black, white, turn, size (preserves custom board size)
    
    Args:
        path: Filename to load (directory components ignored for security)
        
    Returns:
        Tuple of (board, black_to_move)
        
    Raises:
        ValueError: If filename is invalid, file format is invalid, or file not found
        OSError: If file cannot be read
    """
    safe_path = _validate_save_path(path)
    
    if not safe_path.exists():
        raise ValueError(f"Save file '{safe_path.name}' not found")
    
    try:
        with open(safe_path) as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise OSError(f"Failed to load game state: {e}")
    
    # Support both legacy (3-line) and new (4-line) formats
    if len(lines) == 3:
        # Legacy format - use default board size for backward compatibility
        try:
            board = BitBoard(int(lines[0]), int(lines[1]))  # Uses DEFAULT_BOARD_SIZE
            black_to_move = bool(int(lines[2]))
            return board, black_to_move
        except (ValueError, TypeError) as e:
            raise ValueError(f"Corrupted save file (legacy format): {e}")
    elif len(lines) == 4:
        # New format - preserve board size
        try:
            black_pieces = int(lines[0])
            white_pieces = int(lines[1])
            black_to_move = bool(int(lines[2]))
            board_size = int(lines[3])
            
            # Validate board size
            if board_size < 4 or board_size > 26 or board_size % 2 != 0:
                raise ValueError(f"Invalid board size: {board_size} (must be even, 4-26)")
            
            board = BitBoard(black_pieces, white_pieces, board_size)
            return board, black_to_move
        except (ValueError, TypeError) as e:
            raise ValueError(f"Corrupted save file (new format): {e}")
    else:
        raise ValueError(f"Invalid save file format: expected 3 or 4 lines, got {len(lines)}")
