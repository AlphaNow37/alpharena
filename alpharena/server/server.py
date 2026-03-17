import socket
import time

from alpharena.protocol import ActionTypes, Sender, Recever
from alpharena.server.player import Player
from alpharena.map import Map

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), 8080))
        self.sock.listen(5)

        self.senders = []
        self.recevers = []
        self.event_queues = []

        self.send_stop_message = True
        self.running = True
        self._last_update = time.time()
        self.projectiles = {}
        try:
            self.run()
        finally:
            if self.send_stop_message:
                for sender in self.senders:
                    sender.send(ActionTypes.STOP_GAME)
            for r in self.recevers:
                r.running = False
            time.sleep(0.5)
            for r in self.recevers:
                r.close()
            self.sock.close()
            print('[-] Server closed')

    def run(self):
        for i in range(2):
            conn, addr = self.sock.accept()
            print(f'[+] {addr} connected')
            recever = Recever(conn)
            sender = Sender(conn)
            self.senders.append(sender)
            self.recevers.append(recever)
            self.event_queues.append(recever.events)
        self.reset()
        while self.running:
            self.events()
            self.update()

    def events(self):
        for player_i, queue in enumerate(self.event_queues):
            conn_sender: Sender = self.senders[player_i]
            other_sender: Sender = self.senders[not player_i]
            player = self.players[player_i]
            for action_type, args in queue:
                print(f'[Event] {player_i} {action_type.name} {args}')
                if action_type is ActionTypes.STOP_GAME:
                    self.send_stop_message = False
                    self.running = False
                    other_sender.send(ActionTypes.STOP_GAME)
                elif action_type is ActionTypes.ERROR:
                    text = args[0]
                    conn_sender.send(ActionTypes.ERROR, f"Server: {text}")
                elif action_type is ActionTypes.MOVE_TO:
                    x, y = args
                    succes = player.move_to(x/128, y/128)
                    if not succes:
                        conn_sender.send(ActionTypes.MOVE_TO, player.pos_to_int())
                elif action_type is ActionTypes.SHOOT:
                    x, y = args
                    succes = player.shoot(x/128, y/128)
                    if not succes:
                        conn_sender.send(ActionTypes.ERROR, "Impossible de tirer...")

    def update(self):
        act_time = time.time()
        if act_time - self._last_update > 1/20:
            for proj in list(self.projectiles.values()):
                proj.update()
                if proj.finished:
                    del self.projectiles[proj.id]
                    proj.destroy()
            self._last_update = act_time
            for player in self.players:
                player.life += 0.2

    def reset(self):
        self.map = Map("map")
        starting_positions = self.map.starting_pos
        for id_, proj in getattr(self, 'projectiles', {}).items():
            proj.finished = True
        self.players: list[Player] = [
            Player(i, self.senders[i], self.senders[not i], self.map, starting_positions[i], self.projectiles, self.reset)
            for i in range(2)
        ]
        self.players[0].opponent = self.players[1]
        self.players[1].opponent = self.players[0]
