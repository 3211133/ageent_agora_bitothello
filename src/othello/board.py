class Board:
    SIZE = 8

    def __init__(self):
        self.black = 0
        self.white = 0
        mid = Board.SIZE // 2
        self.set_disc(mid - 1, mid - 1, 'white')
        self.set_disc(mid, mid, 'white')
        self.set_disc(mid - 1, mid, 'black')
        self.set_disc(mid, mid - 1, 'black')

    def set_disc(self, x, y, color):
        pos = y * Board.SIZE + x
        if color == 'black':
            self.black |= 1 << pos
        else:
            self.white |= 1 << pos

    def get_disc(self, x, y):
        pos = y * Board.SIZE + x
        if self.black & (1 << pos):
            return 'black'
        if self.white & (1 << pos):
            return 'white'
        return None

    def legal_moves(self, color):
        moves = []
        for y in range(Board.SIZE):
            for x in range(Board.SIZE):
                if self.get_disc(x, y) is not None:
                    continue
                if self._would_flip(x, y, color):
                    moves.append(y * Board.SIZE + x)
        return moves

    def _would_flip(self, x, y, color):
        opp = 'white' if color == 'black' else 'black'
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            flipped = False
            while 0 <= nx < Board.SIZE and 0 <= ny < Board.SIZE:
                c = self.get_disc(nx, ny)
                if c == opp:
                    flipped = True
                elif c == color and flipped:
                    return True
                else:
                    break
                nx += dx
                ny += dy
        return False

    def apply_move(self, color, pos):
        x, y = pos % Board.SIZE, pos // Board.SIZE
        if not self._would_flip(x, y, color):
            raise ValueError('Illegal move')
        opp = 'white' if color == 'black' else 'black'
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            discs = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < Board.SIZE and 0 <= ny < Board.SIZE:
                c = self.get_disc(nx, ny)
                if c == opp:
                    discs.append((nx, ny))
                elif c == color:
                    for fx, fy in discs:
                        self.set_disc(fx, fy, color)
                    break
                else:
                    break
                nx += dx
                ny += dy
        self.set_disc(x, y, color)
