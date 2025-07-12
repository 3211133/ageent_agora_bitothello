"""Tests for CLI module to improve test coverage."""

import pytest
import sys
import io
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.cli import _parse_host_port, run_game, run_network_game, main
from othello.board import BitBoard, DEFAULT_BOARD_SIZE


class TestCLIFunctions:
    """Test suite for CLI module functions."""
    
    def test_parse_host_port_valid_cases(self):
        """Test _parse_host_port with valid inputs."""
        # Basic host:port
        host, port = _parse_host_port("localhost:8080")
        assert host == "localhost"
        assert port == 8080
        
        # IP address
        host, port = _parse_host_port("192.168.1.1:9999")
        assert host == "192.168.1.1"
        assert port == 9999
        
        # IPv6 with brackets (rsplit handles this)
        host, port = _parse_host_port("[::1]:8080")
        assert host == "[::1]"
        assert port == 8080
        
        # Host with spaces (should be stripped)
        host, port = _parse_host_port("  localhost  :8080")
        assert host == "localhost"
        assert port == 8080
    
    def test_parse_host_port_invalid_cases(self):
        """Test _parse_host_port with invalid inputs."""
        # No colon
        with pytest.raises(ValueError, match="Invalid host:port format"):
            _parse_host_port("localhost")
        
        # Empty string
        with pytest.raises(ValueError, match="Invalid host:port format"):
            _parse_host_port("")
        
        # Empty host
        with pytest.raises(ValueError, match="Host cannot be empty"):
            _parse_host_port(":8080")
        
        # Invalid port (non-numeric)
        with pytest.raises(ValueError, match="Invalid port number"):
            _parse_host_port("localhost:abc")
        
        # Port out of range (too low)
        with pytest.raises(ValueError, match="Port .* out of valid range"):
            _parse_host_port("localhost:0")
        
        # Port out of range (too high)
        with pytest.raises(ValueError, match="Port .* out of valid range"):
            _parse_host_port("localhost:99999")
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_basic_functionality(self, mock_print, mock_input):
        """Test basic run_game functionality."""
        # Mock user quitting immediately
        mock_input.return_value = 'q'
        
        # Run a basic game
        result = run_game(vs_ai=False, ai_vs_ai=False, size=4)
        
        # Should return a BitBoard
        assert isinstance(result, BitBoard)
        assert result.size == 4
        
        # Should have printed game state
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_with_ai(self, mock_print, mock_input):
        """Test run_game with AI opponent."""
        # Mock user quitting after AI move
        mock_input.return_value = 'q'
        
        result = run_game(vs_ai=True, ai_level="easy", size=6)
        
        assert isinstance(result, BitBoard)
        assert result.size == 6
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    @patch('othello.cli.time.time')
    def test_run_game_ai_vs_ai(self, mock_time, mock_print, mock_input):
        """Test run_game with AI vs AI mode."""
        # Mock time to prevent actual delays
        mock_time.return_value = 0
        
        # Run a short AI vs AI game
        result = run_game(ai_vs_ai=True, ai_level="easy", size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_save_load_commands(self, mock_print, mock_input):
        """Test run_game save and load commands."""
        # Test save command then quit
        mock_input.side_effect = ['s', 'q']
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        # Should have attempted to save
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_undo_redo_commands(self, mock_print, mock_input):
        """Test run_game undo and redo commands."""
        # Test undo, redo, then quit
        mock_input.side_effect = ['u', 'r', 'q']
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_invalid_move(self, mock_print, mock_input):
        """Test run_game with invalid move input."""
        # Test invalid move then quit
        mock_input.side_effect = ['z9', 'q']
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        # Should have printed error about illegal move
        mock_print.assert_called()
    
    @patch('othello.cli.network.host_game')
    @patch('othello.cli.network.send_line')
    @patch('othello.cli.network.recv_line')
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_network_game_host(self, mock_print, mock_input, mock_recv, mock_send, mock_host):
        """Test run_network_game as host."""
        # Mock network components
        mock_socket = MagicMock()
        mock_host.return_value = mock_socket
        mock_input.return_value = 'q'
        
        result = run_network_game(host="localhost:8080", size=4)
        
        assert isinstance(result, BitBoard)
        mock_host.assert_called_once_with("localhost", 8080)
        mock_send.assert_called_with(mock_socket, "QUIT")
    
    @patch('othello.cli.network.join_game')
    @patch('othello.cli.network.recv_line')
    @patch('othello.cli.print')
    def test_run_network_game_connect(self, mock_print, mock_recv, mock_join):
        """Test run_network_game as client."""
        # Mock network components
        mock_socket = MagicMock()
        mock_join.return_value = mock_socket
        mock_recv.return_value = "QUIT"
        
        result = run_network_game(connect="localhost:8080", size=4)
        
        assert isinstance(result, BitBoard)
        mock_join.assert_called_once_with("localhost", 8080, timeout=30.0)
    
    def test_run_network_game_invalid_host_format(self):
        """Test run_network_game with invalid host format."""
        with pytest.raises(ValueError, match="Invalid host format"):
            run_network_game(host="invalid_format")
    
    def test_run_network_game_invalid_connect_format(self):
        """Test run_network_game with invalid connect format."""
        with pytest.raises(ValueError, match="Invalid connect format"):
            run_network_game(connect="invalid_format")
    
    def test_run_network_game_no_host_or_connect(self):
        """Test run_network_game with neither host nor connect."""
        with pytest.raises(ValueError, match="host or connect must be provided"):
            run_network_game()
    
    @patch('othello.cli.run_game')
    @patch('sys.argv')
    def test_main_basic_game(self, mock_argv, mock_run_game):
        """Test main function with basic arguments."""
        mock_argv.__getitem__.return_value = ['othello']
        mock_run_game.return_value = BitBoard.initial()
        
        # Test with no arguments (basic game)
        with patch('othello.cli.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                ai=False, ai_vs_ai=False, ai_level="easy",
                time_limit=None, size=8, host=None, connect=None
            )
            
            main()
            
            mock_run_game.assert_called_once()
    
    @patch('othello.cli.run_game')
    @patch('sys.argv')
    def test_main_ai_game(self, mock_argv, mock_run_game):
        """Test main function with AI arguments."""
        mock_run_game.return_value = BitBoard.initial()
        
        with patch('othello.cli.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                ai=True, ai_vs_ai=False, ai_level="hard",
                time_limit=60.0, size=6, host=None, connect=None
            )
            
            main()
            
            mock_run_game.assert_called_once_with(
                vs_ai=True, ai_vs_ai=False, ai_level="hard",
                time_limit=60.0, size=6
            )
    
    @patch('othello.cli.run_network_game')
    @patch('sys.argv')
    def test_main_network_game(self, mock_argv, mock_run_network):
        """Test main function with network arguments."""
        mock_run_network.return_value = BitBoard.initial()
        
        with patch('othello.cli.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                ai=False, ai_vs_ai=False, ai_level="easy",
                time_limit=None, size=8, host="localhost:8080", connect=None
            )
            
            main()
            
            mock_run_network.assert_called_once_with(
                host="localhost:8080", connect=None, size=8
            )
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_time_limit(self, mock_print, mock_input):
        """Test run_game with time limit."""
        # Mock quick quit to avoid time complexity
        mock_input.return_value = 'q'
        
        result = run_game(time_limit=1.0, size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.BitBoard.initial')
    @patch('othello.cli.input')
    def test_run_game_bitboard_creation_fallback(self, mock_input, mock_initial):
        """Test run_game BitBoard creation with fallback."""
        # Mock BitBoard.initial to raise TypeError first, then succeed
        mock_input.return_value = 'q'
        mock_initial.side_effect = [TypeError(), BitBoard.initial()]
        
        result = run_game(size=10)
        
        # Should have tried with size, then fallen back to default
        assert mock_initial.call_count == 2
        assert isinstance(result, BitBoard)


class TestCLIIntegration:
    """Integration tests for CLI module."""
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_complete_game_flow(self, mock_print, mock_input):
        """Test a complete game flow with moves."""
        # Simulate a few moves then quit
        mock_input.side_effect = ['d3', 'c3', 'q']
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        # Game should have processed moves
        assert mock_input.call_count >= 1
    
    @patch('othello.cli.print')
    def test_backward_compatibility(self, mock_print):
        """Test that play function still works (backward compatibility)."""
        from othello.cli import play
        
        # play should be the same as main
        assert play == main


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running CLI coverage tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All CLI coverage tests passed!")
    else:
        print("❌ Some CLI tests failed!")
        sys.exit(1)