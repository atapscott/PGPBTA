import random
from storyworld.entities import Entity, Agent, Threat, Location, PlayerCharacter
from storyworld.storyworld import Storyworld, Move
from playerworld.playerworld import Playerworld
from storyworld.behavior import PlayerBehaviorModel, MCBehaviorModel
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

    def get_location(self) -> Location:
        [location] = [e for e in self.entities if 'location' in e.attributes.keys()]
        return location

    def has_action(self, candidate_action) -> bool:
        # print(candidate_action.__repr__())
        # print([a.__repr__() for a in self.actions])
        b = candidate_action.__repr__() in [a.__repr__() for a in self.actions]
        # print(b)
        return b

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class GameManager:
    scenes: list = []
    playerworld: Playerworld = None
    storyworld: Storyworld = None
    assert PlayerBehaviorModel.test_sanity()
    assert MCBehaviorModel.test_sanity()

    @classmethod
    def get_entity_agent_scenes(cls, agent_entity: Agent) -> int:
        featured_scenes: int = 0
        for s in [s for s in cls.scenes if s.entities]:
            if agent_entity.name in [e.name for e in s.entities if isinstance(e, PlayerCharacter)]:
                featured_scenes += 1

        return featured_scenes

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

        n: int = 6
        while n > 0:
            cls.storyworld.entities.append(cls.storyworld.create_location())
            n -= 1

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
    def get_next_player_action(cls, scene: Scene, start_chain: bool = False) -> tuple:

        player_characters: list = [e for e in scene.entities if e.is_player_character()]

        indexed_candidate_player_moves: dict = cls.storyworld.get_candidate_moves(
            [e for e in scene.entities if e.is_player_character()], scene.entities)

        if start_chain:
            next_behavior_tag = 'pc_initiator'

        else:
            last_action: tuple = scene.actions[-1]
            last_move: Move = last_action[1]
            last_behavior_tag: str = last_action[3]
            next_behavior_tag = PlayerBehaviorModel.get_next_behavior_tag(last_behavior_tag, len(scene.actions))

            # Disable pc_interferences if there are less than 3 potential agents
            if len(player_characters) < 3 and next_behavior_tag in ('pc_interference'):
                next_behavior_tag = 'pc_follow_up'
            elif next_behavior_tag == 'pc_reply' and last_action[2] and not last_action[2].is_player_character():
                next_behavior_tag = 'pc_end'

        agent_candidates: list = []
        object_candidates: list = []

        if next_behavior_tag == 'pc_end':
            return None, None, None, 'pc_end'

        elif next_behavior_tag in ('pc_initiator', 'pc_follow_up'):
            agent_candidates = player_characters
            object_candidates = scene.entities

        elif next_behavior_tag == 'pc_reply':
            agent_candidates = [last_action[2]] if last_action[2] is not None else [scene.actions[-2][0]]
            object_candidates = [last_action[0]]

        elif next_behavior_tag == 'pc_interference':
            interrupted_entities = [last_action[0], last_action[2]]
            agent_candidates = [e for e in scene.entities if
                                e.is_player_character() and e not in interrupted_entities]
            object_candidates = interrupted_entities

        filtered_indexed_candidate_agent_moves: dict = {}
        for agent_candidate in agent_candidates:
            candidate_agent_moves: list = indexed_candidate_player_moves[agent_candidate.name]
            candidate_agent_moves = [cam for cam in candidate_agent_moves if
                                     cls.move_has_tags(cam[0], [next_behavior_tag])]

            candidate_agent_moves = [cam for cam in candidate_agent_moves if
                                     len(cam) == 1 or cam[1] in object_candidates]

            filtered_indexed_candidate_agent_moves[agent_candidate.name] = candidate_agent_moves

        agent = random.choice([ac for ac in agent_candidates if ac in agent_candidates])

        player_move_match = random.choice(filtered_indexed_candidate_agent_moves[agent.name])

        if player_move_match[0].is_reflexive():
            return agent, player_move_match[0], scene, next_behavior_tag
        else:
            return agent, player_move_match[0], player_move_match[1], next_behavior_tag

    @classmethod
    def get_next_mc_action(cls, scene: Scene, configure_scene: bool = False) -> tuple:

        next_move: Move = None

        indexed_mc_moves: dict = {m.id: m for m in GameManager.storyworld.mc_moves}

        if configure_scene:
            next_move = indexed_mc_moves['mc_scene_conf']
            return None, next_move, None, 'mc_scene_conf'

        last_action: tuple = scene.actions[-1]
        last_move: Move = last_action[1]
        last_behavior_tag: str = last_action[3]
        next_behavior_tag: str = MCBehaviorModel.get_next_behavior_tag(last_behavior_tag, len(
            scene.actions))

        while next_behavior_tag == 'mc_threat' and len([e for e in scene.entities if isinstance(e, Threat)]) < 1:
            next_behavior_tag: str = MCBehaviorModel.get_next_behavior_tag(last_behavior_tag, len(
                scene.actions))

        if next_behavior_tag == 'mc_threat':
            candidate_actions: list = list([])

            pcs: list = [e for e in scene.entities if e.is_player_character()]
            threats: list = [e for e in scene.entities if isinstance(e, Threat)]

            if len(threats) > 0:
                indexed_candidate_threat_moves: dict = cls.storyworld.get_candidate_moves(
                    threats, pcs)
                candidate_threat = random.choice(threats)
                threat_move_match = random.choice(indexed_candidate_threat_moves[candidate_threat.name])
                candidate_actions.append((candidate_threat, threat_move_match[0], threat_move_match[1], 'mc_threat'))

                return random.choice(candidate_actions)

        elif next_behavior_tag == 'mc_descriptive':

            npcs: list = [e for e in scene.entities if not e.is_player_character() and 'person' in e.attributes.keys()]

            [location] = [e for e in scene.entities if isinstance(e, Location)]

            next_move = indexed_mc_moves['mc_descriptive']

            return None, next_move, location, next_behavior_tag

        elif next_behavior_tag == 'mc_ominous':

            foreign_locations: list = [e for e in cls.storyworld.entities if e not in scene.entities and
                                       isinstance(e, Location)]
            location: Location = random.choice(foreign_locations)
            next_move = indexed_mc_moves['mc_ominous']

            return None, next_move, location, next_behavior_tag

        return None, next_move, None, next_behavior_tag

    @classmethod
    def run_scene(cls):

        next_scene: Scene = Scene()
        next_scene.name = 'Scene {}'.format(len(cls.scenes))
        indexed_pc_spotlight: dict = {pc.name: cls.get_entity_agent_scenes(pc) for pc in
                                      cls.storyworld.get_player_characters()}
        next_scene.players = cls.playerworld.get_next_scene_players(indexed_pc_spotlight)
        next_scene.entities = cls.storyworld.get_next_scene_entities(next_scene.players, cls.scenes)
        next_scene.entities.append(
            random.choice([e for e in cls.storyworld.entities if isinstance(e, Location)]))

        next_scene.actions.append(cls.get_next_mc_action(next_scene, True))

        n: int = random.randint(1, 3)
        while n > 0:

            next_mc_action: tuple = cls.get_next_mc_action(next_scene)
            while next_mc_action[3] != 'mc_end':
                next_scene.actions.append(next_mc_action)
                next_mc_action = cls.get_next_mc_action(next_scene)
                while next_scene.has_action(next_mc_action):
                    next_mc_action = cls.get_next_mc_action(next_scene)

            next_pc_action: tuple = cls.get_next_player_action(next_scene, True)
            while next_pc_action[3] != 'pc_end':
                next_scene.actions.append(next_pc_action)
                next_pc_action = cls.get_next_player_action(next_scene)
                while next_scene.has_action(next_pc_action):
                    next_pc_action = cls.get_next_player_action(next_scene)

            n -= 1

        cls.scenes.append(next_scene)


if __name__ == "__main__":

    GameManager.new_game(player_names=['Player 1'])
    i: int = 0
    while i < 100:
        GameManager.run_scene()
        i += 1

    for i, scene in enumerate(GameManager.scenes):

        rendered_sentences: dict = {}
        print('\n')

        if scene.entities is None:
            print(scene.actions)
        else:
            pcs: list = [e.print_nice_name() for e in scene.entities if e.is_player_character()]
            npcs: list = [e.print_nice_name() for e in scene.entities if
                          not e.is_player_character() and 'person' in e.attributes.keys()]
            for action in scene.actions:

                if action[1] and NLRenderer.has_template(action[1].id):
                    render_data: dict = {'agent': action[0], 'object': action[2], 'scene': scene, 'pcs': pcs,
                                         'npcs': npcs}
                    template_id: str = action[1].id if isinstance(action[1], Move) else action[1]

                    rendered_sentence = NLRenderer.get_rendered_nl(template_id, render_data)
                    print(rendered_sentence)
                else:
                    print(action)

    pass
