import random
from storyworld.entities import Entity
from storyworld.storyworld import Storyworld
from playerworld.playerworld import Playerworld


class GameManager:

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

        storyworld.assign_initial_bio()

        return playerworld, storyworld


if __name__ == "__main__":
    playerworld, storyworld = GameManager.new_game(player_names=['Player 1', 'Player 2', 'Player 3', 'Player 4'])
    for ps in storyworld.plot_structure:
        print("{} the {}".format(ps[0].name, ps[0].attributes['playbook_name'].lower()),
              ps[1],
              "{} the {}".format(ps[2].name, ps[2].attributes['playbook_name'].lower()))

    '''
    from pprint import pprint
    pprint(storyworld.get_agent_moves())
    playerworld.run_turn(storyworld)
    '''

    pass
