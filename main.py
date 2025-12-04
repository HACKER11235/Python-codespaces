import pygame as pg
import sys
from settings import *
from map import *
from player import *
from object_renderer import *
from raycasting import *
from floor import *
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'

class Game:
    def __init__(self): 
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()
        
    def new_game(self): 
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = Raycasting(self)
        self.floor = Floor(self)
        
    def update(self):
        self.player.update()
        self.raycasting.update()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
        
    def draw(self):
        self.screen.fill('black')
        self.floor.draw()
        self.object_renderer.draw_background() # Draw the sky only
        self.object_renderer.render_game_objects() # Draw the walls/sprites
        self.object_renderer.draw_player_health()
        
        
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
                
    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
            pg.display.flip()
if __name__ == '__main__':
    game = Game()
    game.run()