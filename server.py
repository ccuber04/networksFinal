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
    """Main game loop to process players input, updating the snake, updating snacks, and sending game state to
    all clients"""
    global food
    while True:
        # apply player input and update all snakes
        for player_id, player in players.items():
            snake = player["snake"]
            direction = player["direction"]

            head_x, head_y = snake[0]
            dx, dy = direction

            new_head = [head_x + dx, head_y + dy]

            # handle collisions
            hit_wall = new_head[0] >= rows or new_head[0] < 0 or new_head[1] >= rows or new_head[1] < 0
            hit_self = new_head in snake
            hit_snake = any(
                new_head in other_player["snake"]
                for id, other_player in players.items()
                if id != player_id
            )

            # current player collides with the wall, itself, or other players then reset
            if hit_wall or hit_self or hit_snake:
                reset_player(player)
                continue

            # head did not collide so insert head as a new location
            snake.insert(0, new_head)

            # handle food
            if new_head in snacks:
                # extend the snake and don't pop the tail
                snack_index = snacks.index(new_head)
                snacks[snack_index] = random_snack_position()
            else:
                # keep the snake at the same size
                snake.pop()

        # build game state
        state = {
            "type": "state",
            "players": players,
            "snacks": snacks
        }

        # send state to all clients
        for ws in list(socket_to_id.keys()):
            try:
                await ws.send(json.dumps(state))
            except Exception as e:
                print(f"Removing disconnected client: {e}")

                # send likely fail because player no longer exists
                # remove the player from players and socket_to_id
                player_id = socket_to_id[ws]
                if player_id is not None:
                    players.pop(player_id)
                socket_to_id.pop(ws, None)

        # player could be removed so update number of snacks
        sync_total_snacks()

        # sleep to allow handler to recv data
        await asyncio.sleep(0.1)

async def handler(ws):
    """Handles websocket connections and use JSON for data transfer"""
    global next_id
    print("Connected", ws)

    # initialize player with random spawn, direction, and color
    player_data = {
        "snake": [random_spawn_location()],
        "direction": random_direction(),
        "color": random_color()
    }

    players[next_id] = player_data
    socket_to_id[ws] = next_id
    next_id += 1

    # sync number of snacks to the number of players
    sync_total_snacks()

    # sending initial game state and what id the client has
    sending_data = {
        "type": "init",
        "player_id": socket_to_id[ws],
        "players": players
    }

    await ws.send(json.dumps(sending_data))

    try:
        async for message in ws:
            data = json.loads(message)

            # player changing direction at a keypress
            if data["type"] == "input":
                player_id = socket_to_id[ws]
                player = players[player_id]

                current_dx, current_dy = player["direction"]
                new_dx, new_dy = data["direction"]

                # do not allow reverse directions (left -> right or up -> down)
                if current_dx + new_dx != 0 and current_dy + new_dy != 0:
                    player["direction"] = data["direction"]

    finally:
        # connection is closed
        player_id = socket_to_id[ws]
        del players[player_id]
        del socket_to_id[ws]

        # player leaves == update total snacks
        sync_total_snacks()

        print("Client disconnected")

async def server():
    """Server connection and game loop starter"""
    async with serve(handler, '0.0.0.0', 8080):
        print("Server started on 0.0.0.0:8080")
        game_task = asyncio.create_task(game_loop())
        await asyncio.Future()

#### Helpers ####
def random_snack_position():
    """Randomly generates a snack position"""
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

def random_spawn_location():
    """Randomly generates a spawn location"""
    while True:
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, rows - 1)
        spawn = [x, y]

        on_snake = any(
            spawn in player["snake"]
            for player in players.values()
        )
        on_snack = spawn in snacks

        if not on_snake and not on_snack:
            return spawn

def random_color():
    """Randomly generates the players color"""
    return [
        random.randrange(50, 255),
        random.randrange(50, 255),
        random.randrange(50, 255)
    ]

def random_direction():
    """Randomly selects initial and reset direction of player"""
    return random.choice([
        [1, 0], [-1, 0], [0, 1], [0, -1]
    ])

def sync_total_snacks():
    """Synchronize and update snack positions based on number of players"""
    # add more snacks if there are more players than snacks
    while len(snacks) < len(players):
        snacks.append(random_snack_position())

    # remove snacks if there are more snacks than players
    while len(snacks) > len(players):
        snacks.pop()

def reset_player(player):
    """Reset player after death to new spawn location and random direction"""
    player["snake"] = []
    player["snake"] = [random_spawn_location()]
    player["direction"] = random_direction()

if __name__ == "__main__":
    asyncio.run(server())
