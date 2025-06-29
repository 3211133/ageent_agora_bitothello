import unittest
from src.board import Board

class TestBoard(unittest.TestCase):
    def test_initial_position(self):
        board = Board.initial()
        self.assertEqual(bin(board.black).count('1'), 2)
        self.assertEqual(bin(board.white).count('1'), 2)

    def test_legal_moves_initial(self):
        board = Board.initial()
        moves_black = board.legal_moves('black')
        moves_white = board.legal_moves('white')
        # Starting position: black has 4 moves, white has 4 moves
        self.assertEqual(bin(moves_black).count('1'), 4)
        self.assertEqual(bin(moves_white).count('1'), 4)

if __name__ == '__main__':
    unittest.main()
