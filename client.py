from threading import Thread, Event
import socket, sys

HOST = "127.0.0.1"
PORT = 1234
BUFFER_SIZE = 1024  # Normally 1024
shutdown = False


class DataReceived(Thread):

    def __init__(self, s):
        Thread.__init__(self)
        self.socket = s
        self.event = Event()

    def run(self):
        global shutdown
        while True:
            try:
                data = self.socket.recv(BUFFER_SIZE)

                if not data:
                    continue

                try:
                    data = data.decode('utf-8')

                    if ":" in data:
                        splits = data.split(':')
                        command = splits[0].strip()
                        payload = splits[1].strip()
                    else:
                        command = data.strip()

                    if command == "shutdown":
                        print("Shutdown initiated...")
                        self.socket.close()
                        shutdown = True
                        sys.exit()

                    else:
                        print(command)

                except BaseException as ex:
                    print(ex)
                    sys.exit()

            except BaseException as ex:
                print(ex)
                sys.exit()

    def stop(self):
        self.event.set()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    receiving_thread = DataReceived(s=s)
    receiving_thread.start()

    while not shutdown:
        try:
            command = input("Enter command: ")
            if command:
                s.send(bytes(command, "utf-8"))

        except KeyboardInterrupt:
            # quit
            sys.exit()
        except:
            continue
