import os
from time import sleep
import math
import vizdoom as vzd
import cv2

def setupGame():
    # load the initial configuration for the game and returns the game object using the vizdoom API
    # this code is modified from vizdoom example code found in the vizdoom repo, some lines copied & removed and tweaked
    game = vzd.DoomGame()
    # game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "deathmatch.wad"))
    game.load_config(os.path.join(vzd.scenarios_path, "cig.cfg"))

    # Sets map to start (scenario .wad files can contain many maps).
    game.set_doom_map("map01")
    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
    game.set_screen_format(vzd.ScreenFormat.RGB24)

    # Sets the living reward (for each move) to -1
    game.set_available_buttons(
        [vzd.Button.MOVE_FORWARD, vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.ATTACK, vzd.Button.TURN_LEFT_RIGHT_DELTA]
    )

    game.set_render_hud(True)

    game.set_depth_buffer_enabled(True)

    # Buttons that will be used can be also checked by:
    game.set_available_game_variables([vzd.GameVariable.AMMO2])
    game.set_available_game_variables([vzd.GameVariable.KILLCOUNT])

    # Causes episodes to finish after 200 tics (actions)
    game.set_episode_timeout(2000)

    # Makes episodes start after 10 tics (~after raising the weapon)
    game.set_episode_start_time(10)

    # Makes the window appear (turned on by default)
    game.set_window_visible(True)

    # this is the reward for staying alive, we set it to -1 per frame the player is alive so higher scores for faster elims
    game.set_living_reward(1)
    game.set_mode(vzd.Mode.PLAYER)
    return game

rooms = []
map = []

def decideNextMove(screen_buffer, navigating):
    # determine if we should move or shoot
    gray_image = cv2.cvtColor(screen_buffer, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('./gray_image.png', gray_image)
    depth = state.depth_buffer
    if navigating:
        if(map and checkIfInNewRoom(depth)):
            print('A WHOLE NEW ROOOOOOM')
            map.clear()
            return {'action' : 'map', 'depth' : depth}
        else:
            return {'action' : 'navigate', 'angle' : 0}
    if depth is not None:
        cv2.imwrite('./gray_image.png', gray_image)
        cv2.imwrite('./depth' + str(len(map)) +'.png', depth)
    # filter the image by minimum brightness threshold to remove noise
    for (line_idx, line) in enumerate(gray_image):
        for (pixel_idx, pixel) in enumerate(line):
            if (pixel < 100):
                gray_image[line_idx, pixel_idx] = 0
    # search for a destination to goto and then navigate to it
    if len(map) < 4:
        return {'action' : 'map', 'depth' : depth}
    min_intensity = 256
    min_idx = 0
    all_navigation_targets = []
    for (idx, depthMap) in enumerate(map):
        destinations = getPossibleDestinations(depthMap)
        if(destinations[0]['max'] < min_intensity):
            min_intensity = destinations[0]['max']
            min_idx = idx
        all_navigation_targets.append(destinations)
    if (not navigating):
        offset = min_idx * 90
        angle = getAngleForTraversal(all_navigation_targets[min_idx], gray_image.shape)
        real_angle = offset + angle
        print('got the real angle for navigation')
        print(real_angle)
        return {'action' : 'navigate', 'angle' : real_angle}


    # angle = getAngleForTraversal(possible_destinations, gray_image.shape)
    # return {'action' : 'navigate', 'angle' : angle}
    return findMonsterDownRange(gray_image)

def checkIfInNewRoom(depthMap):
    # return true if in new room, otherwise return false
    max_depth_brightness = 0
    depth_indexes = []
    thresdhold = 10
    # return true if we are in another room, otherwise false
    for (line_idx, line) in enumerate(depthMap):
        for (pixel_idx, pixel) in enumerate(line):
            if (pixel > max_depth_brightness + thresdhold):
                max_depth_brightness = pixel
                depth_indexes.clear()
            if (pixel == max_depth_brightness):
                depth_indexes.append((pixel_idx, line_idx))
    destination_x_coords = getBoundingRectsForCoordinateList(depth_indexes)
    if destination_x_coords[0]['low'] < 10 and destination_x_coords[0]['high'] + destination_x_coords[0]['low'] > 360:
        return True
    else:
        return False

def getPossibleDestinations(depthMap):
    max_depth_brightness = 0
    depth_indexes = []
    for (line_idx, line) in enumerate(depthMap):
        for (pixel_idx, pixel) in enumerate(line):
            if (pixel > max_depth_brightness):
                max_depth_brightness = pixel
                depth_indexes.clear()
            if (pixel == max_depth_brightness):
                depth_indexes.append((pixel_idx, line_idx))
    destination_x_coords = getBoundingRectsForCoordinateList(depth_indexes)
    # check the arr idx here, is it necessary?
    destination_x_coords[0]['max'] = max_depth_brightness
    return destination_x_coords


def getBoundingRectsForCoordinateList(coordinate_list):
    rects = []
    rect_cords = []
    for (idx, coord_pair) in enumerate(coordinate_list):
        if idx == 0:
            rect_cords.append(coord_pair)
            continue
        if (len(rect_cords) > 0 and coord_pair[1] - rect_cords[idx - 1][1] < 3):
            rect_cords.append(coord_pair)
        else:
            rects.append(getXBoundaries(rect_cords))
            rect_cords.clear()
    if len(rect_cords) > 0:
        rects.append(getXBoundaries(rect_cords))
        rect_cords.clear()
    return rects

def getXBoundaries(coordinate_list):
    low_x = -1
    high_x = -1
    for coordinate in coordinate_list:
        if low_x == -1 or coordinate[0] < low_x:
            low_x = coordinate[0]
        if coordinate[0] > 0 and coordinate[0] > high_x:
            high_x = coordinate[0]
    return {"low": low_x, "high" : high_x}

def getAngleForTraversal(x_destination, resolution):
    chosen_destination = x_destination[0]
    destination_midpoint = math.floor(chosen_destination['low'] + chosen_destination['high'] / 2)
    screen_midpoint = math.floor(resolution[1] / 2)
    x_delta = (destination_midpoint - screen_midpoint)
    y_delta = (resolution[0] - math.floor(resolution[0] / 2))
    approach_angle = math.atan2(x_delta , y_delta)
    approach_angle_degrees = math.degrees(approach_angle)
    return approach_angle_degrees

def getDepthMap():
    # rotate 90 degrees per turn
    pass


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
                brightest_idx[0] = i
                brightest_idx[1] = idx
    if brightest_idx[1] < 150:
        return "LEFT"
    if brightest_idx[1] > 170:
        return "RIGHT"
    else:
        return "RIGHT"
    
# main loop and setup based off vizdoom examples. Some lines below copied/removed and tweaked from vizdoom examples

if __name__ == "__main__":
    game = setupGame()
    game.add_game_args(
        "+vid_forcesurface 1"
        "-host 1 -deathmatch +timelimit 10.0 "
        "+sv_forcerespawn 1 +sv_noautoaim 1 +sv_respawnprotect 1 +sv_spawnfarthest 1 +sv_nocrouch 1 "
        "+viz_respawn_delay 10"
        )
    game.add_game_args("+viz_bots_path ../../scenarios/perfect_bots.cfg")
    game.add_game_args("+name AI +colorset 0")

    game.init()
    bots = 7
    navigating = False

    # these are the different game input actions, for our limited example we're using move left, move right, shoot
    # actions can be extended to incorporate move forward, rotation, and interaction
    angle_index = 4 # the index of the turn angle
    actions = [
                [True, False, False, False, 0],
                [False, True, False, False, 0],
                [False, False, True, False, 0],
                [False, False, False, True, 0],
                [False, False, False, False, 90],
              ]

    episodes = 5

    sleep_time = 1.0 / vzd.DEFAULT_TICRATE

    for i in range(episodes):
        print(f"Episode #{i + 1}")
        game.new_episode()

        while not game.is_episode_finished():

            state = game.get_state()
            screen_buf = state.screen_buffer
            next_move = decideNextMove(screen_buf, navigating)
            # game.make_action(actions[0])

            if (next_move['action'] == 'map'):
                actions[4][angle_index] = 90
                game.make_action(actions[4])
                map.append(next_move['depth'])



            if (next_move['action'] == 'navigate'):
                navigating = True
                actions[4][angle_index] = next_move['angle']
                game.make_action(actions[4])
                # game.make_action(actions[4])
                game.make_action(actions[0])
                game.make_action(actions[0])
                


            if (next_move == "LEFT"):
                actions[4][angle_index] = 15
                game.make_action(actions[4])
            if (next_move == "RIGHT"):
                actions[4][angle_index] = -15
                game.make_action(actions[4])
            if (next_move == "SHOOT"):
                game.make_action(actions[2])
            if sleep_time > 0:
                sleep(sleep_time)

        # Check how the episode went.
        print("Episode finished.")
        print("Kills:", game.get_game_variable(vzd.GameVariable.KILLCOUNT))
        print("Total reward:", game.get_total_reward())
        print("************************")

    game.close()