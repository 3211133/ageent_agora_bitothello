import socket


def host_game(host: str = "localhost", port: int = 9999) -> socket.socket:
    """Wait for a connection and return the accepted socket."""
    # TODO: handle network errors and retries gracefully
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((host, port))
    srv.listen(1)
    conn, _ = srv.accept()
    return conn


def join_game(host: str = "localhost", port: int = 9999) -> socket.socket:
    """Connect to an existing game and return the socket."""
    # TODO: support connection timeout and error handling
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def send_line(sock: socket.socket, line: str) -> None:
    """Send a line of text ending with a newline."""
    # NOTE: assumes socket is connected and writable
    sock.sendall((line + "\n").encode())


def recv_line(sock: socket.socket) -> str:
    """Receive a newline terminated line of text."""
    # REVIEW: consider buffering for performance
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data.strip().decode()
