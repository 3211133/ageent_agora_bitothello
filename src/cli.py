from othello.board import Board


def main():
    board = Board()
    player = 'black'
    while True:
        moves = board.legal_moves(player)
        if not moves:
            break
        print(f"{player}'s turn. Legal moves: {moves}")
        pos = int(input('Enter move position (0-63): '))
        board.apply_move(player, pos)
        player = 'white' if player == 'black' else 'black'


if __name__ == '__main__':
    main()
