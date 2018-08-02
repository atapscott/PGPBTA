from storyworld.entities import Entity, Agent, PlayerCharacter, Threat
from storyworld.moves import Move
import json
import random
from utils import utils


class Storyworld:
    entities: list = None
    playbooks: list = None
    moves: list = None
    generator_data: dict = None
    scenes: list = None
    threat_types: list = None

    def __init__(self, **kwargs):

        self.entities = []
        self.player_moves = []
        self.scenes = []
        self.generator_data = {}
        self.load_data()

    def load_data(self):

        with open('data/playbooks.json', 'r', encoding='utf8') as infile:
            serialized_playbook_data_list: list = json.load(infile)

            self.playbooks = serialized_playbook_data_list

        with open('data/player_moves.json', 'r', encoding='utf8') as infile:
            serialized_player_moves: list = json.load(infile)

            self.player_moves = [Move(**smd) for smd in serialized_player_moves]

        with open('data/generators.json', 'r', encoding='utf8') as infile:
            serialized_generator_data: dict = json.load(infile)

            self.generator_data = serialized_generator_data

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
        pc.name = self.get_generator_data_item('names')
        pc.attributes = {'agent': 'True', 'person': 'True', 'owner': kwargs['owner']}
        pc.moves = self.player_moves
        self.entities.append(pc)
        return pc

    def create_threat(self, **kwargs) -> Threat:

        threat: Threat = Threat(**kwargs)
        threat_type = self.get_threat_type_by_name(kwargs['threat_type_name'])
        threat.name = self.get_generator_data_item('names')
        threat.attributes = {'agent': 'True', 'threat_type_name': kwargs['threat_type_name']}
        threat.moves = threat_type['moves']
        self.entities.append(threat)
        return threat

    def get_player_characters(self) -> list:
        return [e for e in self.entities if 'owner' in e.attributes.keys()]

    def get_candidate_agent_moves(self, candidate_entities: list = None) -> dict:
        agent_moves: dict = {}
        if candidate_entities is None:
            candidate_entities = self.entities

        for agent_entity in [e for e in self.entities if isinstance(e, Agent) and e in candidate_entities]:
            agent_moves[agent_entity.name] = self._get_eligible_agent_moves(agent_entity, candidate_entities)

        return agent_moves

    def get_playbook_by_name(self, playbook_name: str) -> dict:
        return {p['name']: p for p in self.playbooks}[playbook_name]

    def get_threat_type_by_name(self, threat_type_name: str) -> dict:
        return {tt['name']: tt for tt in self.threat_types}[threat_type_name]

    def get_entity_by_name(self, entity_name: str) -> Entity:
        return {e.name: e for e in self.entities}[entity_name]

    def get_generator_data_item(self, generator_name: str):
        random.shuffle(self.generator_data[generator_name])
        value = self.generator_data[generator_name][0]
        del self.generator_data[generator_name][0]
        return value

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
                eligible_moves.append((move, ))

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
        link_amount = random.randint(0, len(history_links))

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

        link_mod_amount = random.randint(0, len(history_link_mods))

        if link_mod_amount > fellow_player_amount:
            link_mod_amount = fellow_player_amount

        history_link_mod_list: list = random.sample(history_link_mods, link_mod_amount)

        while len(history_link_mod_list) < fellow_player_amount:
            history_link_mod_list.append({"base": default_value})

        random.shuffle(history_link_mod_list)

        return history_link_mod_list

    def get_initial_history(self) -> list:

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
                        (player_character, history_link['plot'], paired_character))

                stored_history_link_value = paired_character.get_attribute('hist_{}'.format(player_character.name))
                history_link_modded_value: int = self._resolve_hist_value(stored_history_link_value,
                                                                          history_link_mod['base'])

                paired_character.set_attribute('hist_{}'.format(player_character.name),
                                               history_link_modded_value)
                if 'plot' in history_link_mod.keys():
                    initial_history.append(
                        (player_character, history_link_mod['plot'], paired_character))

        return initial_history

    def get_npc_entities(self)->list:
        return [e for e in self.entities if not e.is_player_character()]

    def get_next_scene_entities(self, next_scene_players: list, previous_scenes: list):
        next_scene_entities: list = [nsp.character for nsp in next_scene_players]
        npc_entities: list = self.get_npc_entities()
        npc_amount: int = random.randint(0, len(npc_entities))
        next_scene_entities = next_scene_entities + random.sample(npc_entities, npc_amount)
        return  next_scene_entities
