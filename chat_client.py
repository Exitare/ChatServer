import json
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

    def __init__(self, s, button_queue: queue.Queue, entry_queue, textbox_queue):
        Thread.__init__(self)
        self.socket = s
        self.event = Event()
        self.button_queue: queue.Queue = button_queue
        self.entry_queue: queue.Queue = entry_queue
        self.text_box_queue: queue.Queue = textbox_queue

    def run(self):
        global shutdown
        global connected
        self.button_queue.put(("connect", "text", "Disconnect"))
        self.button_queue.put(("send", "state", "normal"))
        # self.entry_queue.put(("message", "state", "normal"))
        connected = True

        payload = None
        command = None

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

                    if command == "rooms":
                        print("rooms")
                        print(payload)
                        payloads = payload.split("||")
                        array = json.loads(payloads[1])
                        print(array)

                        for row in array:
                            print(row)

                        print("First element")
                        print(array[0][0])
                        rooms = [room.strip() for room in payload]
                        self.text_box_queue.put(("rooms", "", rooms))

                    else:
                        print(command)
                        self.text_box_queue.put(("chat_message", "", command))

                except BaseException as ex:
                    print(ex)
                    sys.exit()

            except BaseException as ex:
                connected = False
                self.button_queue.put(("connect", "text", "Connect"))
                self.button_queue.put(("send", "state", "disabled"))
                # self.entry_queue.put(("message", "state", "disabled"))
                print(ex)
                sys.exit()

    def stop(self):
        self.event.set()


# Creating App class
# which will contain our overall App
class App:
    def __init__(self, root) -> None:
        self.socket = None
        self.button_queue = queue.Queue()
        self.entry_queue = queue.Queue()
        self.textbox_queue = queue.Queue()
        self.root = root
        self.receiving_thread = None
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.buttons = {}
        self.entries = {}
        self.textboxes = {}

        self.connectButton = Button(self.frm, text="Connect", command=self.connect_to_server,
                                    state=NORMAL)
        self.connectButton.grid(row=0, column=0)
        self.buttons["connect"] = self.connectButton

        self.exitButton = Button(self.frm, text="Quit", command=self.close_client)
        self.exitButton.grid(row=1, column=0)

        self.textbox = Text(self.frm, height=50, width=50, state="disabled")
        self.textbox.grid(row=0, column=1)
        self.textboxes["chat_message"] = self.textbox

        self.rooms = ttk.Combobox(self.frm, height=5, width=6, state="normal")
        self.rooms.grid(row=0, column=4)
        self.textboxes["rooms"] = self.rooms

        self.message_entry = Entry(self.frm)
        self.message_entry.grid(row=1, column=1)
        self.entries["message"] = self.message_entry

        self.sendButton = Button(self.frm, text="Send", command=self.send_message)
        self.sendButton.grid(row=1, column=2)
        self.sendButton["state"] = DISABLED
        self.buttons["send"] = self.sendButton

        # self.button2.pack(pady=20)

    def refresh_data(self):
        """
        """
        # do nothing if the aysyncio thread is dead
        # and no more data in the queue

        # refresh the GUI with new data from the queue
        while not self.button_queue.empty():
            button, attribute, data = self.button_queue.get()
            self.buttons[button][attribute] = data

        while not self.entry_queue.empty():
            entry, attribute, data = self.entry_queue.get()
            self.entries[entry][attribute] = data

        while not self.textbox_queue.empty():
            textbox, attribute, data = self.textbox_queue.get()
            if textbox == "rooms":
                for room in data:
                    self.textboxes[textbox].insert(1.0, room + "\n")

        #  timer to refresh the gui with data from the asyncio thread
        self.root.after(500, self.refresh_data)  # called only once!

    def send_message(self):
        self.socket.send(bytes(f"message:{self.message_entry.get()}", "utf-8"))

    def join_room(self):
        self.socket.send(bytes(f"jr:1234"))

    def connect_to_server(self):

        global connected

        if not connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))

            self.receiving_thread = DataReceived(s=self.socket, button_queue=self.button_queue,
                                                 entry_queue=self.entry_queue, textbox_queue=self.textbox_queue)
            #  timer to refresh the gui with data from the asyncio thread
            self.root.after(250, self.refresh_data)  # called only once!
            self.receiving_thread.start()

        else:
            print("Disconnecting")
            self.button_queue.put(("connect", "text", "Connect"))
            self.socket.send(bytes("disconnect", "utf-8"))
            self.socket.close()

    def close_client(self):
        global shutdown
        shutdown = True
        if self.socket is not None:
            self.socket.close()
        if self.receiving_thread is not None:
            self.receiving_thread.join()
        root.destroy()


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
