import pygame
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

WIDTH, HEIGHT = 1024, 768
LEVEL_WIDTH, LEVEL_HEIGHT = 2432, 1856
TILE_SIZE = 64
MAX_ENEMIES = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BULLET = (47, 97, 97)
MAGENTA = (255, 0, 255)

START_SCORE = 0
BASE_SCORE = 10
MAX_MULTIPLIER = 5

PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ARMOR = 50
ARMOR_EFFECTIVENESS = 0.5

image_files = {
    "pistol": os.path.join(PROJECT_ROOT, "images/pistol.png"),
    "machine_gun": os.path.join(PROJECT_ROOT, "images/machinegun.png"),
    "armor": os.path.join(PROJECT_ROOT, "images/armor.png"),
    "health": os.path.join(PROJECT_ROOT, "images/health.png")
}