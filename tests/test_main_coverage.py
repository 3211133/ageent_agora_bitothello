"""Tests for main.py module to improve test coverage."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')


class TestMainModule:
    """Test suite for main.py module."""
    
    @patch('main.othello.cli.main')
    def test_main_function_calls_cli(self, mock_cli_main):
        """Test that main function calls CLI main."""
        # Import main module
        import main
        
        # Call main function
        main.main()
        
        # Should call CLI main function
        mock_cli_main.assert_called_once()
    
    @patch('main.othello.cli.main')
    def test_main_module_execution(self, mock_cli_main):
        """Test main module when executed directly."""
        # Import main module
        import main
        
        # Simulate direct execution
        with patch.object(main, '__name__', '__main__'):
            # This would normally call main() if __name__ == '__main__'
            # We test the function directly since import doesn't trigger __main__
            main.main()
            
        mock_cli_main.assert_called_once()
    
    def test_main_module_imports(self):
        """Test that main module imports correctly."""
        # Should be able to import without errors
        import main
        
        # Should have main function
        assert hasattr(main, 'main')
        assert callable(main.main)
    
    def test_main_module_structure(self):
        """Test main module structure and content."""
        import main
        
        # Should import othello.cli
        assert hasattr(main, 'othello')
        
        # Main function should exist
        assert 'main' in dir(main)


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running main module coverage tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All main module coverage tests passed!")
    else:
        print("❌ Some main module tests failed!")
        sys.exit(1)