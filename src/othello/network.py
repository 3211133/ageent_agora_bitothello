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
) -> socket.socket:
    """Wait for a connection and return the accepted socket.

    The server will retry ``retries`` times if no connection is received within
    ``accept_timeout`` seconds.
    """
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
                return conn
            except socket.timeout:
                attempt += 1
                logger.warning("Accept timed out")
                if attempt > retries:
                    raise TimeoutError("Accept timed out and retries exceeded")
                time.sleep(retry_delay)
    except socket.error as e:
        logger.error(f"Network error while hosting game: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while hosting game: {e}")
        raise


def join_game(
    host: str = "localhost",
    port: int = 9999,
    timeout: float = 10.0,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> socket.socket:
    """Connect to an existing game and return the socket.

    The connection will be attempted ``retries`` times. ``timeout`` specifies the
    timeout for each connection attempt.
    """
    attempt = 0
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            logger.info(f"Connecting to {host}:{port} (attempt {attempt + 1})...")
            sock.connect((host, port))
            logger.info(f"Successfully connected to {host}:{port}")
            sock.settimeout(None)  # Remove timeout after connection
            return sock
        except socket.timeout:
            logger.warning(f"Connection timeout after {timeout} seconds")
        except socket.error as e:
            logger.error(f"Network error while joining game: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while joining game: {e}")
        attempt += 1
        if attempt > retries:
            raise ConnectionError("Failed to connect after retries")
        time.sleep(retry_delay)


def send_line(sock: socket.socket, line: str) -> None:
    """Send a line of text ending with a newline."""
    try:
        sock.sendall((line + "\n").encode())
    except socket.error as e:
        logger.error(f"Error sending data: {e}")
        raise ConnectionError(f"Failed to send data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while sending: {e}")
        raise


def recv_line(sock: socket.socket) -> str:
    """Receive a newline terminated line of text."""
    try:
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(1)
            if not chunk:
                raise ConnectionError("Connection closed by remote host")
            data += chunk
        return data.strip().decode()
    except socket.timeout:
        logger.warning("Timeout while receiving data")
        raise
    except socket.error as e:
        logger.error(f"Network error while receiving: {e}")
        raise ConnectionError(f"Failed to receive data: {e}")
    except UnicodeDecodeError as e:
        logger.error(f"Invalid text encoding received: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while receiving: {e}")
        raise
