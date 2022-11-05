import socket, sys
from threading import Thread, Event

import static
from client_thread import ClientThread

HOST = "127.0.0.1"
PORT = 1234
BUFFER_SIZE = 1024  # Normally 1024
threads = []
shutdown: bool = False


class ClientAcceptingThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = None
        self.event = Event()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.socket = s
            self.socket.bind((HOST, PORT))
            self.socket.listen()

            try:
                while not self.event.is_set():
                    conn, (ip, port) = self.socket.accept()
                    new_thread = ClientThread(ip, port, conn)
                    new_thread.start()
                    threads.append(new_thread)

            except BaseException as ex:
                s.close()

            finally:
                print("Stopped accepting clients!")

    def stop(self):
        self.event.set()
        self.socket.close()


if __name__ == '__main__':

    accepting_thread = ClientAcceptingThread()
    accepting_thread.start()

    print("Server up and running....")
    while not shutdown:
        command = input("Enter your command: ").strip()

        if command == "shutdown":
            print("Shutting down server.")
            shutdown = True

            for t in threads:
                t.stop()

            accepting_thread.stop()
            accepting_thread.join()


        elif command == "test":
            thread: ClientThread
            for thread in threads:
                try:
                    thread.conn.send(b"test")
                except:
                    thread.active = False

            threads = [thread for thread in threads if thread.active]

        elif command == "rooms":
            print(f"{static.rooms} rooms created.")
            for room in static.rooms:
                print(room.clients)



    else:
        print("Server is down...")
        sys.exit()
