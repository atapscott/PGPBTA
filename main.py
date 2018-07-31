import random
from utils import utils
from storyworld.entities import Entity
from storyworld.storyworld import Storyworld
from playerworld.playerworld import Playerworld


class GameManager:

    @classmethod
    def resolve_hist_value(cls, base_self_turn_hist: int, paired_character_hist_mod) -> int:
        if isinstance(paired_character_hist_mod, str):
            return base_self_turn_hist + eval(paired_character_hist_mod)
        elif isinstance(paired_character_hist_mod, int):
            return paired_character_hist_mod
        elif isinstance(paired_character_hist_mod, dict):
            return cls.resolve_hist_value(base_self_turn_hist, utils.parse_complex_value(paired_character_hist_mod))

    @classmethod
    def generate_self_hist_link_list(cls, fellow_player_amount: int, history_links: list, default_value: int) -> list:
        link_amount = random.randint(0, len(history_links))

        if link_amount > fellow_player_amount:
            link_amount = fellow_player_amount

        history_link_list: list = random.sample(history_links, link_amount)

        while len(history_link_list) < fellow_player_amount:
            history_link_list.append({"base": default_value})

        random.shuffle(history_link_list)

        return history_link_list

    @classmethod
    def generate_self_hist_link_mod_list(cls, fellow_player_amount: int, history_link_mods: list,
                                         default_value: int) -> list:

        link_mod_amount = random.randint(0, len(history_link_mods))

        if link_mod_amount > fellow_player_amount:
            link_mod_amount = fellow_player_amount

        history_link_mod_list: list = random.sample(history_link_mods, link_mod_amount)

        while len(history_link_mod_list) < fellow_player_amount:
            history_link_mod_list.append({"base": default_value})

        random.shuffle(history_link_mod_list)

        return history_link_mod_list

    @classmethod
    def assign_initial_bio(cls, playerworld: Playerworld, storyworld: Storyworld):

        indexed_history_link_mods: dict = {}
        for player in playerworld.players:
            character: Entity = player.character
            playbook: dict = storyworld.get_playbook_by_name(character.attributes['playbook_name'])
            fellow_characters: list = [e for e in storyworld.entities if
                                       e.id != character.id and e.is_player_character()]
            indexed_history_link_mods[character.__repr__()] = cls.generate_self_hist_link_mod_list(
                len(fellow_characters), playbook['hist']['others_turn']['history_links'],
                playbook['hist']['others_turn']['base'])

        for player in playerworld.players:
            character: Entity = player.character
            playbook: dict = storyworld.get_playbook_by_name(character.attributes['playbook_name'])

            fellow_characters: list = [e for e in storyworld.entities if
                                       e.id != character.id and e.is_player_character()]

            history_links: list = cls.generate_self_hist_link_list(len(fellow_characters),
                                                                   playbook['hist']['self_turn']['history_links'],
                                                                   playbook['hist']['self_turn']['base'])

            paired_character: Entity
            for paired_character in fellow_characters:
                history_link: dict = history_links[0]
                del history_links[0]

                history_link_mods = indexed_history_link_mods[character.__repr__()]
                history_link_mod = history_link_mods[0]
                del history_link_mods[0]

                paired_character.set_attribute('hist_{}_{}'.format(player.name, player.id), history_link['base'])
                if 'plot' in history_link.keys():
                    storyworld.plot_structure.append(
                        (character, history_link['plot'], paired_character))

                stored_history_link_value = paired_character.get_attribute('hist_{}_{}'.format(player.name, player.id))
                history_link_modded_value: int = cls.resolve_hist_value(stored_history_link_value,
                                                                        history_link_mod['base'])

                paired_character.set_attribute('hist_{}_{}'.format(player.name, player.id), history_link_modded_value)
                if 'plot' in history_link_mod.keys():
                    storyworld.plot_structure.append(
                        (character, history_link_mod['plot'], paired_character))

    @classmethod
    def assign_playbook(cls, storyworld: Storyworld, entity: Entity):
        picked_playbooks: list = [e.attributes['playbook_name'] for e in storyworld.entities if 'owner' in e.attributes.keys() and 'playbook_name' in e.attributes.keys()]
        playbook: dict = random.choice([p for p in storyworld.playbooks if p['name'] not in picked_playbooks])
        entity.attributes['playbook_name'] = playbook['name']
        entity.attributes['stats'] = random.choice(playbook['stats'])

    @classmethod
    def new_game(cls, **kwargs) -> (Playerworld, Storyworld):
        playerworld: Playerworld = Playerworld()
        storyworld: Storyworld = Storyworld()

        moves: dict = storyworld.get_agent_moves()

        for player_name in kwargs['player_names']:
            playerworld.create_player(name=player_name)
            player = playerworld.get_player_by_name(player_name)
            character_name = storyworld.get_generator_data_item('names')
            storyworld.create_entity(name='{}'.format(character_name),
                                     attributes={'owner': player.id, 'agent': 'True', 'person': 'True'})
            player.character = storyworld.get_entity_by_name('{}'.format(character_name))
            cls.assign_playbook(storyworld, player.character)

        storyworld.create_entity(name='{} the warlord'.format(storyworld.get_generator_data_item('names')),
                                 attributes={'agent': 'True', 'person': 'True', 'warlord': 'True'})

        cls.assign_initial_bio(playerworld, storyworld)

        return playerworld, storyworld


if __name__ == "__main__":
    playerworld, storyworld = GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'])

    for ps in storyworld.plot_structure:
        print("{} the {}".format(ps[0].name, ps[0].attributes['playbook_name'].lower()),
              ps[1],
              "{} the {}".format(ps[2].name, ps[2].attributes['playbook_name'].lower()))

    from pprint import pprint
    pprint(storyworld.get_agent_moves())
    pass
