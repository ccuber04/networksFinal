from websockets.asyncio.server import serve
import asyncio
import json
import random

players = {}
socket_to_id = {}
snacks = []

width = 500
rows = 20

next_id = 0

async def game_loop():
    global food
    while True:
        # apply player input
        # update all snakes
        for player_id, player in players.items():
            snake = player["snake"]
            direction = player["direction"]

            head_x, head_y = snake[0]
            dx, dy = direction

            new_head = [head_x + dx, head_y + dy]

            # handle collisions
            hit_wall = new_head[0] >= rows or new_head[0] < 0 or new_head[1] >= rows or new_head[1] < 0
            hit_self = new_head in snake
            hit_snake = new_head in [snakes["snake"] for _, snakes in players.items()]

            if hit_wall or hit_self or hit_snake:
                reset_player(player)
                continue

            if new_head in snake:
                reset_player(player)
                continue

            # head did not collide so insert head as a new location
            snake.insert(0, new_head)

            # handle food
            if new_head in snacks:
                snack_index = snacks.index(new_head)
                snacks[snack_index] = random_snack_position()
            else:
                snake.pop()

        # build game state
        state = {
            "type": "state",
            "players": players,
            "snacks": snacks
        }

        # send state to all clients
        for ws in socket_to_id.keys():
            await ws.send(json.dumps(state))

        await asyncio.sleep(0.1)

async def handler(ws):
    global next_id
    print("Connected", ws)
    player_data = {
        "snake": [[10, 10]],
        "direction": [0, 1]
    }

    players[next_id] = player_data
    socket_to_id[ws] = next_id
    next_id += 1

    # sync number of snacks to the number of players
    sync_total_snacks()

    sending_data = {
        "type": "init",
        "player_id": socket_to_id[ws],
        "players": players
    }

    await ws.send(json.dumps(sending_data))

    try:
        async for message in ws:
            data = json.loads(message)
            if data["type"] == "input":
                player_id = socket_to_id[ws]
                player = players[player_id]

                current_dx, current_dy = player["direction"]
                new_dx, new_dy = data["direction"]

                if current_dx + new_dx != 0 and current_dy + new_dy != 0:
                    player["direction"] = data["direction"]
                    print(f"Player {player_id} redirected: {players[player_id]}")

    finally:
        player_id = socket_to_id[ws]
        del players[player_id]
        del socket_to_id[ws]

        # player leaves == update total snacks
        sync_total_snacks()

        print("Client disconnected")

async def main():
    async with serve(handler, '192.168.0.21', 8080) as server:
        print("Server started on localhost:8080")
        await game_loop()
        # await server.serve_forever()

#### Helpers ####
def random_snack_position():
    while True:
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, rows - 1)
        new_snack = [x, y]

        food_on_snake = False
        for player in players.values():
            if new_snack in player["snake"]:
                food_on_snake = True
                break

        if not food_on_snake and new_snack not in snacks:
            return new_snack

def sync_total_snacks():
    while len(snacks) < len(players):
        snacks.append(random_snack_position())

    while len(snacks) > len(players):
        snacks.pop()

def reset_player(player):
    player["snake"] = [[10, 10]]
    player["direction"] = [0, 1]

if __name__ == "__main__":
    asyncio.run(main())
