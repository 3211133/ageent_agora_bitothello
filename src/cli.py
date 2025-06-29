from othello.board import Board


def main():
    board = Board()
    player = 'black'
    while True:
        moves = board.legal_moves(player)
        if not moves:
            break
        print(f"{player}'s turn. Legal moves: {moves}")
        while True:
            try:
                pos = int(input('Enter move position (0-63): '))
                if pos not in range(64):
                    print("Invalid input. Please enter a number between 0 and 63.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        board.apply_move(player, pos)
        player = 'white' if player == 'black' else 'black'


if __name__ == '__main__':
    main()
