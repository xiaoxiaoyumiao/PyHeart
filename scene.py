import pygame
from pygame.locals import *
from sys import exit
import os, math
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
import json

def pressing(INDEX):
    return pygame.key.get_pressed()[INDEX]

def get_center(vertices):
    sum_x = 0
    sum_y = 0
    for ele in vertices:
        sum_x += ele[0]
        sum_y += ele[1]
    return (sum_x / len(vertices), sum_y / len(vertices))

class SceneBase:
    id = -1
    parent = None
    def __init__(self, _id, _parent=None):
        id = _id
        parent = _parent
    
    def start(self):
        """Called to load initial contents onscreen."""
        pass
    
    def fixed_update(self):
        """Called to update physics related states."""
        pass

    def update(self, screen):
        """Called to update rendering states."""
        pass

    def deactivate(self):
        """Hide everything onscreen in the next update."""
        pass
    
    def activate(self):
        """Recover everything onscreen in the next update."""
        pass

    def destroy(self):
        """Called to clean all contents."""
        pass

    def event_handler(self, event):
        """Called to handle events from pygame.event.get()."""
        pass

    def load_scene(self, scenes):
        return self


class SceneLevel(SceneBase):
    GRAVITY = (0.0, 900.0)
    DAMPING = 0.8 
    FPS     = 50.0
    HEIGHT  = 768
    WIDTH   = 1024
    CONFIG_FILE = "CONFIG.json"
    MAP_BODY_RAW_FILE = "MAP_BODY.png"
    MAP_BODY_FILE = "MAP.json"
    MAP_IMG_FILE  = "MAP.png"
    CHARA_BODY_FILE = "CHARA_BODY.png"
    LEVEL_ROOT = "levels"
    
    # game object data, object generated at runtime
    object_data = []
    object_list = []
    def __init__(self, _id, _parent, _name):
        super(SceneLevel, self).__init__(_id, _parent)
        self.name = _name
        level_data_path = os.path.join(SceneLevel.LEVEL_ROOT, self.name)
        config_path = os.path.join(level_data_path, SceneLevel.CONFIG_FILE)
        config_file_handler = open(config_path, "r")
        config = json.load(config_file_handler)
        config_file_handler.close()
        self.fps = config["FPS"]

        # pymunk space
        self.space = pymunk.Space()
        self.space.gravity = config["GRAVITY"]
        self.space.damping = config["DAMPING"]

        # static data (layout of terrain, etc.)
        map_path = os.path.join(level_data_path, SceneLevel.MAP_BODY_FILE)
        map_file_handler = open(map_path, "r")
        self.map_data = json.load(map_file_handler)
        map_file_handler.close()
        map_img_path = os.path.join(level_data_path, SceneLevel.MAP_IMG_FILE)
        self.map_img = pygame.image.load(map_img_path)
        body = None
        for rev_shape in self.map_data:
            if len(rev_shape)<=2:
                continue
            print(rev_shape)
            pos = get_center(rev_shape)
            shape = [(x[1]-pos[1],x[0]-pos[0]) for x in rev_shape]
            pos = tuple(reversed(pos))
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            shape = pymunk.Poly(body, shape, radius=1)
            shape.friction = config["FRICTION"] / 2
            self.space.add(body, shape)

        chara_img_path = os.path.join("pic","CHARA.png")
        self.chara_img = pygame.image.load(chara_img_path)
        chara_shape = config["CHARA_BODY"]
        chara_shape_loc = get_center(chara_shape)
        chara_shape = [(x[1]-chara_shape_loc[1],x[0]-chara_shape_loc[0]) for x in chara_shape]
        chara_shape_loc = tuple(reversed(chara_shape_loc))
        self.chara_body = pymunk.Body(config["CHARA_MASS"],config["CHARA_MOVEMENT"])
        self.chara_body.position = chara_shape_loc
        chara_shape = pymunk.Poly(self.chara_body, chara_shape, radius=1)
        chara_shape.friction = config["FRICTION"] / 2
        self.space.add(chara_shape, self.chara_body)
        self.chara_offset = tuple(reversed(config["CHARA_OFFSET"]))
        self.chara_ori_right = 1

        def limit_velocity(body, gravity, damping, dt):
            max_velocity = 200
            pymunk.Body.update_velocity(body, gravity, damping, dt)
            l = body.velocity.length
            if l > max_velocity:
                body.velocity = body.velocity * (max_velocity / l)
            
        self.chara_body.velocity_func = limit_velocity

        c = pymunk.RotaryLimitJoint(body, self.chara_body,0,0)
        self.space.add(c)
        self.pressing_key = None

    def fixed_update(self):
        x = self.chara_body.position.x
        y = self.chara_body.position.y
        if self.pressing_key == K_w:
            if abs(self.chara_body.velocity.y) < 1:
                self.chara_body.apply_impulse_at_world_point((0,-40000),(x,SceneLevel.HEIGHT))
            self.pressing_key = None
        elif self.pressing_key == K_a:
            self.chara_ori_right = 0
            if pressing(K_a):
                self.chara_body.apply_force_at_world_point((-40000,0),(0, y))
        elif self.pressing_key == K_d:
            self.chara_ori_right = 1
            if pressing(K_d):
                self.chara_body.apply_force_at_world_point((40000,0),(SceneLevel.WIDTH, y))
        self.space.step(1/self.fps)
        return super().fixed_update()

    def event_handler(self, event):
        if event.type == KEYDOWN:
            self.pressing_key = event.key
        return super().event_handler(event)

    def update(self, screen):
        screen.blit(self.map_img, (0,0))
        chara_loc = self.chara_body.position
        chara_loc = (chara_loc[0]-self.chara_offset[0], 
                     chara_loc[1]-self.chara_offset[1])
        chara = self.chara_img
        if self.chara_ori_right == 0:
            chara = pygame.transform.flip(chara, True, False)
        screen.blit(chara, chara_loc)
        return super().update(screen)