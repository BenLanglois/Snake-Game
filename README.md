# Snake Game

**Video of the highscore:** https://i.imgur.com/HYVrA2k.mp4

This is a recreation of the snake game. It was made using Python 3.6.2 and pygame 1.9.3. The game was designed to be played by either a human or a neural network.

The game is customizable, with all settings found in game.py starting on line 13. You can choose the size of the board, the game speed, whether the game should be played by a human or by the computer, and more. You can also modify the neural network's settings staring on line 29 of game.py.

If you wish to let the neural network play, set the `HUMAN_PLAYER` setting to `False`. If you wish to start evolving the neural network from scratch, set the `LOAD_NETWORK` option to `False`. After each generation, the program will log the network with the highest score to log.txt. If you wish to load a previously evolved network, set `LOAD_NETWORK` to  `True` and paste the fittest network in log.txt. An example neural network can be found in best_snake.txt and will achieve a score of 17 if `GAME_SEED` is set to 3 and `BOARD_SIZE` is set to 25. A video of this network running can also be found in Highscore.mp4
