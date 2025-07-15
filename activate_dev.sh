#!/bin/bash
# Quick development environment activation
# Usage: source activate_dev.sh

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Development environment activated"
    echo "   • Virtual environment: venv"
    echo "   • Python: $(python --version)"
    echo "   • Package: othello (development mode)"
    echo ""
    echo "🔧 Quick commands:"
    echo "   • Run game: othello"
    echo "   • Run GUI: othello-gui"
    echo "   • Run tests: pytest --cov=src"
    echo "   • Quick test: python -c \"import othello.board; print('OK')\""
    echo ""
else
    echo "❌ Virtual environment not found. Run ./scripts/dev-setup.sh first."
fi
