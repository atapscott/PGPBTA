from playerworld.players import Player, MasterOfCeremonies
from storyworld.storyworld import Storyworld
from storyworld.entities import Entity

class Playerworld:

    players: list = None
    master_of_ceremonies: MasterOfCeremonies = None

    def __init__(self):
        self.players = []
        self.master_of_ceremonies = MasterOfCeremonies()

    def create_player(self, **kwargs):

        player_character: Player = Player(**kwargs)
        self.players.append(player_character)

    def get_player_by_name(self, player_name: str) -> Player:
        indexed_players: dict = {pc.name: pc for pc in self.players}
        return indexed_players[player_name]

    def get_player_characters(self) -> list:
        return [p.character for p in self.players]

    def run_turn(self, storyworld: Storyworld):
        for player_character in [p.character for p in self.players]:
            print(storyworld.get_performed_agent_actions(player_character))


