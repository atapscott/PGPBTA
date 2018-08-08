import math
import random


class BehaviorModel:

    state_model_row_names = ('initiator', 'follow_up', 'reply', 'interference', 'end')

    state_map = [
        [0, 4 / 5, 0, 1 / 5, 0],
        [0, 7 / 20, 7 / 20, 4 / 20, 2 / 20],
        [0, 35 / 100, 35 / 100, 20 / 100, 2 / 20],
        [0, 18 / 20, 0, 0, 2 / 20],
        [0, 0, 0, 0, 1]
    ]

    @classmethod
    def get_next_behavior_tag(cls, current_behavior_tag: str, accumulated_actions: int = None)->str:

        current_index: int = cls.state_model_row_names.index(current_behavior_tag)
        current_transitions: list = cls.state_map[current_index]
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

        return cls.state_model_row_names[next_state]

    @classmethod
    def test_sanity(cls)->bool:
        for state in cls.state_map:
            assert (math.ceil(sum(state))) == 1
        return True


'''
current_state: str = 'initiator'
while current_state != 'end':
    print(current_state)
    current_state = BehaviorModel.get_next_behavior_tag(current_state)


current_state = 0
while current_state < 4:
    print(BehaviorModel.state_model_row_names[current_state])
    rand_index = random.randint(1, 100)
    current_state_transitions = BehaviorModel.state_map[current_state]
    discarded_probabilities = 0
    for index, transition in enumerate(current_state_transitions):
        if rand_index < transition * 100 + discarded_probabilities:
            current_state = index
            break
        else:
            discarded_probabilities += transition * 100
'''
