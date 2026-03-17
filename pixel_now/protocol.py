import socket
import enum
import threading

DEBUG = False
class Sender:
    def __init__(self, sock: socket.socket):
        self.sock = sock

    def send(self, action_type, args=()):
        if isinstance(action_type, str):
            action_type = ActionTypes[action_type]
        if not isinstance(args, tuple | list):
            args = (args,)
        head = action_type.value.to_bytes(1, "big")
        arglist = ACTIONS[action_type]
        if len(args) != len(arglist):
            raise ValueError(f"Invalid number of arguments for {action_type.name}: {len(args)} != {len(arglist)}")
        to_send = head
        for arg, (argtype, arglen) in zip(args, arglist):
            assert isinstance(arg, argtype)
            if argtype is str:
                barg = arg.encode("utf-8")
            elif argtype is int:
                barg = arg.to_bytes(arglen, "big")
            elif argtype is bytes:
                barg = arg
            else:
                raise ValueError(f"Invalid argument type {argtype}")
            if arglen is None:
                arglen = len(barg)
                to_send += arglen.to_bytes(1, "big")
            to_send += barg
        if DEBUG:
            print("start send. send by ", self.sock.getsockname())
            print("start send to ", self.sock.getpeername())
            print(f"send {action_type.name} {to_send!r}")
        self.sock.sendall(to_send)


class RecvQueue(threading.Thread):
    def __init__(self, sock: socket.socket, eventcaller):
        super().__init__()
        self.sock = sock
        self.eventcaller = eventcaller
        self.running = True
        self.start()

    def run(self):
        try:
            while self.running:
                head = self.sock.recv(1)
                if not head:
                    raise RuntimeError("recv head empty")
                action_type = ActionTypes(int.from_bytes(head, "big"))
                arglist = ACTIONS[action_type]
                args = []
                for argtype, arglen in arglist:
                    if arglen is None:
                        arg = self.sock.recv(1)
                        if not arg:
                            raise RuntimeError("recv arglen empty")
                        arglen = int.from_bytes(arg, "big")
                    arg = self.sock.recv(arglen)
                    if not arg:
                        raise RuntimeError("recv arg empty")
                    if argtype is str:
                        arg = arg.decode("utf-8")
                    elif argtype is int:
                        arg = int.from_bytes(arg, "big")
                    elif argtype is bytes:
                        pass
                    else:
                        raise RuntimeError(f"unknown argtype {argtype}")
                    args.append(arg)

                if DEBUG:
                    print("recv by ", self.sock.getsockname())
                    print("recv from ", self.sock.getpeername())
                    print(f"recv {action_type.name} {args}")
                self.eventcaller(action_type, args)
        except BaseException as e:
            self.eventcaller(ActionTypes.THREAD_EXCEPTION, (e,))
        finally:
            self.sock.close()

class ActionTypes(enum.Enum):
    PLAY = 0  # Client-> Server : (PLAY)(case_id:4)
    RESET = 1  # Client-> Server : (RESET)
    ERROR = 2  # Server-> Client : (ERROR)(lenght:1)(*str)
    GAME_OVER = 3  # Server-> Client : (GAME_OVER)(winner:1)
    STOP_GAME = 4  # ~~ : (STOP_GAME)
    CASE_CHANGE = 5  # Server-> Client : (CASE_CHANGE)(case_id:4)(new_case:1)
    SET_ENERGY = 6  # Client-> Server : (SET_ENERGY)(energy:1)

    THREAD_EXCEPTION = 7

ACTIONS = {
    ActionTypes.PLAY: [(int, 4)],
    ActionTypes.RESET: [],
    ActionTypes.ERROR: [(str, None)],
    ActionTypes.GAME_OVER: [(int, 1)],
    ActionTypes.STOP_GAME: [],
    ActionTypes.CASE_CHANGE: [(int, 4), (int, 1)],
    ActionTypes.SET_ENERGY: [(int, 1)],
}
