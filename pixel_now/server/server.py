import socket
from functools import partial

from pixel_now.protocol import ActionTypes, Sender, RecvQueue
from pixel_now.server.servergame import PixelNowServer
from pixel_now.constants import GRID_SIZE

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), 8080))
        self.sock.listen(5)

        self.senders = []
        self.queues = []

        self.run()

    def event(self, player_i, action_type: ActionTypes, args):
        print(f'[Event] {player_i} {action_type.name} {args}')
        if action_type is ActionTypes.PLAY:
            case_id, = args
            y, x = divmod(case_id, GRID_SIZE)
            if player_i == 1:
                y = GRID_SIZE - y - 1
            succes = self.game.play(x, y, player_i)
            if succes:
                self.senders[0].send(ActionTypes.CASE_CHANGE, (y * GRID_SIZE + x, player_i != 0))
                self.senders[1].send(ActionTypes.CASE_CHANGE, ((GRID_SIZE - y - 1) * GRID_SIZE + x, player_i != 1))
            else:
                self.senders[player_i].send(ActionTypes.ERROR, ("You can't play here", ))
        elif action_type is ActionTypes.STOP_GAME:
            self.game.stop()
            self.senders[not player_i].send(ActionTypes.STOP_GAME)
            del self
        elif action_type is ActionTypes.THREAD_EXCEPTION:
            self.game.stop()
            for sender in self.senders:
                sender.send(ActionTypes.STOP_GAME)
            raise args[0]

    def run(self):
        try:
            for i in range(2):
                conn, addr = self.sock.accept()
                print(f'[+] {addr} connected')
                self.senders.append(Sender(conn))
                self.queues.append(RecvQueue(conn, partial(self.event, i)))
            self.game = PixelNowServer(self.senders)
            self.game.run()
        finally:
            self.sock.close()
