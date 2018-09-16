from game_states import GameStates

def handle_keys(input, game_state):

	if input:
		if game_state == GameStates.PLAYER_TURN:
			return handle_player_turn_keys(input)
		elif game_state == GameStates.TARGETING:
			return handle_targeting_keys(input)
		elif game_state == GameStates.DIRECTIONAL_TARGETING:
			return handle_directional_targeting_keys(input)
		elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
			return handle_inventory_keys(input)
		elif game_state == GameStates.CHARACTER_SCREEN:
			return handle_character_screen_keys(input)
		elif game_state == GameStates.LEVEL_UP:
			return handle_level_up_keys(input)
		elif game_state == GameStates.PLAYER_DEAD:
			return handle_player_dead_keys(input)

	return {}

def handle_mouse(mouse_event):
	if mouse_event:
		(x, y) = mouse_event.cell

		if mouse_event.button == 'LEFT':
			return {'left_click': (x, y)}

		elif mouse_event.button == 'RIGHT':
			return {'right_click': (x, y)}

	return {}

def handle_player_turn_keys(input):

	if input.key == 'UP' or input.key == 'KP8' or input.char == 'k':
		return {'move': (0, -1)}
	elif input.key == 'DOWN' or input.key == 'KP2' or input.char == 'j':
		return {'move': (0, 1)}
	elif input.key == 'LEFT' or input.key == 'KP4' or input.char == 'h':
		return {'move': (-1, 0)}
	elif input.key == 'RIGHT' or input.key == 'KP6' or input.char == 'l':
		return {'move': (1, 0)}
	#up left
	elif input.char == 'y' or input.key == 'KP7':
		return {'move': (-1, -1)}
	#up right
	elif input.char == 'u' or input.key == 'KP9':
		return {'move': (1, -1)}
	#down left
	elif input.char == 'b' or input.key == 'KP1':
		return {'move': (-1, 1)}
	#down right
	elif input.char == 'n' or input.key == 'KP3':
		return {'move': (1, 1)}

	#pickup
	elif input.char == ',':
		return {'pickup': True}

	#drop
	elif input.char == 'd':
		return {'drop': True}

	#show inventory
	elif input.char == 'i':
		return {'inventory' : True}

	#show character screen
	elif input.char == 'c':
		return {'character_screen' : True}

	#wait
	elif (input.char == '.' and not input.shift) or input.key == 'KP5':
		return {'wait': True}

	#traverse the downstairs with '>'
	elif input.char == '.' and input.shift:
		return {'go_down': True}

	#ALT+ENTER fullscreen
	if input.key == 'ENTER' and input.alt:
		return {'fullscreen': True}

	elif input.key == 'ESCAPE':
		return{'exit': True}

	#default to no action
	return {}

def handle_inventory_keys(input):
	if not input.char:
		return {}

	index = ord(input.char) - ord('a')

	if index >= 0:
		return {'inventory_index': index}

	if input.key == 'ENTER' and input.alt:
		return {'fullscreen': True}

	elif input.key == 'ESCAPE':
		return{'exit': True}

	#default to no action
	return {}


def handle_main_menu(input):
	if input:
		if input.char == 'a':
			return {'new': True}
		elif input.char == 'b':
			return {'load': True}
		elif input.char == 'c' or input.key == 'ESCAPE':
			return {'exit': True}

	return {}

def handle_player_name_keys(input):
	if input:
		if input.key == 'ENTER':
			return{'done': True}
		elif input.key == 'ESCAPE':
			return{'exit': True}
		elif input.key == 'BACKSPACE':
			return{'backspace': True}
		elif input.char:
			if input.shift:
				return{'new_char': input.char.upper()}
			else:
				return{'new_char': input.char}

	return {}


def handle_targeting_keys(input):
	if input.key == 'ESCAPE':
		return{'exit': True}

	return {}


def handle_directional_targeting_keys(input):
	if input:
		if input.key == 'ESCAPE':
			return{'exit': True}
		elif input.key == 'UP' or input.key == 'KP8' or input.char == 'k':
			return {'direction_selected': 'N'}
		elif input.key == 'DOWN' or input.key == 'KP2' or input.char == 'j':
			return {'direction_selected': 'S'}
		elif input.key == 'LEFT' or input.key == 'KP4' or input.char == 'h':
			return {'direction_selected': 'W'}
		elif input.key == 'RIGHT' or input.key == 'KP6' or input.char == 'l':
			return {'direction_selected': 'E'}
		elif input.char == 'y' or input.key == 'KP7':
			return {'direction_selected': 'NW'}
		elif input.char == 'u' or input.key == 'KP9':
			return {'direction_selected': 'NE'}
		elif input.char == 'b' or input.key == 'KP1':
			return {'direction_selected': 'SW'}
		elif input.char == 'n' or input.key == 'KP3':
			return {'direction_selected': 'SE'}
		elif (input.char == '.' and not input.shift) or input.key == 'KP5':
			return {'direction_selected': 'self'}

	return {}


def handle_character_screen_keys(input):
	if input.key == 'ESCAPE' or input.char == 'c':
		return{'exit': True}

	return {}


def handle_level_up_keys(input):
	if input:
		if input.char == 'a':
			return {'level_up': 'constitution'}
		elif input.char == 'b':
			return {'level_up': 'strength'}
		elif input.char == 'c':
			return {'level_up': 'agility'}
		elif input.char == 'd':
			return {'level_up': 'dexterity'}
		elif input.char == 'e':
			return {'level_up': 'endurance'}

	return {}


#show a limited menu if the player is dead
def handle_player_dead_keys(input):

	if input.char == 'i':
		return {'inventory' : True}

	if input.key == 'ENTER' and input.alt:
		return {'fullscreen': True}

	elif input.key == 'ESCAPE':
		return {'exit': True}

	return {}