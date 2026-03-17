
SYMBOLS = ["X", "O"]
class ClientMorpion:
    def __init__(self):
        self.board: list[list[None | int]] = [[None, None, None], [None, None, None], [None, None, None]]
        print(self)
        print("Nouvelle partie")

    def __setitem__(self, key, value):
        x, y = key
        self.board[y][x] = value
        print(f"{SYMBOLS[value]} joue en {x+1} {y+1}")

    def __str__(self):
        return "\n".join(
            " ".join("/" if case is None else SYMBOLS[case]
                     for case in line)
            for line in self.board
        )

    def show(self):
        print(self)

    @staticmethod
    def clame_winner(winner):
        print("Game Over")
        if winner == -1:
            print("Match nul")
        else:
            print(f"{SYMBOLS[winner]} a gagné")

    @staticmethod
    def input():
        while True:
            coords = input("x y").replace(" ", "")
            if len(coords) != 2:
                print("Vous devez entrer deux chiffres séparées par un espace")
                continue
            x, y = coords
            if not x.isdigit() or not y.isdigit():
                print("Vous devez entrer deux chiffres")
                continue
            x, y = int(x) - 1, int(y) - 1
            if (not 0 <= x < 3) or (not 0 <= y < 3):
                print("Vous devez entrer des coordonnées valides")
                continue
            break
        return x, y
