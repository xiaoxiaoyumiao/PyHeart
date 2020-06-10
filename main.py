import pygame
from pygame.locals import *
from sys import exit

import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

from scene import SceneBase, SceneLevel

WHITE = (255,255,255)
BGCOLOR = (100,170,208)
FPS = 50.0
HEIGHT = 768
WIDTH = 1024

def main():
    pygame.init()
    screen = pygame.display.set_mode((SceneLevel.WIDTH, SceneLevel.HEIGHT), 0, 32)
    pygame.display.set_caption("Heart Game")
    clock = pygame.time.Clock()
    
    pymunk.pygame_util.positive_y_is_up = False
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    scenes = []
    current_scene = SceneLevel(0, None, "level1")
    scenes.append(current_scene)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            current_scene.event_handler(event)

        # physical update
        current_scene.fixed_update()
        
        # screen update
        current_scene.update(screen)
        pygame.display.update()

        # current_scene = current_scene.load_scene(scenes)
        
        clock.tick(FPS)

if __name__=='__main__':
    main()