"""Security tests for input validation vulnerabilities."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from othello.board import BitBoard, parse_move
from othello.cli import _validate_network_move, _parse_host_port


class TestInputValidationSecurity:
    """Test suite for input validation security fixes."""
    
    def test_parse_move_bounds_checking(self):
        """Test that parse_move properly validates bounds."""
        # Valid moves should work
        valid_moves = [
            ('d3', 8),
            ('A1', 8),
            ('h8', 8),
            ('a1', 6),
            ('f6', 6)
        ]
        
        for move, size in valid_moves:
            result = parse_move(move, size)
            assert isinstance(result, int)
            assert result > 0
    
    def test_parse_move_invalid_input_types(self):
        """Test that parse_move rejects invalid input types."""
        invalid_inputs = [
            (123, 8),           # Integer instead of string
            (None, 8),          # None
            ([], 8),            # List
            ('d3', '8'),        # String size instead of int
            ('d3', None),       # None size
            ('d3', 3.14),       # Float size
        ]
        
        for move, size in invalid_inputs:
            with pytest.raises(TypeError):
                parse_move(move, size)
    
    def test_parse_move_invalid_board_sizes(self):
        """Test that parse_move rejects invalid board sizes."""
        invalid_sizes = [
            0, 1, 2, 3,         # Too small
            27, 50, 100,        # Too large  
            5, 7, 9,            # Odd numbers
            -1, -8,             # Negative
        ]
        
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                parse_move('d3', size)
    
    def test_parse_move_invalid_formats(self):
        """Test that parse_move rejects invalid move formats."""
        invalid_moves = [
            '',                 # Empty string
            '   ',              # Whitespace only
            'd',                # Too short
            '33',               # No letter
            'dd',               # No number
            'd3x',              # Extra characters
            '99',               # Invalid format
            'z1',               # Column out of bounds
            'd0',               # Row 0 (invalid)
            'd99',              # Row too high
            'i1',               # Column out of bounds for 8x8
        ]
        
        for move in invalid_moves:
            with pytest.raises(ValueError):
                parse_move(move, 8)
    
    def test_parse_move_bounds_validation(self):
        """Test that parse_move validates coordinate bounds."""
        # Test column bounds
        with pytest.raises(ValueError, match="Column.*out of bounds"):
            parse_move('i1', 8)  # Column 'i' is out of bounds for 8x8
        
        with pytest.raises(ValueError, match="Column.*out of bounds"):
            parse_move('z1', 8)  # Way out of bounds
        
        # Test row bounds
        with pytest.raises(ValueError, match="Row.*out of bounds"):
            parse_move('a0', 8)  # Row 0 is invalid
            
        with pytest.raises(ValueError, match="Row.*out of bounds"):
            parse_move('a9', 8)  # Row 9 is out of bounds for 8x8
            
        with pytest.raises(ValueError, match="Row.*out of bounds"):
            parse_move('a99', 8)  # Way out of bounds
    
    def test_network_move_validation(self):
        """Test network move validation security."""
        # Valid network moves
        valid_moves = ['d3', 'A1', 'h8', 'PASS']
        
        for move in valid_moves[:3]:  # Skip PASS for now
            result = _validate_network_move(move, 8)
            assert isinstance(result, int)
    
    def test_network_move_security_checks(self):
        """Test that network move validation blocks malicious input."""
        malicious_inputs = [
            'a' * 50,                    # Too long
            'd3\x00',                    # Null byte
            'd3\r\n',                    # Carriage return/newline
            'd3\t',                      # Tab character
            'script',                    # Suspicious keyword
            'eval()',                    # Code injection attempt
            'exec("print(1)")',          # Code execution attempt
            'import os',                 # Import statement
            'd3\x08\x0c',               # Control characters
        ]
        
        for malicious in malicious_inputs:
            with pytest.raises(ValueError):
                _validate_network_move(malicious, 8)
    
    def test_network_move_type_validation(self):
        """Test that network move validation checks input types."""
        invalid_types = [
            123,           # Integer
            None,          # None
            [],            # List
            {},            # Dict
            3.14,          # Float
        ]
        
        for invalid_input in invalid_types:
            with pytest.raises(TypeError):
                _validate_network_move(invalid_input, 8)
    
    def test_host_port_validation(self):
        """Test host:port parsing validation."""
        # Valid cases
        valid_cases = [
            'localhost:8080',
            '192.168.1.1:9999',
            'example.com:80',
            '127.0.0.1:1234'
        ]
        
        for case in valid_cases:
            host, port = _parse_host_port(case)
            assert isinstance(host, str)
            assert isinstance(port, int)
            assert 1 <= port <= 65535
    
    def test_host_port_invalid_formats(self):
        """Test that host:port parsing rejects invalid formats."""
        invalid_cases = [
            '',                    # Empty
            'localhost',           # No port
            ':8080',              # No host
            'localhost:',         # Empty port
            'localhost:abc',      # Non-numeric port
            'localhost:0',        # Port 0
            'localhost:65536',    # Port too high
            'localhost:-1',       # Negative port
            'localhost:8080:extra', # Extra parts
        ]
        
        for case in invalid_cases:
            with pytest.raises(ValueError):
                _parse_host_port(case)
    
    def test_bitboard_initial_size_validation(self):
        """Test that BitBoard.initial validates size parameter."""
        # Valid sizes
        valid_sizes = [4, 6, 8, 10, 12, 16, 20, 26]
        
        for size in valid_sizes:
            board = BitBoard.initial(size)
            assert board.size == size
    
    def test_bitboard_initial_invalid_sizes(self):
        """Test that BitBoard.initial rejects invalid sizes."""
        invalid_sizes = [
            0, 1, 2, 3,         # Too small
            27, 50, 100,        # Too large
            5, 7, 9,            # Odd numbers
            -1, -8,             # Negative
        ]
        
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                BitBoard.initial(size)
    
    def test_bitboard_initial_type_validation(self):
        """Test that BitBoard.initial validates input types."""
        invalid_types = [
            '8',           # String
            8.0,           # Float
            None,          # None
            [],            # List
            {},            # Dict
        ]
        
        for invalid_type in invalid_types:
            with pytest.raises(TypeError):
                BitBoard.initial(invalid_type)
    
    def test_edge_case_coordinate_parsing(self):
        """Test edge cases in coordinate parsing."""
        # Test boundary coordinates for different board sizes
        sizes_and_bounds = [
            (4, 'a1', 'd4'),
            (6, 'a1', 'f6'), 
            (8, 'a1', 'h8'),
            (10, 'a1', 'j10'),
        ]
        
        for size, min_coord, max_coord in sizes_and_bounds:
            # Valid boundary coordinates should work
            parse_move(min_coord, size)
            parse_move(max_coord, size)
            
            # Just outside bounds should fail
            if size < 26:  # Only test if there's a next letter
                next_col = chr(ord(max_coord[0]) + 1)
                with pytest.raises(ValueError):
                    parse_move(f'{next_col}1', size)
            
            next_row = int(max_coord[1:]) + 1
            with pytest.raises(ValueError):
                parse_move(f'a{next_row}', size)
    
    def test_injection_attack_patterns(self):
        """Test various injection attack patterns in input validation."""
        injection_patterns = [
            # Command injection attempts
            'd3; rm -rf /',
            'd3 && echo evil',
            'd3 | cat /etc/passwd',
            'd3 `whoami`',
            'd3 $(id)',
            
            # Path traversal in move strings
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            
            # Unicode/encoding attacks
            'd3\u0000',
            'd3\u202e',  # Right-to-left override
            'd3\ufeff',  # Zero-width no-break space
            
            # Format string attacks
            'd3%s%s%s',
            'd3{0}{1}',
            
            # SQL injection patterns (unlikely but test anyway)
            "d3'; DROP TABLE users; --",
            "d3 OR 1=1",
        ]
        
        for pattern in injection_patterns:
            with pytest.raises(ValueError):
                parse_move(pattern, 8)
            
            # Also test through network validation
            with pytest.raises(ValueError):
                _validate_network_move(pattern, 8)


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys
    
    print("Running input validation security tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ])
    
    if result.returncode == 0:
        print("✅ All input validation security tests passed!")
    else:
        print("❌ Some security tests failed!")
        sys.exit(1)