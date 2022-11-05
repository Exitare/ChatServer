import static
from room import Room


class CommandHandler:

    @staticmethod
    def handle_commands(client: any, data: str):
        try:

            command = None
            payload = None
            print(data)
            if ":" in data:
                splits = data.split(':')
                command = splits[0].strip()
                payload = splits[1].strip()
            else:
                command = data.strip()

            print(command)
            if command == "cr":
                if payload is None:
                    return

                payloads = payload.split('||')
                print(payloads)
                Room.create_room(room_id=payloads[0].strip(), client=client)

            if command == "jr":
                if payload is None:
                    return

                payloads = payload.split('||')
                print(payloads)
                Room.join_room(room_id=payloads[0].strip(), client=client)

            if command == "sm":
                if payload is None:
                    return

                payloads = payload.split('||')
                print(payloads)
                selected_room: Room = None
                for room in static.rooms:
                    if room.id == payloads[0]:
                        selected_room = room

                if selected_room is None:
                    print("Could not find room!")

                for connected_client in selected_room.clients:
                    if connected_client == client:
                        continue

                    print(f"Sending message to client with port: {connected_client.port}")
                    connected_client.conn.send(bytes(payloads[1], "utf-8"))


        except BaseException as ex:
            print(ex)
