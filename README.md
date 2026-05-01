# Networks Final - Snake Game
## Purpose
- Create a networked Multiplayer Snake game from techwithtim's [snake game](https://github.com/techwithtim/Snake-Game.git)
## Project 
- Websockets used to make connection between client and server
- Server to host the game
- Multiple clients to battle
- Edit the game to have multiple fruit generated and running into other snakes kills your snake
## How to Use
### Packages Required to Install:
- `websockets`
- `pygame`

### Running the Game
After installing the packages above, first, run the server in a python terminal. Next, you will want to change the
clients connection IP address to what the IP of the server is. This is done in this line under the `client.py` file:
```python
async with connect("ws://localhost:8080") as ws:
```
You will change `localhost` to your servers IP address. Or, if you wish to run locally you can keep `localhost` and run
the client. 

You can have multiple players connecting to the same server. Just run `client.py` on your different devices and play
this game with a friend. Each player will have their own random color so that you can easily identify yourself in the map.
There will be an additional snack for every player that is in the game. But be careful to not run into your fellow snakes
or you will be reset to just the head. 
## Code Examples
This networked game took the original techwithtim example as a guide for the game itself. Some adjustments were made to
rendering the game in `render.py` and for receiving keypresses from `client.py`. Rendering the window was adjusted to
include multiple players and snacks in the game. Those changes are seen here:
```python
for player in server_players.values():
    snake = [tuple(pos) for pos in player["snake"]]
    color = tuple(player.get("color", [255, 0, 0]))

    for i, pos in enumerate(snake):
        c = cube(pos, color=color)
        if i == 0:
            c.draw(win, True)
        else:
            c.draw(win)
```
We iterate through the list of players and apply their color to each cube in the snake instead of using the default value
and draw all the snakes in the list instead of the single snake in the game.
```python
for snack in server_snacks:
    snack_cube = cube(snack, color=(0, 255, 0))
    snack_cube.draw(win)
```
Here we are drawing all the snack cubes that are in the game instead of doing the one line draw that techwithtim had.

As far as keypresses, we detect when there is an event type of `KEYDOWN` before sending the input data. This means if you
hold down the key, there will not be multiple websocket messages being sent to the server, only one for the single keypress.
```python
elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_LEFT:
        await send_input(ws, [-1, 0])
    elif event.key == pygame.K_RIGHT:
        await send_input(ws, [1, 0])
    elif event.key == pygame.K_UP:
        await send_input(ws, [0, -1])
    elif event.key == pygame.K_DOWN:
        await send_input(ws, [0, 1])
```
The game state is sent by JSON and each state includes the following data as an example:
```json
{
  "type": "state",
  "players": {
  "0": {
    "snake": [[10, 10], [10, 9], [10, 8]],
    "direction": [0, 1],
    "color": [222, 120, 83]
  }
  },
  "snacks": [[10, 11]]
}
```