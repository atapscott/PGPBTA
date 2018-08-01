class Move:

    name: str = None
    reflexive: bool = False
    prerequisite: list = None
    id: str = None

    def __init__(self, **kwargs):
        self.name = 'Unnamed'
        self.prerequisites = []
        self.reflexive = False

        self.__dict__ = kwargs

    def is_reflexive(self)->bool:
        return self.reflexive

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.id
