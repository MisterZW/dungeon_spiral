import tdl
import tcod
import textwrap
from colors import Colors
from components.equipment_slots import EquipmentSlots
from input_handlers import handle_player_name_keys

def menu(display, header, options, width):
    con = display.con
    root = display.root_console

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after textwrap) and one line per option
    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tdl.Console(width, height)

    # print the header, with wrapped text
    window.draw_rect(0, 0, width, height, None, fg=Colors.WHITE, bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0 + i, header_wrapped[i])

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        window.draw_str(0, y, text, bg=None)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = display.SCREEN_WIDTH // 2 - width // 2
    y = display.SCREEN_HEIGHT // 2 - height // 2
    root.blit(window, x, y, width, height, 0, 0)

#shows a menu with each inventory item as an ordinal option
#shows which items are equipped as well as the # of charges remaining on wands
def inventory_menu(display, header, player):
    inventory_width = 50

    descriptors = [None, '(in main hand)', '(in off hand)', '(on head)', '(on body)', '(on feet)', '(on hands)',
        '(around neck)', '(on left finger)', '(on right finger)', '(on your shoulders)']

    options = []
        
    for item in player.inventory.items:

        if item.item.charges > 1:
            options.append(item.name + ' ({0} charges remain)'.format(item.item.charges))
        elif item.item.charges == 1:
            options.append(item.name + ' ({0} charge remains)'.format(item.item.charges))
        elif item in player.equipment.equipment:
            slot_index = item.equippable.slot.value
            options.append(item.name + ' ' + descriptors[slot_index])
        else:
            options.append(item.name)

    menu(display, header, options, inventory_width)

def vendor_main_menu(display, header, player):
    menu_width = 45
    options = [' BUY', ' SELL', ' EXIT']

    menu(display, header, options, menu_width)

def vendor_sell_menu(display, header, player, vendor):
    menu_width = 45
    options = []
    for item in vendor.vendor.stock:
        options.append(item.name)

    menu(display, header, options, menu_width)

def vendor_buy_menu(display, header, player, vendor):
    menu_width = 45
    options = []
    for item in player.inventory.items:
        options.append(item.name)

    menu(display, header, options, menu_width)

def main_menu(display, background_image):

    background_image.scale(display.SCREEN_WIDTH  * 2, display.SCREEN_HEIGHT * 2)

    background_image.blit_2x(display.root_console, 0, 0)

    title = 'DUNGEON SPIRAL'
    center = (display.SCREEN_WIDTH - len(title)) // 2

    display.root_console.draw_str(center, display.SCREEN_HEIGHT // 2 - 4, title, bg=Colors.BLACK, fg=Colors.WHITE)

    author = 'Development: ZDW              ? during play shows controls'
    center = (display.SCREEN_WIDTH - len(author)) // 2
    display.root_console.draw_str(center, display.SCREEN_HEIGHT - 2, author, bg=Colors.BLACK, fg=Colors.WHITE)

    menu(display, '', [' NEW GAME', ' CONTINUE', ' QUIT'], 24)

def level_up_menu(display, header, player):
    menu_width = 45

    if player.inventory.capacity + 3 <= 26:
        endurance_option = 'Endurance: (+3 carry capacity {0} --> {1}'.format(player.inventory.capacity, player.inventory.capacity + 3)
    else:
        endurance_option = 'Endurance (MAXED)'
        
    options = ['Constitution: (+20HP, {0} --> {1})'.format(player.fighter.max_hp, player.fighter.max_hp + 20),
    'Strength: (+1 power, {0} --> {1})'.format(player.fighter.power, player.fighter.power + 1),
    'Agility: (+1 defense, {0} --> {1})'.format(player.fighter.defense, player.fighter.defense + 1),
    'Dexterity: (+2 accuracy, {0} --> {1})'.format(player.fighter.accuracy, player.fighter.accuracy + 2),
    endurance_option]

    menu(display, header, options, menu_width)


#menu @ game start for player to pick his/her character's name
#returns player name when complete, or None if user hits ESCAPE during selection
def player_name_select(display):

    prompt = 'Who are you?'
    char_name = ''

    window = tdl.Console(display.SCREEN_WIDTH, display.SCREEN_HEIGHT)

    done = False

    while not done:
        window.clear(fg=Colors.WHITE, bg=Colors.BLACK)

        center = (display.SCREEN_WIDTH - len(prompt)) // 2
        window.draw_str(center, display.SCREEN_HEIGHT // 2 - 4, prompt, bg=Colors.BLACK, fg=Colors.WHITE)

        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
        else:
            user_input = None

        if not user_input:
            continue

        player_input = handle_player_name_keys(user_input)
        char = player_input.get('new_char')
        backspace = player_input.get('backspace')
        done = player_input.get('done')
        exit = player_input.get('exit')

        if exit:
            return None
        if backspace:
            char_name = char_name[:-1]
        elif char and len(char_name) < 40:
            char_name += char

        center = (display.SCREEN_WIDTH - len(char_name)) // 2
        window.draw_str(center, display.SCREEN_HEIGHT // 2, char_name, bg=Colors.BLACK, fg=Colors.WHITE)
        display.root_console.blit(window, 0, 0, display.SCREEN_WIDTH, display.SCREEN_HEIGHT, 0, 0)
        tdl.flush()

    return char_name

def character_screen(display, player):
    char_screen_width = 30
    char_screen_height = 17

    window = tdl.Console(char_screen_width, char_screen_height)

    window.draw_rect(0, 0, char_screen_width, char_screen_height, None, fg=Colors.WHITE, bg=None)

    window.draw_str(1, 1, 'Name: {0}'.format(player.name))

    window.draw_str(1, 3, 'Level: {0}'.format(player.level.current_level))
    window.draw_str(1, 4, 'Experience: {0}'.format(player.level.current_xp))
    window.draw_str(1, 5, 'Experience to Level: {0}'.format(player.level.exp_to_next_level))
    
    window.draw_str(1, 7, 'BASE STAT(ADJUSTED STAT)')

    window.draw_str(1, 9, 'Max HP: {0}({1})'.format(player.fighter.base_max_hp, player.fighter.max_hp))
    window.draw_str(1, 10, 'Power: {0}({1})'.format(player.fighter.base_power, player.fighter.power))
    window.draw_str(1, 11, 'Defense: {0}({1})'.format(player.fighter.base_defense, player.fighter.defense))
    window.draw_str(1, 12, 'Accuracy: {0}({1})'.format(player.fighter.base_accuracy, player.fighter.accuracy))
    window.draw_str(1, 13, 'Armor: {0}({1})'.format(player.fighter.base_armor, player.fighter.armor))

    window.draw_str(1, 15, 'Light Radius: {0}({1})'.format(display.gmap.FOV_RADIUS, display.gmap.FOV_RADIUS + player.equipment.fov_bonus))
    window.draw_str(1, 16, 'Carrying Capacity: {0}({1})'.format(player.inventory.base_capacity, player.inventory.capacity))
   
    x = display.SCREEN_WIDTH // 2 - char_screen_width // 2
    y = display.SCREEN_HEIGHT // 2 - char_screen_height // 2
    display.root_console.blit(window, x, y, char_screen_width, char_screen_height, 0, 0)

def controls_screen(display):
    controls_screen_width = 37
    controls_screen_height = 17

    window = tdl.Console(controls_screen_width, controls_screen_height)

    window.draw_rect(0, 0, controls_screen_width, controls_screen_height, None, fg=Colors.WHITE, bg=None)

    window.draw_str(1, 1, 'GENERAL CONTROLS FOR DUNGEON SPIRAL')

    window.draw_str(1, 3, 'Move: ARROWS, VIKEYS, NUMPAD')
    window.draw_str(1, 4, 'Wait: PERIOD, NUMPAD 5')
    window.draw_str(1, 5, 'View entity info: MOUSE HOVER')
    
    window.draw_str(1, 7, 'MENU CONRTOLS')

    window.draw_str(1, 9, 'Display inventory: I')
    window.draw_str(1, 10, 'Display character screen: C')
    window.draw_str(1, 11, 'Show vendor wares: S')
    window.draw_str(1, 12, 'Confirm targeting: L-CLICK')
    window.draw_str(1, 13, 'Cancel targeting: ESC or R-CLICK')

    window.draw_str(1, 15, 'Descend stairs: >')
    window.draw_str(1, 16, 'Save and quit: ESCAPE')
   
    x = display.SCREEN_WIDTH // 2 - controls_screen_width // 2
    y = display.SCREEN_HEIGHT // 2 - controls_screen_height // 2
    display.root_console.blit(window, x, y, controls_screen_width, controls_screen_height, 0, 0)

def message_box(display, header, width):
    menu(display, header, [], width)
