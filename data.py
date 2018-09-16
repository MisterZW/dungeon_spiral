import shelve
import os

def save_game(player, entities, game_map, log, game_state):
    with shelve.open('save_game', 'n') as file:
        file['player_index'] = entities.index(player)
        file['entities'] = entities
        file['game_map'] = game_map
        file['log'] = log
        file['game_state'] = game_state

def load_game():
    if not os.path.isfile('save_game.dat') and not ('save_game'):
        raise FileNotFoundError

    with shelve.open('save_game', 'r') as file:
        player_index = file['player_index'] 
        entities = file['entities'] 
        game_map = file['game_map']
        log = file['log']
        game_state = file['game_state']

    #needed to ensure that all references are correct internally
    player = entities[player_index]
    game_map.player = player
    game_map.entities = entities
    
    return (player, entities, game_map, log, game_state)