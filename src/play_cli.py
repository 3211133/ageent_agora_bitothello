import sys
from board import Board
import random


def bit_to_pos(bit: int) -> str:
    idx = 0
    while bit >> idx:
        if bit & (1 << idx):
            break
        idx += 1
    row = idx // 8
    col = idx % 8
    return f"{chr(col + ord('a'))}{row + 1}"


def pos_to_bit(pos: str) -> int:
    col = ord(pos[0].lower()) - ord('a')
    row = int(pos[1]) - 1
    return 1 << (row * 8 + col)


def print_moves(moves: int):
    print("Legal moves:")
    for i in range(64):
        if moves & (1 << i):
            r = i // 8
            c = i % 8
            print(f" {chr(c + ord('a'))}{r + 1}", end='')
    print()


def main():
    board = Board.initial()
    player = 'black'
    while True:
        moves = board.legal_moves(player)
        if moves == 0:
            other_moves = board.legal_moves('white' if player == 'black' else 'black')
            if other_moves == 0:
                break
            print(f"{player} has no legal moves. Passing.")
            player = 'white' if player == 'black' else 'black'
            continue
        print(board)
        print_moves(moves)
        if player == 'black':
            pos = input('Enter move for black (e.g., d3): ').strip()
            move = pos_to_bit(pos)
        else:
            # simple random for white
            options = [1 << i for i in range(64) if moves & (1 << i)]
            move = random.choice(options)
            print(f"White plays {bit_to_pos(move)}")
        if not board.apply_move(player, move):
            print('Illegal move. Try again.')
            continue
        player = 'white' if player == 'black' else 'black'
    print('Game over:')
    print(board)


if __name__ == '__main__':
    main()
