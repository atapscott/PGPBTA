from storyworld.storyworld import Storyworld, Move
from playerworld.playerworld import Playerworld
from storyworld.behavior import PlayerBehaviorModel, MCBehaviorModel
from storyworld.nl_renderer import NLRenderer
from storyworld.entities import Entity, Agent, Threat, Location, PlayerCharacter
from utils import utils
from copy import deepcopy
import random


class Scene:
    name: str = None
    actions: list = None
    players: list = None
    entities: list = None
    template: dict = None

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.actions = []

    def get_entity_actions(self, entity: Entity) -> list:
        return [a for a in self.actions if a[1].id == entity.id]

    def get_location(self) -> Location:
        [location] = [e for e in self.entities if 'location' in e.attributes.keys()]
        return location

    def has_action(self, candidate_action) -> bool:
        # b = candidate_action.__repr__() in [a.__repr__() for a in self.actions]
        # print("{} in {}?".format((candidate_action[0], candidate_action[1]), [(a[0], a[1]) for a in self.actions]))
        b1 = (candidate_action[0], candidate_action[1]) in [(a[0], a[1]) for a in self.actions]
        b2 = (candidate_action[1], candidate_action[2]) in [(a[1], a[2]) for a in self.actions if a[2]]
        # print("{} or {}".format(b1, b2))
        return b1 or b2

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class GameManager:
    scenes: list = None
    playerworld: Playerworld = None
    storyworld: Storyworld = None
    mps: dict = None

    assert PlayerBehaviorModel.test_sanity()
    assert MCBehaviorModel.test_sanity()

    @classmethod
    def get_story_template_elements(cls, scene_template_name: str, scene_element_name: str) -> list:
        element_list: list = []
        for scene in [s for s in cls.scenes if s.template]:
            if scene.template['name'] == scene_template_name:
                for se_k, se_v in scene.template['scene_elements'].items():
                    if se_k == scene_element_name:
                        element_list.append(se_v)

        return element_list

    @classmethod
    def get_player_character_spotlight(cls, player_character: PlayerCharacter) -> int:
        player_character_spotlight: int = 0
        player_scenes: list = cls.get_entity_agent_scenes(player_character)  # type: List[Scene]

        for scene in player_scenes:
            for action in scene.actions:
                if action[0] == player_character:
                    player_character_spotlight += (2 * 1 / player_character.get_player().spotlight_modifier)
                elif action[2] and action[2] == player_character:
                    player_character_spotlight += (1 * 1 / player_character.get_player().spotlight_modifier)

        return player_character_spotlight

    @classmethod
    def get_entity_agent_scenes(cls, agent_entity: Agent) -> list:
        featured_scenes: list = []
        for s in [s for s in cls.scenes if s.entities]:
            if agent_entity.name in [e.name for e in s.entities if isinstance(e, Agent)]:
                featured_scenes.append(s)

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
        cls.scenes = []
        cls.playerworld: Playerworld = Playerworld()
        cls.storyworld: Storyworld = Storyworld(**kwargs)
        NLRenderer.initialize(storyworld=cls.storyworld)
        cls.storyworld.load_story_template_by_name(kwargs['story_template'])

        if 'mps' in kwargs.keys():
            cls.mps = kwargs['mps']

        for player_data in kwargs['player_data']:
            cls.playerworld.create_player(**player_data)
            player = cls.playerworld.get_player_by_name(player_data['name'])
            player.character = cls.storyworld.create_player_character(owner=player)
            cls.assign_playbook(player.character)

        cls.storyworld.story_template.initial_history = cls.storyworld.get_initial_history()

        n: int = 6
        while n > 0:
            cls.storyworld.entities.append(cls.storyworld.create_location())
            n -= 1

        cls.storyworld.create_threat(threat_type_name='grotesque')
        cls.storyworld.create_threat(threat_type_name='warlord')

    @classmethod
    def move_has_tags(cls, move: Move, tag_list: list) -> bool:
        eligible: bool = True
        for tag in tag_list:
            eligible *= tag in move.tags

        return eligible

    @classmethod
    def choose_move(cls, candidate_agent_moves: list, scene: Scene) -> tuple:
        """
        Pick an agent-move pairing with an appropriate mps
        :param candidate_agent_moves: candidate tuples of move and agent
        :param scene: current scene
        :return: the matching of move and agent that goes well with the scene's mps
        """

        match_weights: list = []
        # If the scene template has mps, use those values
        if scene.template and 'mps' in scene.template.keys():
            [mental_weight, physical_weight, social_weight] = scene.template['mps']['mental'], scene.template['mps'][
                'physical'], scene.template['mps']['social']
        # Fall back to general mps from the GameManager constructor
        elif cls.mps:
            [mental_weight, physical_weight, social_weight] = cls.mps['mental'], cls.mps['physical'], cls.mps['social']
        else:
            return random.choice(candidate_agent_moves)

        for cam in candidate_agent_moves:
            move_mps = cam[0].mps
            [move_mental, move_physical, move_social] = move_mps['mental'], move_mps['physical'], move_mps['social']
            match_weights.append(move_mental*mental_weight+move_physical*physical_weight+move_social*social_weight)

        if match_weights.count(match_weights[0]) == len(match_weights):
            return random.choice(candidate_agent_moves)

        return random.choices(candidate_agent_moves, match_weights)[0]

    @classmethod
    def get_next_player_action(cls, scene: Scene, pc_spotlight: dict, start_chain: bool = False) -> tuple:

        player_characters: list = [e for e in scene.entities if e.is_player_character()]

        indexed_candidate_player_moves: dict = cls.storyworld.get_candidate_moves(
            [e for e in scene.entities if e.is_player_character()], scene.entities)

        last_action: tuple = scene.actions[-1]
        last_move: Move = last_action[1]
        last_behavior_tag: str = last_action[3]

        if start_chain:

            if last_behavior_tag in ('mc_threat'):
                next_behavior_tag = random.choice(['pc_reply', 'pc_interference'])
            else:
                next_behavior_tag = 'pc_initiator'

        else:
            next_behavior_tag = PlayerBehaviorModel.get_next_behavior_tag(last_behavior_tag, len(scene.actions))

            # Disable pc_interferences if there are less than 3 potential agents
            if len(player_characters) < 3 and next_behavior_tag in ('pc_interference'):
                next_behavior_tag = 'pc_follow_up'

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
            interrupted_entities = [last_action[0]]
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

        # limit the spotlight to characters present in the scene
        pc_spotlight = {name: weight for name, weight in pc_spotlight.items() if
                        name in [ac.name for ac in agent_candidates]}
        agent = cls.storyworld.get_entity_by_name(utils.weighted_choice(pc_spotlight))

        # player_move_match = random.choice(filtered_indexed_candidate_agent_moves[agent.name])
        player_move_match = cls.choose_move(filtered_indexed_candidate_agent_moves[agent.name], scene)

        if player_move_match[0].is_reflexive():
            return agent, player_move_match[0], scene, next_behavior_tag
        else:
            return agent, player_move_match[0], player_move_match[1], next_behavior_tag

    @classmethod
    def get_next_mc_action(cls, scene: Scene, pc_spotlight: dict) -> tuple:

        next_move: Move = None

        indexed_mc_moves: dict = {m.id: m for m in GameManager.storyworld.mc_moves}

        if 'mc_scene_conf' not in [a[3] for a in scene.actions]:
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

                threat_move_match = cls.choose_move(indexed_candidate_threat_moves[candidate_threat.name], scene)
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
    def run_story_introduction(cls):
        intro_scene: Scene = Scene()
        intro_scene.name = "Introduction Scene"
        intro_scene.players = cls.storyworld.get_player_characters()
        intro_scene.entities = cls.storyworld.entities
        indexed_mc_moves: dict = {m.id: m for m in GameManager.storyworld.mc_moves}
        intro_move = indexed_mc_moves['mc_intro']

        intro_scene.actions.append((None, intro_move, None, 'mc_intro'))

        cls.scenes.append(intro_scene)

    @classmethod
    def run_scene(cls):

        next_scene: Scene = Scene()
        next_scene.name = 'Scene {}'.format(len(cls.scenes))

        # Assign scene template if applicable
        if len(cls.storyworld.story_template.scene_templates) > 0:
            random.shuffle(cls.storyworld.story_template.scene_templates)
            next_scene.template = deepcopy(cls.storyworld.story_template.scene_templates[0])
            next_scene.template['template_resolving_action'] = None
            for se_key, se_value in next_scene.template['scene_elements'].items():
                arguments: dict = {}
                if 'arguments' in se_value.keys():
                    for arg_k, arg_v in se_value['arguments'].items():
                        arguments[arg_k] = eval(arg_v)
                next_scene.template['scene_elements'][se_key] = utils.parse_complex_value(se_value, **arguments)
            next_scene.name += ' ' + next_scene.template['name']

        indexed_pc_spotlight: dict = {pc.name: cls.get_player_character_spotlight(pc) for pc in
                                      cls.storyworld.get_player_characters()}

        next_scene.players = cls.playerworld.get_next_scene_players(indexed_pc_spotlight)

        indexed_threat_spotlight: dict = {e.name: len(cls.get_entity_agent_scenes(e)) for e in
                                          cls.storyworld.get_npc_entities() if isinstance(e, Threat)}

        next_scene.entities = cls.storyworld.get_next_scene_entities(next_scene.players, indexed_threat_spotlight)

        if next_scene.template:
            # Ensure the target from the template is present in the entities
            if "target_npc" in next_scene.template['scene_elements'].keys() and next_scene.template['scene_elements'][
                'target_npc'] not in next_scene.entities:
                next_scene.entities.append(next_scene.template['scene_elements']['target_npc'])
        next_scene.entities.append(
            random.choice([e for e in cls.storyworld.entities if isinstance(e, Location)]))

        # Configure the scene
        next_scene.actions.append(cls.get_next_mc_action(next_scene, pc_spotlight=indexed_pc_spotlight))

        n: int = 4

        while next_scene.template['template_resolving_action'] is None or n > 0:

            indexed_pc_spotlight = {pc.name: cls.get_player_character_spotlight(pc) for pc in
                                    cls.storyworld.get_player_characters()}

            while True:
                next_mc_action: tuple = cls.get_next_mc_action(next_scene, indexed_pc_spotlight)
                if next_mc_action[3] == 'mc_end':
                    break

                next_scene.actions.append(next_mc_action)

            initial_pc_scene: bool = True
            while True:
                next_pc_action: tuple = cls.get_next_player_action(next_scene, indexed_pc_spotlight, initial_pc_scene)
                if next_pc_action[3] == 'pc_end':
                    break

                if next_scene.has_action(next_pc_action):
                    break

                # Check for scene template resolution
                if next_scene.template and "resolve_action_condition" in next_scene.template.keys():
                    if eval(next_scene.template["resolve_action_condition"]):
                        next_scene.template['template_resolving_action'] = next_pc_action

                next_scene.actions.append(next_pc_action)
                if initial_pc_scene:
                    initial_pc_scene = False

                n -= 1

        cls.scenes.append(next_scene)

    @classmethod
    def run_story_ending(cls):
        ending_scene: Scene = Scene()
        ending_scene.name = "Ending Scene"
        ending_scene.players = cls.storyworld.get_player_characters()
        ending_scene.entities = cls.storyworld.entities
        indexed_mc_moves: dict = {m.id: m for m in GameManager.storyworld.mc_moves}
        ending_move = indexed_mc_moves['mc_ending']

        ending_scene.actions.append((None, ending_move, None, 'mc_ending'))

        cls.scenes.append(ending_scene)

    @classmethod
    def render_action(cls, scene: Scene, action, pcs, pcs_nice, npcs) -> str:

        rendered_action: str = ""

        render_data: dict = {'agent': action[0], 'object': action[2], 'scene': scene, 'pcs': pcs,
                             'pcs_nice': pcs_nice, 'npcs': npcs}

        # Default action from a generic scene
        if isinstance(action[1], Move) and \
                action[3] not in cls.storyworld.story_template.render_templates.keys() and \
                not (scene.template and action[3] in scene.template['render_templates'].keys()):
            template_id: str = action[1].id
        # Need to check if action belongs to the story template
        elif action[3] in cls.storyworld.story_template.render_templates.keys():
            template_id = cls.storyworld.story_template.render_templates[action[3]]['template_id']

            for se_key in cls.storyworld.story_template.render_templates[action[3]]['elements']:
                cls.storyworld.story_template.story_elements[se_key] = utils.parse_complex_value(
                    cls.storyworld.story_template.story_elements[se_key])

            render_data = {**render_data, **cls.storyworld.story_template.story_elements}
        # Need to check if action belongs to a scene template
        elif scene.template and action[3] in scene.template['render_templates'].keys():
            template_id = scene.template['render_templates'][action[3]]
            render_data = {**render_data, **scene.template["scene_elements"]}

        # History actions fall here
        else:
            template_id = action[1]

        rendered_sentence = NLRenderer.get_rendered_nl(template_id, render_data)
        rendered_action += rendered_sentence.__str__()

        # Attach relevant initial history
        if not isinstance(action[1], str) and not action[1].reflexive \
                and cls.storyworld.story_template.have_initial_history(action[0], action[2]):
            initial_history_action = cls.storyworld.story_template.get_initial_history_action(action[0],
                                                                                              action[2])
            cls.storyworld.story_template.initial_history.remove(initial_history_action)
            rendered_initial_history = cls.render_action(scene, initial_history_action, pcs, pcs_nice, npcs)
            if random.randint(0, 1) > 0:
                rendered_action += ' ' + rendered_initial_history
            else:
                rendered_action = rendered_initial_history + ' ' + rendered_action

        # Attach relevant scene template resolution
        elif scene.template and action == scene.template['template_resolving_action']:
            rendered_resolution = cls.render_action(scene, (action[0], action[1], action[2], 'resolution'), pcs,
                                                    pcs_nice, npcs)
            rendered_action += ' ' + rendered_resolution

        return rendered_action

    @classmethod
    def render_scene(cls, scene: Scene):

        rendered_scene: str = ''

        pcs: list = [e.name for e in scene.entities if e.is_player_character()]
        pcs_nice: list = [e.print_nice_name() for e in scene.entities if e.is_player_character()]
        npcs: list = [e.print_nice_name() for e in scene.entities if
                      not e.is_player_character() and 'person' in e.attributes.keys()]
        for action in scene.actions:

            try:
                rendered_scene += cls.render_action(scene, action, pcs, pcs_nice, npcs) + '\n'

            except KeyError:
                rendered_scene += action.__str__() + '\n'

        return rendered_scene
