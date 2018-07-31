from storyworld.entities import Entity
from storyworld.moves import Move
import json
import random


class Storyworld:

    entities: list = None
    playbooks: list = None
    moves: list = None
    generator_data: dict = None
    plot_structure: list = None

    def __init__(self, **kwargs):

        self.entities = []
        self.moves = []
        self.plot_structure = []
        self.generator_data = {}
        self.load_data()

    def load_data(self):

        with open('data/playbooks.json', 'r', encoding='utf8') as infile:
            serialized_playbook_data_list: list = json.load(infile)

            self.playbooks = serialized_playbook_data_list

        with open('data/moves.json', 'r', encoding='utf8') as infile:
            serialized_move_data_list: list = json.load(infile)

            self.moves = [Move(**smd) for smd in serialized_move_data_list]

        with open('data/generators.json', 'r', encoding='utf8') as infile:
            serialized_generator_data: dict = json.load(infile)

            self.generator_data = serialized_generator_data

    def create_entity(self, **kwargs):

        entity: Entity = Entity(**kwargs)
        self.entities.append(entity)

    def get_player_characters(self)->list:
        return [e for e in self.entities if 'owner' in e.attributes.keys()]

    def get_agent_moves(self) -> dict:
        agent_moves: dict = {}

        for agent_entity in [e for e in self.entities if 'agent' in e.attributes.keys()]:
            agent_moves[agent_entity.name] = self._get_eligible_agent_moves(agent_entity)

        return agent_moves

    def get_playbook_by_name(self, playbook_name: str)->dict:
        return {p['name']: p for p in self.playbooks}[playbook_name]

    def get_entity_by_name(self, entity_name: str)->Entity:
        return {e.name: e for e in self.entities}[entity_name]

    def get_generator_data_item(self, generator_name: str):
        random.shuffle(self.generator_data[generator_name])
        value = self.generator_data[generator_name][0]
        del self.generator_data[generator_name][0]
        return value

    def _get_eligible_agent_moves(self, agent: Entity) -> list:
        eligible_moves: list = []
        for move in self.moves:

            if not move.is_reflexive():
                object_candidates: list = self._get_eligible_object_entities(move.prerequisites, agent, (agent,))
                for object_candidate in object_candidates:
                    eligible_moves.append((move, object_candidate))
            elif move.is_reflexive() and self._is_eligible_agent_object_pairing(move.prerequisites, agent):
                eligible_moves.append((move))

        return eligible_moves

    @staticmethod
    def _is_eligible_agent_object_pairing(prerequisites: list, agent: Entity, object: Entity = None) -> bool:
        assert 'agent' in agent.attributes.keys()
        eligible: bool = True
        for prerequisite in prerequisites:
            eligible *= eval(prerequisite)

        return eligible

    def _get_eligible_object_entities(self, prerequisites: list, agent: Entity, exclusions: tuple = ())->list:
        eligible_object_entities: list = []
        for object_candidate in [e for e in self.entities if e.id not in [ex.id for ex in exclusions]]:

            if self._is_eligible_agent_object_pairing(prerequisites, agent, object_candidate):
                eligible_object_entities.append(object_candidate)

        return eligible_object_entities



