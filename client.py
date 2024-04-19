from array import *
from util import *
import gamecontroller as snake
import graphicscontroller as gfx
import configparser
import asyncio
import networking


async def main():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini')

    allowMultiplayer = config["GAMEPLAY"]["ALLOW_MULTIPLAYER"] == "yes"

    player = get_player_from_input()

    gameController = snake.ObserverGameController(
    ) if allowMultiplayer else snake.GameController()
    spawnPoint = gameController.get_open_spawn_point()

    listenPort = 0
    if (allowMultiplayer):
        message = {"action": "handshake"}
        sender = networking.TCPSender()
        observer = networking.Observer()
        message = observer.prepare_data(message)
        response = await sender.send_data(message)
        listenPort = int(response["port"])
        load_config_from_data(response)
        gameController.load_config_from_data(response)

        message = observer.prepare_data({
            "action": "spawn",
            "player": player.encode(),
        })
        response = await sender.send_data(message)
        print(f"Respuesta del jugador de generación: {response}")
        spawnPoint = response["point"]

        observer.set_sender(sender)
        gameController.add_observer(observer)

    await gameController.spawn_player(player, point=spawnPoint)
    graphics = gfx.GraphicsController()
    graphics.add_player(player)
    graphics.draw_graphics(gameController.get_map())

    print("Iniciando bucle de juego")
    await wait_for_update(graphics, gameController, player, listenPort, allowMultiplayer)
    print(f"¡Se activó un ciclo de actualización!")
    graphics.update_graphics(gameController.get_map())
    print("¡Juego terminado!")
    graphics.get_click_point()


async def check_msg(port):
    print(f"Escuchando en el puerto: {port}")
    server = await asyncio.start_server(handle_data_from_server, "10.10.0.56", port)
    print("Conjunto de escuchadores")
    async with server:
        serverRoutine = await server.serve_forever()
        # serverRoutine.cancel()


async def handle_data_from_server(reader, writer):
    print("Manejo de datos!")
    data = (await reader.read(255)).decode()
    writer.write(str(data).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def check_click(gameController, player, graphics):
    print("Listening for clicks")
    while (not gameController.is_game_over()):
        clickPoint = graphics.get_click_point()
        if (gameController.player_can_move_to(clickPoint, player)):
            await gameController.move_player(clickPoint, player)
            graphics.update_graphics(gameController.get_map())


async def wait_for_update(graphics, gameController, player, port, allowMultiplayer):
    await asyncio.gather(
        check_click(gameController, player, graphics),
        check_msg(port)
    )


def load_config_from_data(data):
    config["GAMEPLAY"]["CELL_LIFETIME"]
    config["GAMEPLAY"]["MAP_SIZE"]


def get_player_from_input():
    playerName = input("Ingresa tu nombre de jugador:")
    return snake.Player(playerName)


asyncio.run(main(), debug=True)
