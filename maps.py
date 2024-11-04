import pygame
import random
import config

TILE_TYPES = {
    'GRASS': (154,205,50),  # Yellow green
    'FOREST': (34, 139, 34),  # Forest green
    'STREET': (128, 128, 144),  # Slate gray
    'PAVEMENT': (160, 82, 45),  # Sienna
    'WATER': (0, 0, 128)  # Navy
}

class WaveFunctionCollapse:
    def __init__(self, tile_types, rules):
        self.tile_types = tile_types
        self.rules = rules
        self.grid = None
        self.wave = None

    def initialize(self, width, height):
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.wave = [[set(self.tile_types) for _ in range(width)] for _ in range(height)]

    def collapse(self, x, y, tile_type):
        self.grid[y][x] = tile_type
        self.wave[y][x] = {tile_type}
        self.propagate(x, y)

    def propagate(self, x, y):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid):
                    updated = self.constrain(nx, ny, cx, cy)
                    if updated:
                        stack.append((nx, ny))

    def constrain(self, x, y, prev_x, prev_y):
        if self.grid[y][x] is not None:
            return False
        
        prev_tile = self.grid[prev_y][prev_x]
        if prev_tile is None:
            return False
        
        direction = (x - prev_x, y - prev_y)
        allowed = set(self.rules[prev_tile][direction])
        
        new_options = self.wave[y][x].intersection(allowed)
        if not new_options:
            # If we've constrained ourselves into an impossible situation, 
            # reset this cell to allow all possibilities
            new_options = set(self.tile_types)
        
        if new_options != self.wave[y][x]:
            self.wave[y][x] = new_options
            return True
        return False

    def get_min_entropy_cell(self):
        min_entropy = float('inf')
        candidates = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if self.grid[y][x] is None:
                    entropy = len(self.wave[y][x])
                    if entropy < min_entropy and entropy > 0:
                        min_entropy = entropy
                        candidates = [(x, y)]
                    elif entropy == min_entropy:
                        candidates.append((x, y))
        return random.choice(candidates) if candidates else None

    def generate(self, width, height):
        self.initialize(width, height)
        while True:
            cell = self.get_min_entropy_cell()
            if cell is None:
                break
            x, y = cell
            if not self.wave[y][x]:
                # If we've constrained a cell to have no possibilities, 
                # reset it to allow all possibilities
                self.wave[y][x] = set(self.tile_types)
            tile_type = random.choice(list(self.wave[y][x]))
            self.collapse(x, y, tile_type)
        return self.grid
    
class Tile:
    def __init__(self, tile_type):
        self.type = tile_type
        self.color = TILE_TYPES[tile_type]

class TileMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[Tile('GRASS') for _ in range(width)] for _ in range(height)]
    
    def get_tile(self, x, y):
        return self.tiles[y][x]
    
    def set_tile(self, x, y, tile_type):
        self.tiles[y][x] = Tile(tile_type)
    
    def generate_wfc_map(self):
        tile_types = list(TILE_TYPES.keys())
        # The adjacent tiles are placed as follows:
        # (-1, 0): The tile to the left
        # (1, 0): The tile to the right
        # (0, -1): The tile above
        # (0, 1): The tile below
        rules = {
            'GRASS': {
                (-1, 0): ['GRASS', 'FOREST', 'WATER', 'PAVEMENT'],
                (1, 0): ['GRASS', 'FOREST', 'WATER', 'PAVEMENT'],
                (0, -1): ['GRASS', 'FOREST', 'WATER', 'PAVEMENT'],
                (0, 1): ['GRASS', 'FOREST', 'WATER', 'PAVEMENT'],
            },
            'FOREST': {
                (-1, 0): ['FOREST', 'GRASS'],
                (1, 0): ['FOREST', 'GRASS'],
                (0, -1): ['FOREST', 'GRASS'],
                (0, 1): ['FOREST', 'GRASS'],
            },
            'STREET': {
                (-1, 0): ['STREET', 'PAVEMENT'],
                (1, 0): ['STREET', 'PAVEMENT'],
                (0, -1): ['STREET', 'PAVEMENT'],
                (0, 1): ['STREET', 'PAVEMENT'],
            },
            'PAVEMENT': {
                (-1, 0): ['GRASS', 'STREET', 'PAVEMENT'],
                (1, 0): ['GRASS', 'STREET', 'PAVEMENT'],
                (0, -1): ['GRASS', 'STREET', 'PAVEMENT'],
                (0, 1): ['GRASS', 'STREET', 'PAVEMENT'],
            },
            'WATER': {
                (-1, 0): ['WATER', 'GRASS'],
                (1, 0): ['WATER', 'GRASS'],
                (0, -1): ['WATER', 'GRASS'],
                (0, 1): ['WATER', 'GRASS'],
            },
        }
        
        wfc = WaveFunctionCollapse(tile_types, rules)
        generated_map = wfc.generate(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, generated_map[y][x])

def render_tilemap(screen, tilemap, camera_pos):
    start_x = int(camera_pos[0]) // config.TILE_SIZE
    start_y = int(camera_pos[1]) // config.TILE_SIZE
    end_x = start_x + (screen.get_width() // config.TILE_SIZE) + 2
    end_y = start_y + (screen.get_height() // config.TILE_SIZE) + 2

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if 0 <= x < tilemap.width and 0 <= y < tilemap.height:
                tile = tilemap.get_tile(x, y)
                screen_x = x * config.TILE_SIZE - int(camera_pos[0])
                screen_y = y * config.TILE_SIZE - int(camera_pos[1])
                pygame.draw.rect(screen, tile.color, (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE))

class Minimap:
    def __init__(self, screen_width, screen_height, level_width, level_height):
        # Minimap dimensions (e.g. 20% of screen size)
        self.width = int(screen_width * 0.2)
        self.height = int(screen_height * 0.2)
        
        # Position minimap in top-right corner with some padding
        self.x = screen_width - self.width - 10
        self.y = 10
        
        # Scale factors to convert game coordinates to minimap coordinates
        self.scale_x = self.width / level_width
        self.scale_y = self.height / level_height
        
        # Create surface for minimap
        self.surface = pygame.Surface((self.width, self.height))
        
        # Store level dimensions
        self.level_width = level_width
        self.level_height = level_height
        
        # Colors
        self.BACKGROUND = (40, 40, 40, 180)  # Dark gray, semi-transparent
        self.BORDER = (200, 200, 200)  # Light gray
        self.PLAYER = (0, 255, 0)  # Green
        self.NPC = (255, 0, 0)  # Red
        self.VIEWPORT = (255, 255, 255)  # White

    def world_to_minimap(self, x, y):
        """Convert world coordinates to minimap coordinates"""
        return (
            int(x * self.scale_x),
            int(y * self.scale_y)
        )

    def draw_viewport(self, screen, camera_pos, viewport_width, viewport_height):
        """Draw the current viewport area on the minimap"""
        start_x, start_y = self.world_to_minimap(camera_pos[0], camera_pos[1])
        width = int(viewport_width * self.scale_x)
        height = int(viewport_height * self.scale_y)
        
        # Draw viewport rectangle
        pygame.draw.rect(self.surface, self.VIEWPORT, 
                        (start_x, start_y, width, height), 1)

    def update(self, game_state):
        # Clear the surface
        self.surface.fill(self.BACKGROUND)
        
        # Draw border
        pygame.draw.rect(self.surface, self.BORDER, 
                        (0, 0, self.width, self.height), 1)
        
        # Draw player
        player_x, player_y = self.world_to_minimap(
            game_state.player_pos[0],
            game_state.player_pos[1]
        )
        pygame.draw.circle(self.surface, self.PLAYER, 
                         (player_x, player_y), 2)
        
        # Draw NPCs
        for npc in game_state.npcs:
            npc_x, npc_y = self.world_to_minimap(
                npc.pos.x,
                npc.pos.y
            )
            pygame.draw.circle(self.surface, self.NPC, 
                             (npc_x, npc_y), 2)
        
        # Draw current viewport
        self.draw_viewport(self.surface, game_state.camera_pos, 
                          game_state.width, game_state.height)

    def draw(self, screen):
        # Draw the minimap surface onto the main screen
        screen.blit(self.surface, (self.x, self.y))