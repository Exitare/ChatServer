import static


class Room:

    def __init__(self, room_id: str, client: any = None):
        self._clients = [client]
        self._id = room_id

    @property
    def id(self):
        return self._id

    @property
    def clients(self):
        return self._clients

    def join(self, client: any):
        self._clients.append(client)

    @staticmethod
    def create_room(room_id: str, client: any):
        static.rooms.append(Room(room_id=room_id, client=client))

    @staticmethod
    def join_room(room_id: str, client: any):
        room: Room
        for room in static.rooms:
            if room.id == room_id:
                room.clients.append(client)
                return

        Room.create_room(room_id=room_id, client=client)
