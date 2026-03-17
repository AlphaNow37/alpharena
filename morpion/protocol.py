import socket
import enum
import threading

DEBUG = False

def send(sock: socket.socket, action_type, message=b""):
    if isinstance(action_type, str):
        action_type = ActionTypes[action_type]
    head = action_type.value.to_bytes(1, "big")
    if DEBUG:
        print("start send. send by ", sock.getsockname())
        print("start send to ", sock.getpeername())
        print(f"send {action_type.name} {head!r} {message!r}")
    sock.send(head)
    if action_type not in NO_ARGS_ACTIONS:
        sock.send(len(message).to_bytes(1, "big"))
        sock.send(message)

class RecvQueue(threading.Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        self.sock = sock
        self.waiting: list[tuple[ActionTypes, bytes]] = []
        self.waiting_event = threading.Event()
        self.start()

    def run(self):
        while True:
            head = self.sock.recv(1)
            action_type = ActionTypes(int.from_bytes(head, "big"))
            if action_type in NO_ARGS_ACTIONS:
                self.waiting.append((action_type, b""))
            else:
                lenght = int.from_bytes(self.sock.recv(1), "big")
                message = self.sock.recv(lenght)
                self.waiting.append((action_type, message))
            self.waiting_event.set()

    def get_last_event(self):
        if len(self.waiting) == 0:
            self.waiting_event.clear()
            self.waiting_event.wait()
        return self.waiting.pop(0)

class ActionTypes(enum.Enum):
    END = 0
    PLAY = 1
    RESET = 2
    ERROR = 3
    GAME_OVER = 4

NO_ARGS_ACTIONS = [ActionTypes.END, ActionTypes.RESET]
