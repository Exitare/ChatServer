import json
from threading import Thread, Event

import static
from room import Room
from command_handler import CommandHandler


class ClientThread(Thread):

    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.event = Event()
        self.active = True
        print("[+] New thread started for " + ip + ":" + str(port))
        total: str = ""

        for room in static.rooms:
            total += room.id + '||'

        room_ids = [room.id for room in static.rooms]

        game_board = []
        for i in range(3):
            row_list = []
            for j in range(3):
                # you need to increment through dataList here, like this:
                row_list.append('_')
            game_board.append(row_list)

        print(game_board)

        total = json.dumps(room_ids)
        self.conn.send(bytes(f"rooms: {total} || {json.dumps(game_board)}", "utf-8"))

    def run(self):
        while self.event.is_set() is not None:
            try:
                payload = None
                command = None
                data = self.conn.recv(2048)
                if not data:
                    break

                data = data.decode('utf-8')

                CommandHandler.handle_commands(self, data)



            except:
                break

    def stop(self):
        self.event.set()
        self.conn.send(b"shutdown")
        self.conn.close()
