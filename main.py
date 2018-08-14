import random
from storyworld.entities import Entity, Agent
from storyworld.storyworld import Storyworld, Move
from playerworld.playerworld import Playerworld
from storyworld.behavior import BehaviorModel
from storyworld.nl_renderer import NLRenderer


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
    BehaviorModel.test_sanity()

    @classmethod
    def assign_playbook(cls, player_character: Agent):
        picked_playbooks: list = [e.attributes['playbook_name'] for e in cls.storyworld.entities if
                                  'owner' in e.attributes.keys() and 'playbook_name' in e.attributes.keys()]
        playbook: dict = random.choice([p for p in cls.storyworld.playbooks if p['name'] not in picked_playbooks])
        player_character.attributes['playbook_name'] = playbook['name']
        player_character.attributes['stats'] = random.choice(playbook['stats'])
        player_character.moves += [Move(**md) for md in playbook['moves']]

    @classmethod
    def new_game(cls, **kwargs):
        cls.playerworld: Playerworld = Playerworld()
        cls.storyworld: Storyworld = Storyworld()
        NLRenderer.initialize(storyworld=cls.storyworld)

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
    def move_has_tags(cls, move: Move, tag_list: list) -> bool:
        eligible: bool = True
        for tag in tag_list:
            eligible *= tag in move.tags

        return eligible

    @classmethod
    def get_next_agent_move(cls, scene: Scene, indexed_candidate_agent_moves: dict) -> tuple:

        if len(scene.actions) == 0:
            next_behavior_tag = 'initiator'

        else:
            last_action: tuple = scene.actions[-1]
            last_move: Move = last_action[1]
            last_behavior_tag: str = last_action[3]
            next_behavior_tag = BehaviorModel.get_next_behavior_tag(last_behavior_tag, len(scene.actions))

            if len(scene.entities) < 3 and next_behavior_tag in ('interference'):
                next_behavior_tag = 'follow_up'

        agent_candidates: list = []
        object_candidates: list = []

        if next_behavior_tag == 'end':
            return None, None, None, 'end'

        elif next_behavior_tag in ('initiator', 'follow_up'):
            agent_candidates = [e for e in scene.entities if isinstance(e, Agent)]
            object_candidates = scene.entities

        elif next_behavior_tag == 'reply':
            agent_candidates = [last_action[2]] if last_action[2] is not None else [scene.actions[-2][0]]
            object_candidates = [last_action[0]]

        elif next_behavior_tag == 'interference':
            interrupted_entity_names = [last_action[0], last_action[2]]
            agent_candidates = [e for e in scene.entities if isinstance(e, Agent) and e not in interrupted_entity_names]
            object_candidates = interrupted_entity_names

        filtered_indexed_candidate_agent_moves: dict = {}
        for agent_candidate in agent_candidates:
            candidate_agent_moves: list = indexed_candidate_agent_moves[agent_candidate.name]
            candidate_agent_moves = [cam for cam in candidate_agent_moves if
                                     cls.move_has_tags(cam[0], [next_behavior_tag])]

            candidate_agent_moves = [cam for cam in candidate_agent_moves if
                                     len(cam) == 1 or cam[1] in object_candidates]

            filtered_indexed_candidate_agent_moves[agent_candidate.name] = candidate_agent_moves

        agent = random.choice([ac for ac in agent_candidates if ac in agent_candidates])

        player_move_match = random.choice(filtered_indexed_candidate_agent_moves[agent.name])

        if player_move_match[0].is_reflexive():
            return agent, player_move_match[0], None, next_behavior_tag
        else:
            return agent, player_move_match[0], player_move_match[1], next_behavior_tag

    @classmethod
    def run_scene(cls):

        next_scene: Scene = Scene()
        next_scene.name = 'Scene {}'.format(len(cls.scenes))
        next_scene.players = cls.playerworld.get_next_scene_players()
        next_scene.entities = cls.storyworld.get_next_scene_entities(next_scene.players, cls.scenes)

        indexed_candidate_agent_moves: dict = cls.storyworld.get_candidate_agent_moves(next_scene.entities)

        while True:
            next_agent_action: tuple = cls.get_next_agent_move(next_scene, indexed_candidate_agent_moves)

            if next_agent_action[3] == 'end':
                break

            next_scene.actions.append(next_agent_action)

        cls.scenes.append(next_scene)


if __name__ == "__main__":

    GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'])
    i: int = 0
    while i < 100:
        GameManager.run_scene()
        i += 1

    for i, scene in enumerate(GameManager.scenes):

        print('\nESCENA {}'.format(i))

        if scene.entities is None:
            print(scene.actions)
        else:
            print(GameManager.storyworld.get_scene_configuration(scene))
            for action in scene.actions:
                render_data: dict = {'agent': action[0], 'object': action[2]}
                template_id: str = action[1].id if isinstance(action[1], Move) else action[1]
                try:
                    print(NLRenderer.get_rendered_nl(template_id, render_data))
                except KeyError:
                    print(action)

    pass
