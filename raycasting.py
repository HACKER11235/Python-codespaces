import pygame as pg
import math
from settings import *
import os

# Keep this as requested
os.environ['SDL_AUDIODRIVER'] = 'dsp'

class Raycasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = self.game.object_renderer.wall_textures
        
    def get_objects_to_render(self):
        self.objects_to_render = []
        
        # Localize lookups for speed
        textures = self.textures
        scale_func = pg.transform.scale
        
        # Pre-calculate constants to avoid math in loop
        texture_size_minus_scale = TEXTURE_SIZE - SCALE
        half_texture_size = HALF_TEXTURE_SIZE
        
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values
            
            # Optimization: Skip rendering if depth is too massive (optional, but safe)
            if proj_height < HEIGHT:
                wall_column = textures[texture].subsurface(
                    offset * texture_size_minus_scale, 0, SCALE, TEXTURE_SIZE
                )
                wall_column = scale_func(wall_column, (SCALE, int(proj_height)))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                
                # Prevent crashing if texture_height is huge by clamping or handling subsurface errors implicitly
                # The logic here remains as provided but using local vars
                wall_column = textures[texture].subsurface(
                    offset * texture_size_minus_scale, 
                    half_texture_size - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = scale_func(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self):
        self.ray_casting_result = []
        
        # Localize global/class attributes to speed up the loop
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos
        world_map = self.game.map.world_map
        player_angle = self.game.player.angle
        
        # Localize math functions
        sin = math.sin
        cos = math.cos
        
        texture_vert, texture_hor = 1, 1
        
        ray_angle = player_angle - HALF_FOV + 0.0001
        
        for ray in range(NUM_RAYS):
            sin_a = sin(ray_angle)
            cos_a = cos(ray_angle)
            
            # --- Horizontals ---
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)  
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a
            
            delta_depth = dy / sin_a
            dx = delta_depth * cos_a
            
            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in world_map:
                    texture_hor = world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # --- Verticals ---
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
            
            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a
            
            delta_depth = dx / cos_a
            dy = delta_depth * sin_a
            
            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in world_map:
                    texture_vert = world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth
                
            # Depth and Texture offset calculation
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor
                
            # Remove fishbowl effect
            # Use local cos and the pre-calculated difference
            depth *= cos(player_angle - ray_angle)
            
            # Projection
            proj_height = SCREEN_DIST / (depth + 0.0001)
            
            # Raycasting result
            self.ray_casting_result.append((depth, proj_height, texture, offset))
            
            ray_angle += DELTA_ANGLE
    
    def update(self):
        self.ray_cast()
        self.get_objects_to_render()
