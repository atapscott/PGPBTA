import random
from storyworld.entities import Entity
from storyworld.storyworld import Storyworld
from playerworld.playerworld import Playerworld
from playerworld.players import Player
import itertools


class Scene:
    name: str = None
    actions: list = None
    players: list = None
    entities: list = None

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.actions = []

    def get_entity_actions(self, entity: Entity) -> list:
        return [a for a in self.actions if a[1].id == entity.id]


class GameManager:
    scenes: list = []
    playerworld: Playerworld = None
    storyworld: Storyworld = None

    @classmethod
    def get_performed_agent_actions(cls, agent_entity):
        is_agent_entity_action = \
            lambda p: True if 'mov_' in p[1] and 'agent' in p[0].attributes.keys() and p[
                0].id == agent_entity.id else False
        actions: list = list(itertools.chain([s.actions for s in self.scenes]))
        return [p for p in self.plot_structure if is_agent_entity_action(p)]

    @classmethod
    def assign_playbook(cls, entity: Entity):
        picked_playbooks: list = [e.attributes['playbook_name'] for e in cls.storyworld.entities if
                                  'owner' in e.attributes.keys() and 'playbook_name' in e.attributes.keys()]
        playbook: dict = random.choice([p for p in cls.storyworld.playbooks if p['name'] not in picked_playbooks])
        entity.attributes['playbook_name'] = playbook['name']
        entity.attributes['stats'] = random.choice(playbook['stats'])

    @classmethod
    def new_game(cls, **kwargs):
        cls.playerworld: Playerworld = Playerworld()
        cls.storyworld: Storyworld = Storyworld()

        for player_name in kwargs['player_names']:
            cls.playerworld.create_player(name=player_name)
            player = cls.playerworld.get_player_by_name(player_name)
            player.character = cls.storyworld.create_player_character(owner=player.id)
            cls.assign_playbook(player.character)

        cls.storyworld.create_threat(threat_type_name='warlord')
        cls.storyworld.create_threat(threat_type_name='warlord')
        cls.storyworld.create_threat(threat_type_name='warlord')

        initial_history_scene: Scene = Scene(name='initial_history')
        initial_history_scene.players = cls.playerworld.players
        initial_history_scene.actions = cls.storyworld.get_initial_history()

        cls.scenes.append(initial_history_scene)

    @classmethod
    def get_next_agent_move(cls, agent: Entity, candidate_agent_moves: dict) -> tuple:

        player_move_match = random.choice(candidate_agent_moves)

        if player_move_match[0].is_reflexive():
            return agent, player_move_match[0]
        else:
            return agent, player_move_match[0], player_move_match[1]

    @classmethod
    def run_scene(cls):

        next_scene: Scene = Scene()
        next_scene.name = 'Scene {}'.format(len(cls.scenes))
        next_scene.players = cls.playerworld.get_next_scene_players()
        next_scene.entities = cls.storyworld.get_next_scene_entities(next_scene.players, cls.scenes)

        indexed_candidate_agent_moves: dict = cls.storyworld.get_candidate_agent_moves(next_scene.entities)

        current_player: Player
        for current_player in next_scene.players:
            next_agent_move: tuple = cls.get_next_agent_move(current_player.character, indexed_candidate_agent_moves[
                current_player.character.name])
            next_scene.actions.append(next_agent_move)

        cls.scenes.append(next_scene)


if __name__ == "__main__":
    GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'])
    GameManager.run_scene()
    GameManager.run_scene()
    GameManager.run_scene()
    GameManager.run_scene()
    GameManager.run_scene()
    GameManager.run_scene()

    for scene in GameManager.scenes:
        print("SCENE: {} with {}".format(scene.name.upper(), scene.entities if scene.entities is not None else 'the past'))
        for action in scene.actions:
            print(action)

    pass
