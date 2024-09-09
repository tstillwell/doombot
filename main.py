import os
from time import sleep
import vizdoom as vzd
import cv2

def setupGame():
    # load the initial configuration for the game and returns the game object using the vizdoom API
    # this code is modified from vizdoom example code found in the vizdoom repo, some lines copied & removed and tweaked
    game = vzd.DoomGame()
    game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "basic.wad"))

    # Sets map to start (scenario .wad files can contain many maps).
    game.set_doom_map("map01")

    game.set_screen_format(vzd.ScreenFormat.RGB24)

    # Sets the living reward (for each move) to -1
    game.set_available_buttons(
        [vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.ATTACK]
    )
    # Buttons that will be used can be also checked by:
    game.set_available_game_variables([vzd.GameVariable.AMMO2])

    # Causes episodes to finish after 200 tics (actions)
    game.set_episode_timeout(200)

    # Makes episodes start after 10 tics (~after raising the weapon)
    game.set_episode_start_time(10)

    # Makes the window appear (turned on by default)
    game.set_window_visible(True)

    # this is the reward for staying alive, we set it to -1 per frame the player is alive so higher scores for faster elims
    game.set_living_reward(-1)
    game.set_mode(vzd.Mode.PLAYER)
    return game

def decideNextMove(screen_buffer):
    # determine if we should move or shoot
    gray_image = cv2.cvtColor(screen_buffer, cv2.COLOR_BGR2GRAY)
    # filter the image by minimum brightness threshold to remove noise
    for (line_idx, line) in enumerate(gray_image):
        for (pixel_idx, pixel) in enumerate(line):
            if (pixel < 100):
                gray_image[line_idx, pixel_idx] = 0
    return findMonsterDownRange(gray_image)

def findMonsterDownRange(gray_image):
    # locate the monster, and move so that it is ready to shoot
    # ignores the last 90 rows of the frame, because the monster is always above that point (in this example)
    # this is an initial POC, this function will need to be more advanced to handle 3d navigation / healthpacks / ammo
    brightest_idx = [0, 0]
    brightest_val = 0
    for i in range(len(gray_image) - 90):
        for (idx, pixel) in enumerate(gray_image[i]):
            if pixel > brightest_val:
                brightest_val = pixel
                brightest_idx[0]= i
                brightest_idx[1] = idx
    if brightest_idx[1] < 150:
        return "LEFT"
    if brightest_idx[1] > 170:
        return "RIGHT"
    else:
        return "SHOOT"
    
# main loop and setup based off vizdoom examples. Some lines below copied/removed and tweaked from vizdoom examples

if __name__ == "__main__":
    game = setupGame()
    game.add_game_args("+vid_forcesurface 1")
    game.init()

    # these are the different game input actions, for our limited example we're using move left, move right, shoot
    # actions can be extended to incorporate move forward, rotation, and interaction
    actions = [[True, False, False], [False, True, False], [False, False, True]]

    episodes = 5

    sleep_time = 1.0 / vzd.DEFAULT_TICRATE

    for i in range(episodes):
        print(f"Episode #{i + 1}")
        game.new_episode()

        while not game.is_episode_finished():

            state = game.get_state()
            screen_buf = state.screen_buffer
            next_move = decideNextMove(screen_buf)

            if (next_move == "LEFT"):
                game.make_action(actions[0])
            if (next_move == "RIGHT"):
                game.make_action(actions[1])
            if (next_move == "SHOOT"):
                game.make_action(actions[2])
            if sleep_time > 0:
                sleep(sleep_time)

        # Check how the episode went.
        print("Episode finished.")
        print("Total reward:", game.get_total_reward())
        print("************************")

    game.close()