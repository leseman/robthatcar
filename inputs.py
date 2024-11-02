import pygame
import io

DEFAULT_CONTROLS = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "switch_weapon": pygame.K_q,
    "weapon_wheel": pygame.K_TAB,
    "shoot": 1
}

def get_control_name(control):
    if 1 <= control <= 5:
        button_names = {
            1: "Left Click",
            2: "Middle Click",
            3: "Right Click",
            4: "Mouse Wheel Up",
            5: "Mouse Wheel Down"
        }
        return button_names.get(control, f"Mouse Button {control}")
    else:
        return pygame.key.name(control).upper()

def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

def load_high_score():
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0