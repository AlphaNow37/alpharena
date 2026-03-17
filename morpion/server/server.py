import socket

from morpion.protocol import ActionTypes, send, RecvQueue
from morpion.server.morpion import ServerMorpion

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), 8080))
        self.sock.listen(5)

        self.conns = []
        self.queues = []

        self.run()

    def run(self):
        for _ in range(2):
            conn, addr = self.sock.accept()
            print(f'[+] {addr} connected')
            self.conns.append(conn)
            self.queues.append(RecvQueue(conn))
        while True:
            self.game = ServerMorpion()
            send(self.conns[0], ActionTypes.RESET)
            send(self.conns[1], ActionTypes.RESET)
            send(self.conns[0], ActionTypes.END)
            while not self.game.game_over:
                act_conn = self.conns[self.game.turn]
                act_queue = self.queues[self.game.turn]
                while True:
                    action_type, data = act_queue.get_last_event()
                    print(f'[+] {action_type.name} {data!r}')
                    if action_type is ActionTypes.END:
                        break
                    elif action_type is ActionTypes.PLAY:
                        case_id = int.from_bytes(data, 'big')
                        y, x = divmod(case_id, 3)
                        succes = self.game.play(x, y)
                        if succes:
                            bcase_id = case_id.to_bytes(1, 'big')
                            for i, conn in enumerate(self.conns):
                                turn = i != self.game.turn
                                bturn = turn.to_bytes(1, 'big')
                                send(conn, ActionTypes.PLAY, bcase_id + bturn)
                            if self.game.game_over:
                                for i, conn in enumerate(self.conns):
                                    if self.game.winner == -1:
                                        bwinner = (2).to_bytes(1, 'big')
                                    else:
                                        bwinner = (self.game.winner != i).to_bytes(1, 'big')
                                    send(conn, ActionTypes.GAME_OVER, bwinner)
                            else:
                                self.game.next_player()
                                send(self.conns[self.game.turn], ActionTypes.END)
                        else:
                            send(act_conn, ActionTypes.ERROR, "Case already played".encode("utf-8"))
                            send(act_conn, ActionTypes.END)

    def __del__(self):
        self.sock.close()
        for conn in self.conns:
            conn.close()
