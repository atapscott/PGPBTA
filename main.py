import random
from game_manager import GameManager

if __name__ == "__main__":

    i: int = 25

    while i > 0:

        print("\n-----------------------\n-----------------------\n-----------------------\nSTORY {}\n".format(25 - i))

        GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'], story_template="journey")

        GameManager.run_story_introduction()
        GameManager.run_initial_history_scene()
        n: int = random.randint(2, 4)
        while n > 0:
            GameManager.run_scene()
            n -= 1
        GameManager.run_story_ending()

        for scene in GameManager.scenes:
            print(GameManager.render_scene(scene))

        i -= 1
