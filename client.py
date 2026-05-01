import asyncio
import json
import pygame
import render
from websockets.asyncio.client import connect

from render import redrawWindow

server_players = {} # dictionary of all players snakes
server_snacks = [] # list of all snack locations sent from server

my_player_id = None

width = 500
rows = 20

async def client_loop():
    """Sets up connections and starts game_loop and receive_loop"""
    async with connect("ws://192.168.0.21:8080") as ws:
        print("Connected to server")

        receive_task = asyncio.create_task(receive_loop(ws))
        game_task = asyncio.create_task(game_loop(ws))

        await game_task
        receive_task.cancel()


async def receive_loop(ws):
    """Websocket recv message loop to initialize data and update states"""
    global server_players, server_snacks, my_player_id
    while True:
        msg = await ws.recv()
        data = json.loads(msg)

        # initialize all players and identify which player the client is
        if data["type"] == "init":
            my_player_id = data["player_id"]
            server_players = data["players"]
            print(f"player id: {my_player_id}")

        # recv and updated game state of players and snacks
        elif data["type"] == "state":
            server_players = data["players"]
            server_snacks = [tuple(pos) for pos in data["snacks"]]


async def game_loop(ws):
    """Client's game loop for reading keypresses to send to server and render the game"""
    pygame.init()
    win = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Multiplayer Snake!")

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    await send_input(ws, [-1, 0])
                elif event.key == pygame.K_RIGHT:
                    await send_input(ws, [1, 0])
                elif event.key == pygame.K_UP:
                    await send_input(ws, [0, -1])
                elif event.key == pygame.K_DOWN:
                    await send_input(ws, [0, 1])

        redrawWindow(width, rows, win, server_players, server_snacks)
        await asyncio.sleep(0)

    pygame.quit()

#### Helpers ####
async def send_input(ws, direction):
    """Send redirection as JSON to server"""
    msg = {
        "type": "input",
        "direction": direction
    }
    await ws.send(json.dumps(msg))

if __name__ == '__main__':
    asyncio.run(client_loop())