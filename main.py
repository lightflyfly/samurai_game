# This is a text game.
# A json file is used as a map.
# Recursion is used to navigate between locations.

import json
import re
import pygame
import sys
from button import Button


def get_font(size):
    return pygame.font.Font("fonts/Advantage.ttf", size)


def game(game_map: dict):
    global hp, gold

    while True:
        game_mouse_pos = pygame.mouse.get_pos()

        screen.blit(bg, (0, 0))

        you_see_text = get_font(30).render('YOU SEE:', True, "Black")
        you_see_rect = you_see_text.get_rect(center=(600, 370))
        screen.blit(you_see_text, you_see_rect)

        # The name of the location the player is in
        for key, subtree in game_map.items():
            my_loc = key

        # Robbers

        for r in subtree:
            if r == 'Robbers min 80 gold':
                gold -= 80
                subtree.remove('Robbers min 80 gold')
                subtree.append('Here were robbers')

        for r in subtree:
            if r == 'Here were robbers':
                robbers_text = get_font(30).render(f'Here were robbers min 80 gold', True, "Red")
                robbers_rect = robbers_text.get_rect(center=(600, 630))
                screen.blit(robbers_text, robbers_rect)

        # Log

        message_1 = f'You are at the {my_loc}'
        if gold < 0:
            message_2 = f'You have {hp} hp and min{gold} gold'
        else:
            message_2 = f'You have {hp} hp and {gold} gold'
        message_3 = f'You have to find exit'
        message_4 = f'What are you going to do?'

        messages = [message_1, message_2, message_3, message_4]
        y_mes = 140

        for mes in messages:
            log_text = get_font(30).render(mes, True, "#d7fcd4")
            log_rect = log_text.get_rect(center=(600, y_mes))
            screen.blit(log_text, log_rect)
            y_mes += 50

        # Monster buttons

        monster_buttons = {}
        y_button = 450

        for x in subtree:
            if isinstance(x, str):
                if x != 'Exit from the forest' and x != 'Robbers min 80 gold' and x != 'Here were robbers' \
                        and x != 'Robbers are gone':
                    monster_buttons[Button(image=None, pos=(450, y_button),
                                           text_input=f"{x}", font=get_font(20), base_color="#d7fcd4",
                                           hovering_color="White", sound=punch_sound)] = x
                    y_button += 40

        for button in monster_buttons:
            button.changeColor(game_mouse_pos)
            button.update(screen)

        if monster_buttons != {}:
            kill_text = get_font(20).render("Press to kill", True, "Black")
            kill_rect = kill_text.get_rect(center=(450, y_button))
            screen.blit(kill_text, kill_rect)

            note_text = get_font(20).render("hp is also gold", True, "Black")
            note_rect = note_text.get_rect(center=(450, y_button + 30))
            screen.blit(note_text, note_rect)

        # Location buttons

        loc_buttons = {}
        y_button = 450

        for y in subtree:
            if isinstance(y, dict):
                for y_key in y:
                    y_key = y_key
                loc_buttons[Button(image=None, pos=(750, y_button),
                                   text_input=f"{y_key}", font=get_font(20), base_color="#d7fcd4",
                                   hovering_color="White", sound=button_sound)] = y_key
                y_button += 40

        for button in loc_buttons:
            button.changeColor(game_mouse_pos)
            button.update(screen)

        # Return to previous location button
        if my_loc != 'Entrance to the forest':
            prev_loc_button = Button(image=None, pos=(750, 410),
                                     text_input=f"PREVIOUS LOC", font=get_font(20), base_color="#d7fcd4",
                                     hovering_color="White", sound=button_sound)
            prev_loc_button.changeColor(game_mouse_pos)
            prev_loc_button.update(screen)

        # Heal button
        for j in subtree:
            if isinstance(j, int):
                heal_button = Button(image=None, pos=(750, 600),
                                     text_input=f"Plus {j}hp", font=get_font(20), base_color="#b85cbf",
                                     hovering_color="White", sound=heal_sound)
                heal_button.changeColor(game_mouse_pos)
                heal_button.update(screen)
                break

        # Quit button (quit the game)
        quit_button = Button(image=None, pos=(1100, 700),
                             text_input=f"Quit", font=get_font(30), base_color="#d7fcd4",
                             hovering_color="White", sound=button_sound)
        quit_button.changeColor(game_mouse_pos)
        quit_button.update(screen)

        # Exit button (way out of the forest)
        for u in subtree:
            if u == 'Exit from the forest':
                exit_button = Button(image=None, pos=(600, 650),
                                     text_input=f"{u} 400 gold", font=get_font(20), base_color="#d7fcd4",
                                     hovering_color="White", sound=button_sound)
                exit_button.changeColor(game_mouse_pos)
                exit_button.update(screen)

                if gold < 400:
                    not_exit_text = get_font(20).render(f'Not enough gold', True, "Red")
                    not_exit_rect = not_exit_text.get_rect(center=(600, 690))
                    screen.blit(not_exit_text, not_exit_rect)

                break

        # 'Wanted' picture

        if my_loc == 'Rivulet':
            wanted = pygame.image.load('images/wanted_small.jpg')
            wanted_rect = wanted.get_rect(bottomright=(540, 700))
            screen.blit(wanted, wanted_rect)

        # Actions

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                # If button = 'monster'
                for button in monster_buttons:
                    if button.checkForInput(game_mouse_pos):
                        # Min hp
                        mob_re = re.compile(r'Akuma minus (\d+)hp')
                        boss_re = re.compile(r'Boss minus (\d+)hp')
                        # Monster or Boss
                        monster = re.search(mob_re, monster_buttons[button])
                        if monster is None:
                            monster = re.search(boss_re, monster_buttons[button])
                        hp -= int(monster[1])
                        if hp <= 0:
                            lose()
                        gold += int(monster[1])
                        # Remove monster from subtree
                        subtree.remove(monster_buttons[button])

                # If button = 'location'
                for button in loc_buttons:
                    if button.checkForInput(game_mouse_pos):

                        # Remove robbers when moving to the location (1)
                        for r in subtree:
                            if r == 'Here were robbers':
                                subtree.remove('Here were robbers')

                        for z in subtree:
                            if isinstance(z, dict):
                                for ke in z:
                                    if ke == loc_buttons[button]:
                                        game(z)

                # If button = 'return to the previous location'
                if my_loc != 'Entrance to the forest':
                    if prev_loc_button.checkForInput(game_mouse_pos):

                        # Remove robbers when moving to the location (2)
                        for r in subtree:
                            if r == 'Here were robbers':
                                subtree.remove('Here were robbers')

                        return

                # If button = 'heal'
                for q in subtree:
                    if isinstance(q, int):
                        if heal_button.checkForInput(game_mouse_pos):
                            hp += q
                            subtree.remove(q)
                            q = None

                # If button = 'quit'
                if quit_button.checkForInput(game_mouse_pos):
                    pygame.quit()
                    sys.exit()

                # If button = 'exit'
                # If pressed and condition is fulfilled
                for w in subtree:
                    if w == 'Exit from the forest':
                        if exit_button.checkForInput(game_mouse_pos):
                            if gold >= 400:
                                win()

        pygame.display.update()


def main_menu():
    while True:
        menu_mouse_pos = pygame.mouse.get_pos()

        screen.blit(bg, (0, 0))

        # Text

        head_text = get_font(50).render('SAMURAI IN THE FOREST', True, "#d7fcd4")
        head_rect = head_text.get_rect(center=(600, 300))
        screen.blit(head_text, head_rect)

        # Play button

        play_button = Button(image=None, pos=(600, 375),
                             text_input="PLAY", font=get_font(75), base_color="#d7fcd4",
                             hovering_color="White", sound=button_sound)
        play_button.changeColor(menu_mouse_pos)
        play_button.update(screen)

        # Actions

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    game(game_map=loaded_json)

        pygame.display.update()


def win():
    while True:
        screen.blit(bg, (0, 0))
        game_mouse_pos = pygame.mouse.get_pos()

        head_text = get_font(50).render('SAMURAI IN THE FOREST', True, "#d7fcd4")
        head_rect = head_text.get_rect(center=(600, 300))
        screen.blit(head_text, head_rect)

        win_text = get_font(75).render('You got out of the forest', True, "#d7fcd4")
        win_rect = head_text.get_rect(center=(350, 375))
        screen.blit(win_text, win_rect)

        quit_game_option(game_mouse_pos)


def lose():
    while True:
        screen.blit(bg, (0, 0))
        game_mouse_pos = pygame.mouse.get_pos()

        head_text = get_font(50).render('SAMURAI IN THE FOREST', True, "#d7fcd4")
        head_rect = head_text.get_rect(center=(600, 300))
        screen.blit(head_text, head_rect)

        win_text = get_font(75).render('You are dead', True, "#d7fcd4")
        win_rect = head_text.get_rect(center=(620, 375))
        screen.blit(win_text, win_rect)

        quit_game_option(game_mouse_pos)


def quit_game_option(game_mouse_pos):
    quit_button = Button(image=None, pos=(1100, 700),
                         text_input="Quit", font=get_font(30), base_color="#d7fcd4",
                         hovering_color="White", sound=button_sound)
    quit_button.changeColor(game_mouse_pos)
    quit_button.update(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button.checkForInput(game_mouse_pos):
                pygame.quit()
                sys.exit()

    pygame.display.update()


pygame.init()

screen = pygame.display.set_mode((1200, 750))
pygame.display.set_caption("Samurai in The Forest")

bg = pygame.image.load('images/bg.png')

icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

pygame.mixer.init()  # для звука
button_sound = pygame.mixer.Sound('sounds/button.mp3')
button_sound.set_volume(0.8)
punch_sound = pygame.mixer.Sound('sounds/punch.mp3')
punch_sound.set_volume(0.2)
heal_sound = pygame.mixer.Sound('sounds/heal.wav')
heal_sound.set_volume(0.4)

pygame.mixer.music.load("sounds/birds.mp3")
pygame.mixer.music.play(-1)

with open('map.json', 'r') as read_file:
    loaded_json = json.load(read_file)

hp = 300
gold = 0

main_menu()
