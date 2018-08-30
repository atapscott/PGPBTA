from utils import utils


class StoryTemplate:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        for se_key, se_value in self.story_elements.items():
            if not isinstance(se_value, str):
                self.story_elements[se_key] = utils.parse_complex_value(se_value)
