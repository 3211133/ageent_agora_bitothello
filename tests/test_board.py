import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from othello.board import Board, BLACK, WHITE


class TestBoard(unittest.TestCase):
    def test_initial_counts(self):
        b = Board()
        black, white = b.count()
        self.assertEqual(black, 2)
        self.assertEqual(white, 2)

    def test_legal_moves_initial(self):
        b = Board()
        black_moves = b.moves_list(BLACK)
        white_moves = b.moves_list(WHITE)
        self.assertEqual(len(black_moves), 4)
        self.assertEqual(len(white_moves), 4)

    def test_apply_move(self):
        b = Board()
        moves = b.moves_list(BLACK)
        move = moves[0]
        self.assertTrue(b.apply_move(BLACK, move))
        black, white = b.count()
        self.assertEqual(black + white, 5)

if __name__ == '__main__':
    unittest.main()

