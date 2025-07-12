"""Network communication module for Othello game.

SECURITY WARNING: This module implements unencrypted network communication.
For production use, consider:
1. Implementing TLS/SSL encryption
2. Adding authentication mechanisms  
3. Using secure protocols (WebSocket over HTTPS)
4. Implementing rate limiting
5. Adding input sanitization beyond basic validation

The current implementation includes basic protections against:
- Message size attacks (DoS prevention)
- Slow-loris attacks (timeout protection)
- Basic input validation
- Resource cleanup

However, all communication is transmitted in plaintext and can be
intercepted, modified, or replayed by malicious actors.
"""

import socket
import logging
import time

# Module level logger
logger = logging.getLogger(__name__)


def host_game(
    host: str = "localhost",
    port: int = 9999,
    accept_timeout: float = 10.0,
    retries: int = 3,
    retry_delay: float = 1.0,
    read_timeout: float = 30.0,
) -> socket.socket:
    """Wait for a connection and return the accepted socket.

    The server will retry ``retries`` times if no connection is received within
    ``accept_timeout`` seconds. ``read_timeout`` sets the socket timeout for
    subsequent read operations to prevent hanging on malicious slow connections.
    """
    srv = None
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(1)
        srv.settimeout(accept_timeout)

        attempt = 0
        while True:
            try:
                logger.info(f"Waiting for connection on {host}:{port}...")
                conn, addr = srv.accept()
                logger.info(f"Connected to {addr}")
                srv.close()
                
                # Set read timeout for security (prevent slow-loris attacks)
                conn.settimeout(read_timeout)
                return conn
            except socket.timeout:
                attempt += 1
                logger.warning("Accept timed out")
                if attempt > retries:
                    if srv:
                        srv.close()
                    raise TimeoutError("Accept timed out and retries exceeded")
                time.sleep(retry_delay)
    except socket.error as e:
        if srv:
            srv.close()
        logger.error(f"Network error while hosting game: {e}")
        raise
    except Exception as e:
        if srv:
            srv.close()
        logger.error(f"Unexpected error while hosting game: {e}")
        raise


def join_game(
    host: str = "localhost",
    port: int = 9999,
    timeout: float = 10.0,
    retries: int = 3,
    retry_delay: float = 1.0,
    read_timeout: float = 30.0,
) -> socket.socket:
    """Connect to an existing game and return the socket.

    The connection will be attempted ``retries`` times. ``timeout`` specifies the
    timeout for each connection attempt. ``read_timeout`` sets the socket timeout
    for subsequent read operations to prevent hanging on malicious slow connections.
    """
    attempt = 0
    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            logger.info(f"Connecting to {host}:{port} (attempt {attempt + 1})...")
            sock.connect((host, port))
            logger.info(f"Successfully connected to {host}:{port}")
            
            # Set read timeout for security (prevent slow-loris attacks)
            sock.settimeout(read_timeout)
            return sock
        except socket.timeout:
            logger.warning(f"Connection timeout after {timeout} seconds")
            if sock:
                sock.close()
        except socket.error as e:
            logger.error(f"Network error while joining game: {e}")
            if sock:
                sock.close()
        except Exception as e:
            logger.error(f"Unexpected error while joining game: {e}")
            if sock:
                sock.close()
                
        attempt += 1
        if attempt > retries:
            raise ConnectionError("Failed to connect after retries")
        time.sleep(retry_delay)


def send_line(sock: socket.socket, line: str, max_length: int = 1024) -> None:
    """Send a line of text ending with a newline with size validation.
    
    Args:
        sock: Socket to send to
        line: Message to send
        max_length: Maximum message length for validation
        
    Raises:
        ValueError: If message exceeds size limit
        ConnectionError: If sending fails
    """
    try:
        # Validate message length before sending
        if len(line) > max_length:
            raise ValueError(f"Message length {len(line)} exceeds maximum {max_length}")
        
        # Validate message content for basic safety
        if '\n' in line:
            raise ValueError("Message cannot contain newline characters")
            
        message = line + "\n"
        sock.sendall(message.encode('utf-8'))
    except socket.error as e:
        logger.error(f"Error sending data: {e}")
        raise ConnectionError(f"Failed to send data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while sending: {e}")
        raise


def recv_line(sock: socket.socket, max_length: int = 1024) -> str:
    """Receive a newline terminated line of text with size limits.
    
    Args:
        sock: Socket to receive from
        max_length: Maximum message length to prevent DoS attacks
        
    Raises:
        ConnectionError: If connection issues occur
        ValueError: If message exceeds size limit
    """
    try:
        data = b""
        while not data.endswith(b"\n"):
            # Check size limit before receiving more data
            if len(data) >= max_length:
                raise ValueError(f"Message exceeds maximum length of {max_length} bytes")
            
            chunk = sock.recv(1)
            if not chunk:
                raise ConnectionError("Connection closed by remote host")
            data += chunk
            
        # Remove newline and decode
        message = data[:-1].decode('utf-8')
        
        # Additional validation for game protocol
        if len(message.strip()) == 0:
            raise ValueError("Empty message received")
            
        return message
    except socket.timeout:
        logger.warning("Timeout while receiving data")
        raise
    except socket.error as e:
        logger.error(f"Network error while receiving: {e}")
        raise ConnectionError(f"Failed to receive data: {e}")
    except UnicodeDecodeError as e:
        logger.error(f"Invalid text encoding received: {e}")
        raise ValueError(f"Invalid UTF-8 encoding: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while receiving: {e}")
        raise
