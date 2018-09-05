import random
from game_manager import GameManager

if __name__ == "__main__":

    i: int = 25

    while i > 0:

        print("\n-----------------------\n-----------------------\n-----------------------\nSTORY {}\n".format(25 - i))

        GameManager.new_game(player_data=[{"name": 'Player 1', "spotlight_modifier": 4},
                                          {"name": 'Player 2'},
                                          {"name": 'Player 3'},
                                          {"name": 'Player 4'}],
                             mps={"mental": 0, "physical": 0, "social": 1},
                             story_template="journey")

        GameManager.run_story_introduction()
        n: int = GameManager.storyworld.story_template.scene_length
        while n > 0:
            GameManager.run_scene()
            n -= 1
        GameManager.run_story_ending()

        for scene in GameManager.scenes:
            print(GameManager.render_scene(scene))

        i -= 1
