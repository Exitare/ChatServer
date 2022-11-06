from tkinter import *
from tkinter import ttk
import socket, sys
from threading import Thread, Event
import queue

HOST = "127.0.0.1"
PORT = 1234
BUFFER_SIZE = 1024  # Normally 1024
shutdown = False
connected = False


class DataReceived(Thread):

    def __init__(self, s, the_queue: queue):
        Thread.__init__(self)
        self.socket = s
        self.event = Event()
        self.the_queue: queue = the_queue

    def run(self):
        global shutdown
        global connected
        self.the_queue.put(("connect", "text", "Disconnect"))
        self.the_queue.put(("send", "state", "normal"))
        connected = True
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
                connected = False
                self.the_queue.put(("connect", "text", "Connect"))
                self.the_queue.put(("send", "state", "disabled"))
                print(ex)
                sys.exit()

    def stop(self):
        self.event.set()


# Creating App class
# which will contain our overall App
class App:
    def __init__(self, root) -> None:
        self.socket = None
        self.the_queue = queue.Queue()
        self.root = root
        self.receiving_thread = None
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.buttons = {}

        self.entry = Entry(self.frm)
        self.entry.grid(column=0, row=1)

        self.connectButton = Button(self.frm, text="Connect", command=self.connect_to_server,
                                    state=NORMAL)
        self.connectButton.grid(column=0, row=2)
        self.buttons["connect"] = self.connectButton

        self.sendButton = Button(self.frm, text="Send",
                                 command=self.send_message)
        self.sendButton.grid(column=1, row=1)
        self.sendButton["state"] = DISABLED
        self.buttons["send"] = self.sendButton

        self.exitButton = Button(self.frm, text="Quit",
                                 command=self.close_client)
        self.exitButton.grid(column=1, row=2)

        # self.button2.pack(pady=20)

    def refresh_data(self):
        """
        """
        # do nothing if the aysyncio thread is dead
        # and no more data in the queue
        if not self.receiving_thread.is_alive() and self.the_queue.empty():
            return

        # refresh the GUI with new data from the queue
        while not self.the_queue.empty():
            button, attribute, data = self.the_queue.get()
            self.buttons[button][attribute] = data

        #  timer to refresh the gui with data from the asyncio thread
        self.root.after(500, self.refresh_data)  # called only once!

    def send_message(self):
        self.socket.send(bytes(f"message:{self.entry.get()}", "utf-8"))

    def connect_to_server(self):

        global connected

        if not connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))

            self.receiving_thread = DataReceived(s=self.socket, the_queue=self.the_queue)
            #  timer to refresh the gui with data from the asyncio thread
            self.root.after(250, self.refresh_data)  # called only once!
            self.receiving_thread.start()

        else:
            self.socket.close()

    def close_client(self):
        global shutdown
        shutdown = True
        if self.socket is not None:
            self.socket.close()
        if self.receiving_thread is not None:
            self.receiving_thread.join()
        root.destroy()


# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Exitare Chat Server!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=closeClient).grid(column=1, row=0)
# ttk.Button(frm, text="Connect", command=connectToServer).grid(column=1, row=1)

# root.mainloop()


if __name__ == "__main__":
    # Instantiating top level
    root = Tk()

    # Setting the title of the window
    root.title("Exitare Chat Server")

    # Setting the geometry i.e Dimensions
    root.geometry("1280x720")

    # Calling our App
    app = App(root)

    # Mainloop which will cause this toplevel
    # to run infinitely
    root.mainloop()
