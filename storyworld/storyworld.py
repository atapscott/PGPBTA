from storyworld.entities import Entity, Agent, PlayerCharacter, Threat, Location
from storyworld.moves import Move
from storyworld.nl_renderer import NLRenderer
from storyworld.story_template import StoryTemplate
import json
import random
from utils import utils

class Storyworld:
    entities: list = None
    playbooks: list = None
    moves: list = None
    generator_data: dict = {}
    scenes: list = None
    threat_types: list = None
    story_template = None

    def __init__(self, **kwargs):

        self.entities = []
        self.player_moves = []
        self.mc_moves = []
        self.scenes = []
        self.load_data()

    def load_data(self):

        with open('data/playbooks.json', 'r', encoding='utf8') as infile:
            serialized_playbook_data_list: list = json.load(infile)

            self.playbooks = serialized_playbook_data_list

        with open('data/player_moves.json', 'r', encoding='utf8') as infile:
            serialized_player_moves: list = json.load(infile)

            self.player_moves = [Move(**smd) for smd in serialized_player_moves]

        with open('data/mc_moves.json', 'r', encoding='utf8') as infile:
            serialized_mc_moves: list = json.load(infile)

            self.mc_moves = [Move(**smd) for smd in serialized_mc_moves]

        with open('data/generators.json', 'r', encoding='utf8') as infile:
            serialized_generator_data: dict = json.load(infile)

            Storyworld.generator_data = serialized_generator_data

        with open('data/threat_types.json', 'r', encoding='utf8') as infile:
            serialized_threat_type_data: dict = json.load(infile)

            for td in serialized_threat_type_data:
                td['moves'] = [Move(**md) for md in td['moves']]

            self.threat_types = serialized_threat_type_data

    def create_entity(self, **kwargs) -> Entity:

        entity: Entity = Entity(**kwargs)
        self.entities.append(entity)

        return entity

    def create_player_character(self, **kwargs) -> PlayerCharacter:

        pc: PlayerCharacter = PlayerCharacter(**kwargs)
        pc.name, pc.gender = self.get_generator_data_item('names')
        if pc.gender == 'mf':
            pc.gender = random.choice(('m', 'f'))
        pc.attributes = {'agent': 'True', 'person': 'True', 'owner': kwargs['owner']}
        pc.moves = [pm for pm in self.player_moves]
        self.entities.append(pc)
        return pc

    def create_threat(self, **kwargs) -> Threat:

        threat: Threat = Threat(**kwargs)
        threat_type = self.get_threat_type_by_name(kwargs['threat_type_name'])
        threat.name, threat.gender = self.get_generator_data_item('names')
        if threat.gender == 'mf':
            threat.gender = random.choice(('m', 'f'))
        threat.attributes = {
            'agent': 'True',
            'threat_type_name': kwargs['threat_type_name'],
            'impulse': utils.parse_complex_value(threat_type['impulse'])
        }

        for k, v in threat_type['attributes'].items():
            threat.attributes[k] = v

        threat.moves = threat_type['moves']
        self.entities.append(threat)
        return threat

    def get_player_characters(self) -> list:
        return [e for e in self.entities if 'owner' in e.attributes.keys()]

    def get_candidate_moves(self, candidate_agent_entities: list = None,
                            candidate_object_entities: list = None) -> dict:
        candidate_agent_moves: dict = {}
        if candidate_agent_entities is None:
            candidate_agent_entities = [e for e in self.entities if e.is_player_character()]

        if candidate_object_entities is None:
            candidate_object_entities = self.entities

        for candidate_agent_entity in candidate_agent_entities:
            candidate_agent_moves[candidate_agent_entity.name] = \
                self._get_eligible_agent_moves(candidate_agent_entity, candidate_object_entities)

        return candidate_agent_moves

    def get_playbook_by_name(self, playbook_name: str) -> dict:
        return {p['name']: p for p in self.playbooks}[playbook_name]

    def get_threat_type_by_name(self, threat_type_name: str) -> dict:
        return {tt['name']: tt for tt in self.threat_types}[threat_type_name]

    def get_entity_by_name(self, entity_name: str) -> Entity:
        return {e.name: e for e in self.entities}[entity_name]

    def load_story_template_by_name(self, st_name: str):
        with open('data/story_templates.json', 'r', encoding='utf8') as infile:
            serialized_story_templates_list: list = json.load(infile)

            self.story_template = StoryTemplate(**{st['name']: st for st in serialized_story_templates_list}[st_name])

    @classmethod
    def get_generator_data_item(cls, generator_name: str, delete_result_from_seeder: bool = True):

        generator_dict: dict = cls.generator_data

        if '_' in generator_name:
            split_index = generator_name.split('_')

            while len(split_index) > 1:
                generator_dict = generator_dict[split_index[0]]

                split_index = split_index[1:]

            generator_name = split_index[0]

        random.shuffle(generator_dict[generator_name])
        result = generator_dict[generator_name][0]

        if delete_result_from_seeder:
            del generator_dict[generator_name][0]
        return result

    def _get_eligible_agent_moves(self, agent: Agent, candidate_entities: list = None) -> list:
        eligible_moves: list = []
        for move in agent.moves:

            if not move.is_reflexive():
                candidate_entities = [e for e in candidate_entities if e.id != agent.id]
                object_candidates: list = self._get_eligible_object_entities(move.prerequisites, agent,
                                                                             candidate_entities)
                for object_candidate in object_candidates:
                    eligible_moves.append((move, object_candidate))
            elif move.is_reflexive() and self._is_eligible_agent_object_pairing(move.prerequisites, agent):
                eligible_moves.append((move,))

        return eligible_moves

    @staticmethod
    def _is_eligible_agent_object_pairing(prerequisites: list, agent: Agent, object: Entity = None) -> bool:

        eligible: bool = True
        for prerequisite in prerequisites:
            eligible *= eval(prerequisite)

        return eligible

    def _get_eligible_object_entities(self, prerequisites: list, agent: Agent, candidate_entities: list = None) -> list:
        eligible_object_entities: list = []
        for object_candidate in [e for e in self.entities if e in candidate_entities]:

            if self._is_eligible_agent_object_pairing(prerequisites, agent, object_candidate):
                eligible_object_entities.append(object_candidate)

        return eligible_object_entities

    @classmethod
    def _resolve_hist_value(cls, base_self_turn_hist: int, paired_character_hist_mod) -> int:
        if isinstance(paired_character_hist_mod, str):
            return base_self_turn_hist + eval(paired_character_hist_mod)
        elif isinstance(paired_character_hist_mod, int):
            return paired_character_hist_mod
        elif isinstance(paired_character_hist_mod, dict):
            return cls._resolve_hist_value(base_self_turn_hist, utils.parse_complex_value(paired_character_hist_mod))

    @classmethod
    def _generate_self_hist_link_list(cls, fellow_player_amount: int, history_links: list, default_value: int) -> list:
        # link_amount = random.randint(0, len(history_links))
        # TODO check this manual fix
        link_amount = len(history_links)

        if link_amount > fellow_player_amount:
            link_amount = fellow_player_amount

        history_link_list: list = random.sample(history_links, link_amount)

        while len(history_link_list) < fellow_player_amount:
            history_link_list.append({"base": default_value})

        random.shuffle(history_link_list)

        return history_link_list

    @classmethod
    def _generate_self_hist_link_mod_list(cls, fellow_player_amount: int, history_link_mods: list,
                                          default_value: int) -> list:

        # link_mod_amount = random.randint(0, len(history_link_mods))
        # TODO check this manual fix
        link_mod_amount = len(history_link_mods)

        if link_mod_amount > fellow_player_amount:
            link_mod_amount = fellow_player_amount

        history_link_mod_list: list = random.sample(history_link_mods, link_mod_amount)

        while len(history_link_mod_list) < fellow_player_amount:
            history_link_mod_list.append({"base": default_value})

        random.shuffle(history_link_mod_list)

        return history_link_mod_list

    def get_initial_history(self, amount: int) -> list:

        initial_history: list = []

        player_characters: list = [e for e in self.entities if e.is_player_character()]

        indexed_history_link_mods: dict = {}
        player_character: Entity
        for player_character in player_characters:
            playbook: dict = self.get_playbook_by_name(player_character.attributes['playbook_name'])
            fellow_characters: list = [e for e in self.entities if
                                       e.id != player_character.id and e.is_player_character()]
            indexed_history_link_mods[player_character.__repr__()] = self._generate_self_hist_link_mod_list(
                len(fellow_characters), playbook['hist']['others_turn']['history_links'],
                playbook['hist']['others_turn']['base'])

        for player_character in player_characters:
            playbook: dict = self.get_playbook_by_name(player_character.attributes['playbook_name'])

            fellow_characters: list = [e for e in self.entities if
                                       e.id != player_character.id and e.is_player_character()]

            history_links: list = self._generate_self_hist_link_list(len(fellow_characters),
                                                                     playbook['hist']['self_turn']['history_links'],
                                                                     playbook['hist']['self_turn']['base'])

            paired_character: Entity
            for paired_character in fellow_characters:
                history_link: dict = history_links[0]
                del history_links[0]

                history_link_mods = indexed_history_link_mods[player_character.__repr__()]
                history_link_mod = history_link_mods[0]
                del history_link_mods[0]

                paired_character.set_attribute('hist_{}'.format(player_character.name), history_link['base'])
                if 'plot' in history_link.keys():
                    initial_history.append(
                        (player_character, history_link['plot'], paired_character, 'initial_history'))

                stored_history_link_value = paired_character.get_attribute('hist_{}'.format(player_character.name))
                history_link_modded_value: int = self._resolve_hist_value(stored_history_link_value,
                                                                          history_link_mod['base'])

                paired_character.set_attribute('hist_{}'.format(player_character.name),
                                               history_link_modded_value)
                if 'plot' in history_link_mod.keys():
                    initial_history.append(
                        (player_character, history_link_mod['plot'], paired_character, 'initial_history'))

        if amount > len(initial_history):
            amount = len(initial_history)

        return random.sample(initial_history, amount)

    def get_npc_entities(self) -> list:
        return [e for e in self.entities if e.is_non_player_character()]

    def get_next_scene_entities(self, next_scene_players: list, indexed_threat_spotlight: dict):
        next_scene_entities: list = [nsp.character for nsp in next_scene_players]

        sorted_npc_names = sorted(indexed_threat_spotlight, key=indexed_threat_spotlight.get)

        npc_amount: int = random.randint(0 if len(next_scene_players) > 1 else 1, len(sorted_npc_names) % 3)

        next_scene_entities = next_scene_entities + [self.get_entity_by_name(e) for e in
                                                     sorted_npc_names[:npc_amount]]
        return next_scene_entities

    @classmethod
    def create_location(cls) -> Location:
        new_location: Location = Location()
        [base, gender] = cls.get_generator_data_item('location_names', True)
        new_location.attributes['base_location'] = base
        new_location.attributes['elements'] = []

        element_amount: int = 6
        while element_amount > 0:
            element: str = cls.get_generator_data_item('location_elements', False)
            if element not in new_location.get_elements():
                new_location.add_element(element)
                element_amount -= 1

        if random.randint(1, 5) < 3:
            pre_adjective: str = cls.get_generator_data_item('adjectives_general', False)
            pre_adjective = NLRenderer.gender_flex(pre_adjective, gender)
            base = "{} {}".format(pre_adjective, base)

        post_adjective: str = cls.get_generator_data_item('adjectives_general', False)
        post_adjective = NLRenderer.gender_flex(post_adjective, gender)
        base = "{} {}".format(base, post_adjective)

        new_location.name = base
        new_location.gender = gender

        return new_location
