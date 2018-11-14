import tdl

from tcod import image_load
from data import load_game, save_game
from menus import main_menu, message_box, player_name_select

from colors import Colors
from map_utils import GameMap, next_floor
from display import Display
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from game_messages import MessageLog, Message
from entity import Entity, get_impassable_entities_at, RenderOrder
from game_states import GameStates
from death import kill_player, kill_monster
from generators.player import initialize_player

def main():
    tdl.set_font('arial12x12.png', greyscale=True, altLayout=True)
    display = Display()  #missing game_map, has an empty log

    show_main_menu = True
    show_load_error = False
    player = None
    entities= []
    state = GameStates.PLAYER_TURN
    game_map = None

    main_menu_background_image = image_load('a.png')

    while not tdl.event.is_window_closed():

        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
        else:
            user_input = None

        if show_main_menu:
            main_menu(display, main_menu_background_image)

            if show_load_error:
                message_box(display, 'No save game to load', 50)

            tdl.flush()

            action = handle_main_menu(user_input)

            new = action.get('new')
            load = action.get('load')
            exit = action.get ('exit')
            fullscreen = action.get('fullscreen')

            if fullscreen:
                tdl.set_fullscreen(not tdl.get_fullscreen())
            if show_load_error and (new or load or exit):
                show_load_error = False
            elif new:
                player_name = player_name_select(display)
                if not player_name:
                    continue
                player, entities, game_map, state = initialize(display, player_name)
                display.write(Message('Chop wood, carry water.'))
                show_main_menu = False
            elif load:
                try:
                    player, entities, game_map, log, state = load_game()
                    display.gmap = game_map
                    display.log = log
                    display.write(Message('Ah, {0} returns. Welcome back.'.format(player.name)))
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error = True
            elif exit:
                break

        else:         
            play(player, entities, game_map, display, state)

            display.root_console.clear()
            display.con.clear()
            display.panel.clear()

            #need to reset message log, player inventory, etc if exiting and returning to main menu
            show_main_menu = True
            show_load_error = False
            display = Display()
            player = None
            game_map = None
            entities = []

def play(player, entities, game_map, display, state):

    mouse_coordinates = (0, 0)
    prev_state = state
    targeting_item = None

    while not tdl.event.is_window_closed():
        
        game_map.player_FOV()
        display.render_all(mouse_coordinates, state, targeting_item)
        tdl.flush()
        display.clear_all()

        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
            elif event.type == 'MOUSEMOTION':
                mouse_coordinates = event.cell
            elif event.type == 'MOUSEDOWN':
                user_mouse_input = event
                break
        else:
            user_input = None
            user_mouse_input = None

        if not (user_input or user_mouse_input):
            continue

        action = handle_keys(user_input, state)
        mouse_action = handle_mouse(user_mouse_input)

        move = action.get('move')
        exit = action.get('exit')
        pickup = action.get('pickup')
        wait = action.get('wait')
        inventory = action.get('inventory')
        drop = action.get('drop')
        shop = action.get('shop')
        buy = action.get('buy')
        sell = action.get('sell')
        sell_index = action.get('vendor_sell_index')
        buy_index = action.get('vendor_buy_index')
        inventory_index = action.get('inventory_index')
        go_down = action.get('go_down')
        level_up = action.get('level_up')
        character_screen = action.get('character_screen')
        fullscreen = action.get('fullscreen')
        direction_selected = action.get('direction_selected')
        controls_screen = action.get('controls_screen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if exit:
            if state in (GameStates.VENDOR_BUY, GameStates.VENDOR_SELL):
                state = prev_state
                prev_state = GameStates.PLAYER_TURN
            elif state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN,
                GameStates.VENDOR_SELECT, GameStates.SHOW_CONTROLS):
                state = prev_state
            elif state in (GameStates.TARGETING, GameStates.DIRECTIONAL_TARGETING):
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, display.log, state)
                return True

        if move and state == GameStates.PLAYER_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy
            if game_map.walkable[dest_x, dest_y]:
                if len(player.inventory.items) <= player.inventory.capacity:
                    target = get_impassable_entities_at(entities, dest_x, dest_y)
                    if target:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    else:   
                        player.move(dx, dy)
                    state = GameStates.ENEMY_TURN
                else:
                    display.write(Message('You are overburdened and cannot move!', Colors.YELLOW))

        elif pickup and state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                display.write(Message('There is nothing here to pick up', Colors.YELLOW))

        if wait and state == GameStates.PLAYER_TURN:
            state = GameStates.ENEMY_TURN

        if inventory:
            prev_state = state
            state = GameStates.SHOW_INVENTORY

        if buy:
            prev_state = state
            state = GameStates.VENDOR_SELL

        if sell:
            prev_state = state
            state = GameStates.VENDOR_BUY

        if character_screen:
            prev_state = state
            state = GameStates.CHARACTER_SCREEN

        if controls_screen:
            prev_state = state
            state = GameStates.SHOW_CONTROLS

        if drop:
            prev_state = state
            state = GameStates.DROP_INVENTORY

        if inventory_index is not None and prev_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, game_map=game_map, source=player))
            else:
                player_turn_results.extend(player.inventory.drop(item))

        if buy_index is not None and prev_state != GameStates.PLAYER_DEAD and buy_index < len(player.inventory.items):
            item = player.inventory.get_and_remove(buy_index)
            vendor = None
            for entity in entities:
                if entity.vendor and entity.x == player.x and entity.y == player.y:
                    vendor = entity
            if vendor:
                vendor.vendor.purchase(item)
                player.inventory.cashola += item.item.price
        if sell_index is not None:
            vendor = None
            item = None
            for entity in entities:
                if entity.vendor and entity.x == player.x and entity.y == player.y:
                    vendor = entity
            if vendor:
                price = vendor.vendor.get_price(sell_index)
                if price is None:
                    display.write(Message('I\'m afraid I don\'t have that listing.', Colors.YELLOW))
                elif player.inventory.cashola < price:
                    display.write(Message('I\'m afraid you can\'t afford that item.', Colors.YELLOW))
                else:
                    item = vendor.vendor.sell(sell_index)
                    
            if item:
                player.inventory.silent_add(item)
                player.inventory.cashola -= item.item.price
            
        if go_down and state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    game_map, entities = next_floor(player, display, entity.stairs.target_floor)
                    break
            else:
                display.write(Message('There are no stairs here.', Colors.YELLOW))

        if shop and state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.vendor and entity.x == player.x and entity.y == player.y:
                    prev_state = state
                    state = GameStates.VENDOR_SELECT
                    break
            else:
                display.write(Message('There are no vendors here.', Colors.YELLOW))

        if state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                item_use_results = player.inventory.use(targeting_item, game_map=game_map, target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if state == GameStates.DIRECTIONAL_TARGETING:
            if direction_selected:
                item_use_results = player.inventory.use(targeting_item, game_map=game_map, direction=direction_selected)
                player_turn_results.extend(item_use_results)

        if level_up:
            if level_up == 'constitution':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'strength':
                player.fighter.base_power += 1
            elif level_up == 'agility':
                player.fighter.base_defense += 1
            elif level_up == 'dexterity':
                player.fighter.base_accuracy += 2
            elif level_up == 'endurance':
                if player.inventory.base_capacity > 23:
                    display.write(Message('You cannot advance endurance further!', Colors.YELLOW))
                    continue
                player.inventory.base_capacity += 3
            state = prev_state

        if fullscreen:
            tdl.set_fullscreen(not tdl.get_fullscreen())

        for player_result in player_turn_results:
            player_message = player_result.get('message')
            dead_entity_PT = player_result.get('dead')
            item_added = player_result.get('item_added')
            item_consumed = player_result.get('consumed')
            item_dropped = player_result.get('item_dropped')
            equip = player_result.get('equip')
            charge_used = player_result.get('charge_used') 
            targeting = player_result.get('targeting')
            directional_targeting = player_result.get('directional_targeting')
            targeting_cancelled = player_result.get('targeting_cancelled')
            xp = player_result.get('xp')

            if player_message:
                display.write(player_message)

            if dead_entity_PT:
                if dead_entity_PT == player:
                    player_message, state = kill_player(dead_entity_PT)
                else:
                    player_message = kill_monster(dead_entity_PT, game_map)

                display.write(player_message)

            if item_added:
                entities.remove(item_added)
                state = GameStates.ENEMY_TURN

            if item_consumed:
                state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                state = GameStates.ENEMY_TURN

            if charge_used:
                state = GameStates.ENEMY_TURN

            if targeting_cancelled:
                state = GameStates.PLAYER_TURN
                display.write(Message('Targeting cancelled'))

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    removed = equip_result.get('removed')

                    if equipped:
                        display.write(Message('You equip the {0}'.format(equipped.name)))
                    if removed:
                        display.write(Message('You remove the {0}'.format(removed.name)))

                state = GameStates.ENEMY_TURN

            if xp:
                leveled_up = player.level.add_xp(xp)
                if leveled_up:
                    display.write(Message('Welcome to level {0}!'.format(player.level.current_level), Colors.LIGHT_RED))
                    prev_state = state
                    state = GameStates.LEVEL_UP

            #canceling from targeting will return to PLAYER mode, not INVENTORY
            if targeting:
                prev_state = GameStates.PLAYER_TURN
                state = GameStates.TARGETING
                targeting_item = targeting
                display.write(targeting_item.item.targeting_msg)

            if directional_targeting:
                prev_state = GameStates.PLAYER_TURN
                state = GameStates.DIRECTIONAL_TARGETING
                targeting_item = directional_targeting
                display.write(targeting_item.item.targeting_msg)

        sanity_check(player)

        if state == GameStates.ENEMY_TURN:
            game_map.enemy_FOV()
            for entity in entities:
                if entity.regeneration:
                    entity.regeneration.regen()
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, game_map)

                    for enemy_result in enemy_turn_results:
                        enemy_message = enemy_result.get('message')
                        dead_entity_ET = enemy_result.get('dead')

                        if enemy_message:
                            display.write(enemy_message)
                        if dead_entity_ET:
                            if dead_entity_ET == player:
                                enemy_message, state = kill_player(dead_entity_ET)
                            else:
                                enemy_message = kill_monster(dead_entity_ET, game_map)

                            display.write(enemy_message)

                            if state == GameStates.PLAYER_DEAD:
                                break

                    if state == GameStates.PLAYER_DEAD:
                            break
            else:                
                state = GameStates.PLAYER_TURN


def initialize(display, player_name):
    player = initialize_player(player_name)
    entities = [player]
    game_map = GameMap(player, entities)
    display.gmap = game_map
    state = GameStates.PLAYER_TURN

    return player, entities, game_map, state

#make sure player's HP doesn't exceed maximum
#can occur when removing (or having stolen) gear which increases max HP
def sanity_check(player):
    if player.fighter.hp > player.fighter.max_hp:
        player.fighter.hp = player.fighter.max_hp


if __name__ == '__main__':
    main()