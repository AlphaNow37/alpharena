
class ServerMorpion:
    def __init__(self):
        self.board: list[list[int | None]] = [[None, None, None], [None, None, None], [None, None, None]]
        self.turn = 0
        self.winner = None
        self.game_over = False

    def play(self, x, y):
        if self.game_over:
            raise Exception("Game is over")
        if self.board[y][x] is not None:
            return False
        self.board[y][x] = self.turn
        self.check_game_over()
        return True

    def next_player(self):
        self.turn += 1
        self.turn %= 2

    def check_game_over(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] is not None:
                self.winner = self.board[i][0]
            elif self.board[0][i] == self.board[1][i] == self.board[2][i] is not None:
                self.winner = self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] is not None:
            self.winner = self.board[0][0]
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] is not None:
            self.winner = self.board[0][2]
        if self.winner is not None:
            if all(all(x is None for x in line) for line in self.board):
                self.winner = -1
        if self.winner is not None:
            self.game_over = True
