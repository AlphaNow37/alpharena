import socket

from pixel_now.client.clientgame import PixelNowClient
from pixel_now.protocol import Sender, RecvQueue, ActionTypes
from pixel_now.constants import GRID_SIZE

class Client:
    def __init__(self):
        try:
            self.game = PixelNowClient(self.play_at)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((socket.gethostname(), 8080))
            print("Client in port ", self.sock.getsockname())
            self.queue = RecvQueue(self.sock, self.event)
            self.sender = Sender(self.sock)
            self.stopped = False

            self.game.run()
            if not self.stopped:
                self.sender.send(ActionTypes.STOP_GAME)
        finally:
            self.sock.close()

    def event(self, action_type: ActionTypes, args: tuple):
        print(f"[Event] {action_type}{args}")
        if action_type is ActionTypes.RESET:
            self.game.reset()
        elif action_type is ActionTypes.CASE_CHANGE:
            case_id, player = args
            y, x = divmod(case_id, GRID_SIZE)
            self.game.play_at(x, y, player)
        elif action_type is ActionTypes.STOP_GAME:
            self.stopped = True
            self.game.stop()
        elif action_type is ActionTypes.SET_ENERGY:
            self.game.energy = args[0]
        elif action_type is ActionTypes.ERROR:
            self.game.error(args[0])
        elif action_type is ActionTypes.THREAD_EXCEPTION:
            self.game.stop()
            raise args[0]

    def play_at(self, x: int, y: int):
        case_id = y * GRID_SIZE + x
        self.sender.send(ActionTypes.PLAY, (case_id,))
