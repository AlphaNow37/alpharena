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
        if isinstance(args, str | bytes | int):
            args = (args,)
        head = action_type.value.to_bytes(1, "big")
        arglist = ACTIONS[action_type]
        if len(args) != len(arglist):
            raise ValueError(f"Invalid number of arguments for {action_type.name}: {len(args)} != {len(arglist)}")
        to_send = head
        for arg, (argtype, arglen, *options) in zip(args, arglist):
            assert isinstance(arg, argtype), f"{action_type.name} argument {arg} is not of type {argtype}"
            if argtype is str:
                barg = arg.encode("utf-8")
            elif argtype is int:
                signed = options[0] if options else False
                barg = arg.to_bytes(arglen, "big", signed=signed)
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
            print("args=", args)
            print(f"send {action_type.name} {to_send!r}")
        self.sock.sendall(to_send)

class Recever(threading.Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        self.sock = sock
        self.running = True
        self.events = EventGenerator()
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
                for argtype, arglen, *options in arglist:
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
                        signed = options[0] if options else False
                        arg = int.from_bytes(arg, "big", signed=signed)
                    elif argtype is bytes:
                        pass
                    else:
                        raise RuntimeError(f"unknown argtype {argtype}")
                    args.append(arg)

                if DEBUG:
                    print("recv by ", self.sock.getsockname())
                    print("recv from ", self.sock.getpeername())
                    print(f"recv {action_type.name} {args}")
                self.events.add(action_type, args)
        except Exception as e:
            if self.running:
                print("//")
                raise e

    def close(self):
        self.running = False
        self.sock.close()

class EventGenerator:
    def __init__(self):
        from collections import deque
        self.events = deque()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.events.popleft()
        except IndexError:
            raise StopIteration()

    def add(self, action_type, args):
        self.events.append((action_type, args))

class ActionTypes(enum.Enum):
    RESET = 0  # Client-> Server : (RESET)
    ERROR = 1  # Server-> Client : (ERROR)(lenght:1)(*str)
    STOP_GAME = 2  # ~~ : (STOP_GAME)
    MOVE_TO = 3  # ~~ : (MOVE_TO)(x:4)(y:4)
    OPP_MOVE_TO = 4  # Server-> Client : (OPPONENT_MOVE_TO)(x:4)(y:4)

    SHOOT = 5  # Client-> Server : (SHOOT)(x:4:-?)(y:4:-?)

    NEW_PROJECTILE = 6  # Server-> Client : (NEW_PROJECTILE)(id:3)
    PROJECTILE_MOVE_TO = 7  # Server-> Client : (PROJECTILE_MOVE_TO)(id:3)(x:4)(y:4)
    PROJECTILE_DESTROYED = 8  # Server-> Client : (PROJECTILE_DESTROYED)(id:3)

    SET_LIFE = 9  # Server-> Client : (SET_LIFE)(life:1)
    SET_OPP_LIFE = 10  # Server-> Client : (SET_OPP_LIFE)(life:1)

ACTIONS = {
    ActionTypes.RESET: [],
    ActionTypes.ERROR: [(str, None)],
    ActionTypes.STOP_GAME: [],
    ActionTypes.MOVE_TO: [(int, 4), (int, 4)],
    ActionTypes.OPP_MOVE_TO: [(int, 4), (int, 4)],
    ActionTypes.SHOOT: [(int, 4, True), (int, 4, True)],
    ActionTypes.NEW_PROJECTILE: [(int, 3)],
    ActionTypes.PROJECTILE_MOVE_TO: [(int, 3), (int, 4), (int, 4)],
    ActionTypes.PROJECTILE_DESTROYED: [(int, 3)],
    ActionTypes.SET_LIFE: [(int, 1)],
    ActionTypes.SET_OPP_LIFE: [(int, 1)],
}
