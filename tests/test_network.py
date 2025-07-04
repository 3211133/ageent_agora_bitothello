import socket
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from othello import network


def test_send_recv_line():
    s1, s2 = socket.socketpair()
    network.send_line(s1, "hello")
    assert network.recv_line(s2) == "hello"
    s1.close()
    s2.close()
