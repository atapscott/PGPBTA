from utils import utils
from storyworld.entities import PlayerCharacter


class StoryTemplate:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def have_initial_history(self, pc1: PlayerCharacter, pc2: PlayerCharacter)->bool:
        try:
            self.get_initial_history_action(pc1, pc2)
            return True
        except ValueError:
            return False

    def get_initial_history_action(self, pc1: PlayerCharacter, pc2: PlayerCharacter)->tuple:
        for action in self.initial_history:
            if action[0].name == pc1.name and action[2].name == pc2.name:
                return action
            elif action[2].name == pc1.name and action[0].name == pc2.name:
                return action

        raise ValueError("No relationship between {} and {}".format(pc1, pc2))