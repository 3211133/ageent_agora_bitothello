"""Tests for network module to improve test coverage."""

import pytest
import socket
import sys
import time
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.network import host_game, join_game, send_line, recv_line


class TestNetworkFunctions:
    """Test suite for network module functions."""
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_host_game_successful_connection(self, mock_sleep, mock_socket_class):
        """Test host_game with successful connection."""
        # Mock socket and connection
        mock_socket = MagicMock()
        mock_conn = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.return_value = (mock_conn, ("127.0.0.1", 12345))
        
        result = host_game("localhost", 8080, accept_timeout=1.0)
        
        assert result == mock_conn
        mock_socket.bind.assert_called_once_with(("localhost", 8080))
        mock_socket.listen.assert_called_once_with(1)
        mock_socket.settimeout.assert_called_once_with(1.0)
        mock_conn.settimeout.assert_called_once()  # Security timeout set
        mock_socket.close.assert_called_once()
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_host_game_timeout_retry(self, mock_sleep, mock_socket_class):
        """Test host_game with timeout and retry logic."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # First call times out, second succeeds
        mock_conn = MagicMock()
        mock_socket.accept.side_effect = [
            socket.timeout(),
            (mock_conn, ("127.0.0.1", 12345))
        ]
        
        result = host_game("localhost", 8080, accept_timeout=0.1, retries=3)
        
        assert result == mock_conn
        assert mock_socket.accept.call_count == 2
        mock_sleep.assert_called_once()  # Should sleep between retries
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_host_game_timeout_exceeded(self, mock_sleep, mock_socket_class):
        """Test host_game when retries are exceeded."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.side_effect = socket.timeout()
        
        with pytest.raises(TimeoutError, match="Accept timed out and retries exceeded"):
            host_game("localhost", 8080, accept_timeout=0.1, retries=1)
        
        assert mock_socket.accept.call_count == 2  # Initial + 1 retry
        mock_socket.close.assert_called()
    
    @patch('othello.network.socket.socket')
    def test_host_game_socket_error(self, mock_socket_class):
        """Test host_game with socket error."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.bind.side_effect = socket.error("Address already in use")
        
        with pytest.raises(socket.error):
            host_game("localhost", 8080)
        
        mock_socket.close.assert_called()
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_join_game_successful_connection(self, mock_sleep, mock_socket_class):
        """Test join_game with successful connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        result = join_game("localhost", 8080, timeout=1.0)
        
        assert result == mock_socket
        mock_socket.settimeout.assert_has_calls([call(1.0), call(30.0)])  # Connect timeout, then read timeout
        mock_socket.connect.assert_called_once_with(("localhost", 8080))
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_join_game_connection_retry(self, mock_sleep, mock_socket_class):
        """Test join_game with connection retry logic."""
        # Mock multiple socket instances for retries
        mock_socket1 = MagicMock()
        mock_socket2 = MagicMock()
        mock_socket_class.side_effect = [mock_socket1, mock_socket2]
        
        # First connection fails, second succeeds
        mock_socket1.connect.side_effect = socket.timeout()
        
        result = join_game("localhost", 8080, timeout=0.1, retries=3)
        
        assert result == mock_socket2
        mock_socket1.close.assert_called_once()  # Failed socket should be closed
        mock_sleep.assert_called_once()
    
    @patch('othello.network.socket.socket')
    @patch('othello.network.time.sleep')
    def test_join_game_retries_exceeded(self, mock_sleep, mock_socket_class):
        """Test join_game when retries are exceeded."""
        mock_socket_class.return_value.connect.side_effect = socket.timeout()
        
        with pytest.raises(ConnectionError, match="Failed to connect after retries"):
            join_game("localhost", 8080, timeout=0.1, retries=1)
    
    @patch('othello.network.socket.socket')
    def test_join_game_socket_error(self, mock_socket_class):
        """Test join_game with socket error."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = socket.error("Connection refused")
        
        with pytest.raises(ConnectionError, match="Failed to connect after retries"):
            join_game("localhost", 8080, retries=0)
        
        mock_socket.close.assert_called()
    
    def test_send_line_successful(self):
        """Test send_line with successful transmission."""
        mock_socket = MagicMock()
        
        send_line(mock_socket, "test message")
        
        mock_socket.sendall.assert_called_once_with(b"test message\n")
    
    def test_send_line_with_size_validation(self):
        """Test send_line with size validation."""
        mock_socket = MagicMock()
        
        # Should work with short message
        send_line(mock_socket, "short", max_length=10)
        mock_socket.sendall.assert_called_once()
        
        # Should fail with long message
        with pytest.raises(ValueError, match="Message length .* exceeds maximum"):
            send_line(mock_socket, "very long message", max_length=5)
    
    def test_send_line_newline_validation(self):
        """Test send_line with newline validation."""
        mock_socket = MagicMock()
        
        with pytest.raises(ValueError, match="Message cannot contain newline characters"):
            send_line(mock_socket, "message\nwith\nnewlines")
    
    def test_send_line_socket_error(self):
        """Test send_line with socket error."""
        mock_socket = MagicMock()
        mock_socket.sendall.side_effect = socket.error("Connection lost")
        
        with pytest.raises(ConnectionError, match="Failed to send data"):
            send_line(mock_socket, "test")
    
    def test_recv_line_successful(self):
        """Test recv_line with successful reception."""
        mock_socket = MagicMock()
        # Mock receiving "hello" one byte at a time
        mock_socket.recv.side_effect = [b"h", b"e", b"l", b"l", b"o", b"\n"]
        
        result = recv_line(mock_socket)
        
        assert result == "hello"
        assert mock_socket.recv.call_count == 6
    
    def test_recv_line_with_size_limit(self):
        """Test recv_line with message size limit."""
        mock_socket = MagicMock()
        # Mock receiving long message
        mock_socket.recv.side_effect = [b"x"] * 1000  # Very long message
        
        with pytest.raises(ValueError, match="Message exceeds maximum length"):
            recv_line(mock_socket, max_length=100)
    
    def test_recv_line_connection_closed(self):
        """Test recv_line when connection is closed."""
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""  # Empty response indicates closed connection
        
        with pytest.raises(ConnectionError, match="Connection closed by remote host"):
            recv_line(mock_socket)
    
    def test_recv_line_empty_message(self):
        """Test recv_line with empty message validation."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b" ", b" ", b"\n"]  # Only whitespace
        
        with pytest.raises(ValueError, match="Empty message received"):
            recv_line(mock_socket)
    
    def test_recv_line_socket_timeout(self):
        """Test recv_line with socket timeout."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = socket.timeout()
        
        with pytest.raises(socket.timeout):
            recv_line(mock_socket)
    
    def test_recv_line_socket_error(self):
        """Test recv_line with socket error."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = socket.error("Network error")
        
        with pytest.raises(ConnectionError, match="Failed to receive data"):
            recv_line(mock_socket)
    
    def test_recv_line_unicode_error(self):
        """Test recv_line with invalid UTF-8."""
        mock_socket = MagicMock()
        # Mock invalid UTF-8 sequence
        mock_socket.recv.side_effect = [b"\xff", b"\xfe", b"\n"]
        
        with pytest.raises(ValueError, match="Invalid UTF-8 encoding"):
            recv_line(mock_socket)


class TestNetworkIntegration:
    """Integration tests for network module."""
    
    @patch('othello.network.socket.socket')
    def test_host_game_resource_cleanup_on_exception(self, mock_socket_class):
        """Test that host_game cleans up resources on exception."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.bind.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception):
            host_game("localhost", 8080)
        
        # Socket should be closed even on unexpected error
        mock_socket.close.assert_called()
    
    @patch('othello.network.socket.socket')
    def test_join_game_resource_cleanup_on_exception(self, mock_socket_class):
        """Test that join_game cleans up resources on exception."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.settimeout.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ConnectionError):  # Should be wrapped
            join_game("localhost", 8080, retries=0)
        
        # Socket should be closed on error
        mock_socket.close.assert_called()
    
    def test_send_recv_line_round_trip(self):
        """Test send_line and recv_line working together."""
        mock_socket = MagicMock()
        
        # Test send
        send_line(mock_socket, "test message")
        mock_socket.sendall.assert_called_once_with(b"test message\n")
        
        # Test receive with same message
        mock_socket.recv.side_effect = [bytes([b]) for b in b"test message\n"]
        result = recv_line(mock_socket)
        
        assert result == "test message"
    
    @patch('othello.network.socket.socket')
    def test_network_security_features(self, mock_socket_class):
        """Test network security features are applied."""
        mock_socket = MagicMock()
        mock_conn = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.return_value = (mock_conn, ("127.0.0.1", 12345))
        
        # Test host_game sets security timeout
        result = host_game("localhost", 8080, read_timeout=15.0)
        mock_conn.settimeout.assert_called_once_with(15.0)
        
        # Test join_game sets security timeout
        mock_socket.reset_mock()
        join_game("localhost", 8080, read_timeout=20.0)
        # Should set timeout twice: once for connection, once for read
        assert mock_socket.settimeout.call_count == 2
    
    def test_message_validation_comprehensive(self):
        """Test comprehensive message validation."""
        mock_socket = MagicMock()
        
        # Test various invalid messages for send_line
        invalid_send_cases = [
            ("too long message", 5, "exceeds maximum"),
            ("line\nwith\nnewlines", 100, "cannot contain newline"),
        ]
        
        for message, max_len, expected_error in invalid_send_cases:
            with pytest.raises(ValueError, match=expected_error):
                send_line(mock_socket, message, max_len)
        
        # Test invalid receive scenarios
        mock_socket.recv.side_effect = [b"\n"]  # Empty message
        with pytest.raises(ValueError, match="Empty message received"):
            recv_line(mock_socket)


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running network coverage tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All network coverage tests passed!")
    else:
        print("❌ Some network tests failed!")
        sys.exit(1)