import uuid
import ast
import asyncio


class Observer:
    def __init__(self, id=None, sender=None, port=9000, host="localhost") -> None:
        if (id is None):
            id = uuid.uuid1()
        self._id = id
        if (sender is None):
            sender = TCPSender(port, host)
        self._sender = sender

    def set_sender(self, sender):
        self._sender = sender

    async def update(self, state, source):
        if (source == self._id):
            return
        return await self._sender.send_data(self.prepare_data(state))

    def prepare_data(self, data):
        data["source"] = str(self._id)
        return data


class TCPSender:
    def __init__(self, port=9000, host="localhost") -> None:
        self.host = host
        self.port = port

    def set_port(self, port):
        self.port = port

    async def send_data(self, data: dict):
        reader, writer = await asyncio.open_connection(
            self.host, self.port)

        print("Enviando datos!")
        writer.write(str(data).encode())
        await writer.drain()

        received = await reader.read(255)
        received = received.decode()
        print(f'Recibido: {received}')

        print('Cierre de conexión')
        writer.close()
        await writer.wait_closed()
        if (received is not None and received != ''):
            return ast.literal_eval(received)
