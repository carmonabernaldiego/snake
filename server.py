import asyncio
import ast
import networking
import gamecontroller as snake


def main():
    global gameController
    gameController = snake.ObserverGameController()

    global clients
    clients = []

    global nextClientPort
    nextClientPort = 9000

    asyncio.run(run_server(), debug=True)


async def run_server():
    HOST, PORT = "localhost", 9000
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()


async def handle_client(reader, writer):
    data = (await reader.read(255)).decode()
    print(f"Intentando decodificar datos: {data}")
    data = ast.literal_eval(data)
    action = data["action"]
    print(action)
    source = data["source"]
    print(f"Source: {source}")
    response = {"status": "good"}
    match(action):
        case "handshake":
            address = "localhost"
            print(f"Dirección para el cliente: {address}")
            add_client(source, address)
            response = get_handshake_config()
        case "spawn":
            player = snake.Player.decode(data["player"])
            point = await gameController.spawn_player(player, source)
            print(f"Got point: {point}")
            response = {"point": point}
        case "move":
            player = snake.Player.decode(data["player"])
            point = (0, 1)
            await gameController.move_player(point, player, source)
        case "test":
            response = {"data": data}
    print(f"Devolviendo respuesta: {response}")
    writer.write(str(response).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    print("Servidor terminado")


def add_client(source, address):
    gameController.add_observer(networking.Observer(
        source, port=get_next_client_port(), host=address))
    clients.append(source)
    print(f"Cliente agregado: {source}")


def get_next_client_port():
    global nextClientPort
    nextClientPort += 1
    return nextClientPort


def get_handshake_config():
    config = gameController.get_config()
    config["port"] = nextClientPort
    return config


if (__name__ == "__main__"):
    main()
