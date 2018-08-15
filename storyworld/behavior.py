import math
import random


class PlayerBehaviorModel:

    player_state_model_row_names = ('pc_initiator', 'pc_follow_up', 'pc_reply', 'pc_interference', 'pc_end')

    player_state_map = [
        [0, 4 / 5, 0, 1 / 5, 0],
        [0, 7 / 20, 7 / 20, 4 / 20, 2 / 20],
        [0, 35 / 100, 35 / 100, 20 / 100, 2 / 20],
        [0, 18 / 20, 0, 0, 2 / 20],
        [0, 0, 0, 0, 1]
    ]

    @classmethod
    def get_next_behavior_tag(cls, current_behavior_tag: str, accumulated_actions: int = None)->str:

        current_index: int = cls.player_state_model_row_names.index(current_behavior_tag)
        current_transitions: list = cls.player_state_map[current_index]
        rand_index: int = random.randint(1, 100) + accumulated_actions * 30
        if rand_index > 100:
            rand_index = 100
        discarded_probabilities: int = 0
        next_state: int = None
        for index, transition in enumerate(current_transitions):
            percentage_transition = math.ceil(transition*100)
            if rand_index <= percentage_transition + discarded_probabilities:
                next_state = index
                break
            else:
                discarded_probabilities += percentage_transition

        return cls.player_state_model_row_names[next_state]

    @classmethod
    def test_sanity(cls)->bool:
        for state in cls.player_state_map:
            assert (math.ceil(sum(state))) == 1
        return True


class MCBehaviorModel:

    mc_state_model_row_names = ('mc_scene_conf', 'mc_descriptive', 'mc_ominous', 'mc_threat', 'mc_end')

    mc_state_map = [
        [0, 3 / 7, 3 / 7, 1 / 7, 0],
        [0, 2 / 7, 2 / 7, 1 / 7, 2 / 7],
        [0, 2 / 7, 2 / 7, 1 / 7, 2 / 7],
        [0, 1 / 3, 1 / 3, 0, 1 / 3],
        [0, 0, 0, 0, 1]
    ]

    @classmethod
    def get_next_behavior_tag(cls, current_behavior_tag: str, accumulated_actions: int = None)->str:

        if 'mc_' not in current_behavior_tag:
            return random.choice(['mc_descriptive', 'mc_ominous'])

        current_index: int = cls.mc_state_model_row_names.index(current_behavior_tag)
        current_transitions: list = cls.mc_state_map[current_index]
        rand_index: int = random.randint(1, 100) + accumulated_actions * 2
        if rand_index > 100:
            rand_index = 100
        discarded_probabilities: int = 0
        next_state: int = None
        for index, transition in enumerate(current_transitions):
            percentage_transition = math.ceil(transition*100)
            if rand_index <= percentage_transition + discarded_probabilities:
                next_state = index
                break
            else:
                discarded_probabilities += percentage_transition

        return cls.mc_state_model_row_names[next_state]

    @classmethod
    def test_sanity(cls)->bool:
        for state in cls.mc_state_map:
            assert (math.ceil(sum(state))) == 1
        return True

