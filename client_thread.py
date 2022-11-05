from threading import Thread, Event
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
