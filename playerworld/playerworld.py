from playerworld.players import Player, MasterOfCeremonies
import random


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

    def get_next_scene_players(self, indexed_pc_spotlight: dict) -> list:
        sorted_pcs = sorted(indexed_pc_spotlight, key=indexed_pc_spotlight.get)
        pc2player = {p.character.name: p for p in self.players}
        sorted_players = [pc2player[pc] for pc in sorted_pcs]
        player_amount: int = random.randint(1, len(self.players))
        player_choice = sorted_players[:player_amount]
        return player_choice

