import socket


def host_game(host: str = "localhost", port: int = 9999) -> socket.socket:
    """Wait for a connection and return the accepted socket."""
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(1)
        logger.info(f"Waiting for connection on {host}:{port}...")
        conn, addr = srv.accept()
        logger.info(f"Connected to {addr}")
        srv.close()
        return conn
    except socket.error as e:
        logger.error(f"Network error while hosting game: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while hosting game: {e}")
        raise


def join_game(host: str = "localhost", port: int = 9999, timeout: float = 10.0) -> socket.socket:
    """Connect to an existing game and return the socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))
        print(f"Successfully connected to {host}:{port}")
        sock.settimeout(None)  # Remove timeout after connection
        return sock
    except socket.timeout:
        print(f"Connection timeout after {timeout} seconds")
        raise
    except socket.error as e:
        print(f"Network error while joining game: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while joining game: {e}")
        raise


def send_line(sock: socket.socket, line: str) -> None:
    """Send a line of text ending with a newline."""
    try:
        sock.sendall((line + "\n").encode())
    except socket.error as e:
        print(f"Error sending data: {e}")
        raise ConnectionError(f"Failed to send data: {e}")
    except Exception as e:
        print(f"Unexpected error while sending: {e}")
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
        print("Timeout while receiving data")
        raise
    except socket.error as e:
        print(f"Network error while receiving: {e}")
        raise ConnectionError(f"Failed to receive data: {e}")
    except UnicodeDecodeError as e:
        print(f"Invalid text encoding received: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while receiving: {e}")
        raise
