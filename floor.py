import pygame as pg
import math
from settings import *

class Floor:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        # Create the surface once in init
        self.floor_surface = pg.Surface((WIDTH, HALF_HEIGHT))
        
        # OPTIMIZATION: Pre-calculate the row distances (Look Up Table)
        # This prevents doing division math for every row, every frame.
        self.row_distances = []
        for y in range(1, HALF_HEIGHT):
            self.row_distances.append((0.5 * HEIGHT) / y)

    def draw(self):
        # 1. Localize lookups for speed
        player = self.game.player
        px, py = player.x, player.y
        player_angle = player.angle
        
        # Cache math functions
        sin_a = math.sin(player_angle)
        cos_a = math.cos(player_angle)

        # 2. Calculate Ray Directions
        # 0.66 is the standard FOV factor
        plane_x = -sin_a * 0.66
        plane_y = cos_a * 0.66

        ray_dir_x0 = cos_a - plane_x
        ray_dir_y0 = sin_a - plane_y
        ray_dir_x1 = cos_a + plane_x
        ray_dir_y1 = sin_a + plane_y

        # 3. Prepare Texture Access
        # PixelArray locks the surface for direct memory access (Much faster than get_at/set_at)
        floor_tex = self.game.object_renderer.floor_texture
        tex_w = floor_tex.get_width()
        tex_h = floor_tex.get_height()
        
        # Create PixelArrays
        # We wrap this in a try/finally or ensure we delete them to unlock the surface
        floor_arr = pg.PixelArray(self.floor_surface)
        tex_arr = pg.PixelArray(floor_tex)

        # Local constants for the loop
        width = WIDTH
        
        # 4. Render Loop
        # We iterate through our pre-calculated row distances
        for i, row_dist in enumerate(self.row_distances):
            y = i + 1  # Matches range(1, HALF_HEIGHT)
            
            # Optimization: Pre-calculate the step size for this row
            step_factor = row_dist / width
            floor_step_x = step_factor * (ray_dir_x1 - ray_dir_x0)
            floor_step_y = step_factor * (ray_dir_y1 - ray_dir_y0)

            # Starting world coordinates
            floor_x = px + row_dist * ray_dir_x0
            floor_y = py + row_dist * ray_dir_y0

            # Inner Loop: Iterate across the screen width
            for x in range(width):
                # Convert world coordinates to texture coordinates
                # using int() is slightly faster here, and % handles the tiling
                cell_x = int(floor_x * tex_w) % tex_w
                cell_y = int(floor_y * tex_h) % tex_h

                floor_x += floor_step_x
                floor_y += floor_step_y
                
                # Direct pixel assignment
                floor_arr[x, y] = tex_arr[cell_x, cell_y]

        # 5. Clean up
        # You MUST delete PixelArrays to unlock the surfaces before blitting
        del floor_arr
        del tex_arr

        # 6. Blit result
        self.game.screen.blit(self.floor_surface, (0, HALF_HEIGHT))
