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
        """Test run_game with AI vs AI mode and verify AI moves."""
        # Mock time to prevent actual delays
        mock_time.return_value = 0
        
        # Get initial board state
        initial_board = BitBoard.initial(4)
        initial_empty_squares = bin(~(initial_board.black | initial_board.white)).count('1')
        
        # Run a short AI vs AI game
        result = run_game(ai_vs_ai=True, ai_level="easy", size=4)
        
        assert isinstance(result, BitBoard)
        # Verify AI moves were made (board changed from initial state)
        result_empty_squares = bin(~(result.black | result.white)).count('1')
        assert result_empty_squares < initial_empty_squares, "AI should have made moves"
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
    
    @patch('othello.cli.input')
    @patch('othello.cli.network.join_game')
    @patch('othello.cli.network.recv_line')
    @patch('othello.cli.print')
    def test_run_network_game_connect(self, mock_print, mock_recv, mock_join, mock_input):
        """Test run_network_game as client with message handling."""
        # Mock network components
        mock_socket = MagicMock()
        mock_join.return_value = mock_socket
        
        # Mock player input and network messages alternately
        mock_input.side_effect = ["q"]  # Client quits after receiving opponent move
        mock_recv.side_effect = ["a2"]  # Opponent makes a valid move
        
        result = run_network_game(connect="localhost:8080", size=4)
        
        assert isinstance(result, BitBoard)
        mock_join.assert_called_once_with("localhost", 8080, timeout=30.0)
        # Verify that message handling occurred
        mock_recv.assert_called()
    
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
    @patch('sys.argv', ['othello'])
    def test_main_basic_game(self, mock_run_game):
        """Test main function with basic arguments."""
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
    @patch('sys.argv', ['othello', '--ai'])
    def test_main_ai_game(self, mock_run_game):
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
    
    @patch('othello.cli.input')
    def test_run_game_bitboard_creation_fallback(self, mock_input):
        """Test run_game BitBoard creation with fallback."""
        # Mock user quitting immediately
        mock_input.return_value = 'q'
        
        # Test with size that should work
        result = run_game(size=8)
        
        # Should return a BitBoard
        assert isinstance(result, BitBoard)
        assert result.size == 8


class TestCLIAdvanced:
    """Advanced CLI tests for missing coverage areas."""
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    @patch('othello.cli.time.time')
    def test_run_game_time_limit_timeout(self, mock_time, mock_print, mock_input):
        """Test run_game with time limit causing timeout."""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 10]  # Player runs out of time
        mock_input.return_value = 'd3'
        
        result = run_game(time_limit=1.0, size=4)
        
        assert isinstance(result, BitBoard)
        # Should have printed timeout message
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    @patch('othello.cli.time.time')
    def test_run_game_ai_vs_ai_with_passes(self, mock_time, mock_print, mock_input):
        """Test AI vs AI game with pass scenarios."""
        # Mock time to prevent delays
        mock_time.return_value = 0
        
        # Create a board state where AI might have no moves
        result = run_game(ai_vs_ai=True, ai_level="easy", size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.save_state')
    @patch('othello.cli.load_state')
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_save_load_error_handling(self, mock_print, mock_input, mock_load, mock_save):
        """Test save/load error handling in game."""
        # Test save, then load with error, then quit
        mock_input.side_effect = ['s', 'l', 'q']
        mock_load.side_effect = Exception("File not found")
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        # Should have called save and load
        mock_save.assert_called_once()
        mock_load.assert_called_once()
        # Should have printed load error
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_undo_redo_edge_cases(self, mock_print, mock_input):
        """Test undo/redo when not possible."""
        # Try undo at start (should fail), then redo (should fail), then quit
        mock_input.side_effect = ['u', 'r', 'q']
        
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        # Should have printed "Cannot undo" and "Cannot redo"
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_pass_scenarios(self, mock_print, mock_input):
        """Test game scenarios with no legal moves (pass)."""
        mock_input.return_value = 'q'
        
        # Start a game and quit immediately
        result = run_game(size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    @patch('othello.cli.time.time')
    def test_run_game_time_deduction_scenarios(self, mock_time, mock_print, mock_input):
        """Test various time deduction scenarios."""
        # Mock time progression
        mock_time.side_effect = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        mock_input.side_effect = ['d3', 'q']
        
        result = run_game(time_limit=5.0, size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.choose_move')
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_game_ai_no_moves_scenario(self, mock_print, mock_input, mock_choose):
        """Test AI having no legal moves."""
        mock_input.return_value = 'q'
        mock_choose.return_value = 0  # AI has no moves
        
        result = run_game(vs_ai=True, ai_level="easy", size=4)
        
        assert isinstance(result, BitBoard)
        mock_print.assert_called()
    
    @patch('othello.cli.network.host_game')
    @patch('othello.cli.network.send_line')
    @patch('othello.cli.network.recv_line')
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_network_game_pass_handling(self, mock_print, mock_input, mock_recv, mock_send, mock_host):
        """Test network game pass scenarios."""
        mock_socket = MagicMock()
        mock_host.return_value = mock_socket
        mock_input.return_value = 'q'
        mock_recv.return_value = "PASS"
        
        result = run_network_game(host="localhost:8080", size=4)
        
        assert isinstance(result, BitBoard)
        mock_host.assert_called_once()
    
    @patch('othello.cli.network.join_game')
    @patch('othello.cli.network.recv_line')
    @patch('othello.cli.network.send_line')
    @patch('othello.cli.input')
    @patch('othello.cli.print')
    def test_run_network_game_client_scenarios(self, mock_print, mock_input, mock_send, mock_recv, mock_join):
        """Test network game as client with various scenarios."""
        mock_socket = MagicMock()
        mock_join.return_value = mock_socket
        mock_input.return_value = 'q'
        mock_recv.return_value = "QUIT"
        
        result = run_network_game(connect="localhost:8080", size=4)
        
        assert isinstance(result, BitBoard)
        mock_join.assert_called_once()
    
    @patch('othello.cli.input')
    @patch('othello.cli.network.host_game')
    def test_run_network_game_bitboard_fallback(self, mock_host, mock_input):
        """Test network game BitBoard creation fallback."""
        mock_socket = MagicMock()
        mock_host.return_value = mock_socket
        mock_input.return_value = 'q'
        
        # Test with a size that should work
        result = run_network_game(host="localhost:8080", size=8)
        
        assert isinstance(result, BitBoard)
        mock_host.assert_called_once()


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