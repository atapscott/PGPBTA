class Move:

    reflexive: bool = False
    prerequisites: list = None
    tags: list = None
    id: str = None

    def __init__(self, **kwargs):
        self.prerequisites = []
        self.reflexive = False

        self.__dict__ = kwargs

        if 'tags' not in self.__dict__.keys():
            self.tags = []

    def is_reflexive(self)->bool:
        return self.reflexive

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id
