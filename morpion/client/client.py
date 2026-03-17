import socket

from morpion.client.morpion import ClientMorpion
from morpion.protocol import send, RecvQueue, ActionTypes

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((socket.gethostname(), 8080))
        print("Client in port ", self.sock.getsockname())
        self.queue = RecvQueue(self.sock)

        self.run()

    def run(self):
        while True:
            action_type, data = self.queue.get_last_event()
            print(f"[Client] Received {action_type.name} {data!r}")
            if action_type is ActionTypes.RESET:
                self.game = ClientMorpion()
            elif action_type is ActionTypes.PLAY:
                bcase_id, bturn = data
                case_id = int(bcase_id)
                y, x = divmod(case_id, 3)
                turn = int(bturn)
                self.game[x, y] = turn
                self.game.show()
            elif action_type is ActionTypes.END:
                x, y = self.game.input()
                send(self.sock, ActionTypes.PLAY, (3*y+x).to_bytes(1, 'big'))
                send(self.sock, ActionTypes.END)
            elif action_type is ActionTypes.GAME_OVER:
                winner = int.from_bytes(data, 'big')
                if winner == 2:
                    winner = -1
                self.game.clame_winner(winner)
            elif action_type is ActionTypes.ERROR:
                print("Erreur: ", data.decode("utf-8"))

    def __del__(self):
        self.sock.close()
