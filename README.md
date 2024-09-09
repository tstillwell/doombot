__Doom Kane and Abel__

Two different AI approaches to playing DOOM.

One is basded on opencv and uses computer vision and hardcoded heuristics / rules.

The other is based on pytorch and uses machine learning (RNN) and is a modified version of the Arnold project
(see https://github.com/glample/Arnold/ for original source code).

Agents are evaluated in zombie_deathmatch benchmark map which is 24 spanwed zombies.
Zombie_Deathmatch map is a modified version from the vizdoom examples, with mobs removed and custom ACS scripting
added to control the zombie spawning.

Evaluation scores are output when running scripts.

Windows Installation instructions

Install wsl (tested using wsl ubuntu on windows 11) env

`sudo apt-get update`

`sudo apt install python3.10-venv`

`sudo apt-get install libgl1`

`sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev`

`python3 -m venv venv`

`source /venv/bin/activate`

`pip install requirements.txt`

To run the CV agent

`python3 new.py`

To run the ML agent

`cd arnoldFixed/Arnold`

then

`./run.sh zombie_deathmatch`

To train the ML agent (from the 'arnoldFixed/Arnold' directory)

`python arnold.py --scenario deathmatch --wad zombie_deathmatch --n_bots 8 --action_combinations "move_fb;move_lr;turn_lr;attack" --frame_skip 4 --game_features "enemy" --network_type dqn_rnn --recurrence lstm --n_rec_updates 5`


__Evaluation Results__

Abel (aka Doombot / CV Agent)

run 1 - 16823
run 2 - 22574
run 3 - 25200
run 4 - 24040
run 5 - 24992
run 6 - 23072
run 7 - 24704

Mean - 23057.85

Kane (aka Arnold / ML Agent)

run 1 - 19256
run 2 - 20240
run 3 - 22080
run 4 - 21304
run 5 - 22208
run 6 - 22224
run 7 - 21208

Mean - 21217.14
