import json
import os

SCOREBOARD_PATH = os.path.join(os.path.dirname(__file__), "scoreboard.json")


def _default_scores() -> dict:
    return {"Black": 0, "White": 0, "Draw": 0}


def load_scores() -> dict:
    """Load scores from ``SCOREBOARD_PATH`` if it exists."""
    if os.path.exists(SCOREBOARD_PATH):
        try:
            with open(SCOREBOARD_PATH) as f:
                return json.load(f)
        except Exception:
            return _default_scores()
    return _default_scores()


def save_scores(scores: dict) -> None:
    """Persist ``scores`` to ``SCOREBOARD_PATH``."""
    with open(SCOREBOARD_PATH, "w") as f:
        json.dump(scores, f)


def update_scores(winner: str | None) -> dict:
    """Update scoreboard with the winner ('Black', 'White' or ``None`` for draw)."""
    scores = load_scores()
    if winner is None:
        scores["Draw"] = scores.get("Draw", 0) + 1
    else:
        scores[winner] = scores.get(winner, 0) + 1
    save_scores(scores)
    return scores


def format_scores(scores: dict) -> str:
    """Return a formatted scoreboard string."""
    return (
        f"Scoreboard - Black: {scores.get('Black',0)}, "
        f"White: {scores.get('White',0)}, "
        f"Draw: {scores.get('Draw',0)}"
    )
