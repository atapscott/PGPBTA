import random
from game_manager import GameManager

if __name__ == "__main__":

    i: int = 25

    while i > 0:

        print("\n-----------------------\n-----------------------\n-----------------------\nSTORY {}".format(25 - i))

        GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'], story_template="journey")

        print("\nENTITIES")
        for e in GameManager.storyworld.entities:
            print(e.print_nice_name())
        print(('\n'))

        GameManager.run_story_introduction()
        n: int = random.randint(2, 6)
        while n > 0:
            GameManager.run_scene()
            n -= 1

        for scene in GameManager.scenes:
            print(GameManager.render_scene(scene))

        i -= 1
