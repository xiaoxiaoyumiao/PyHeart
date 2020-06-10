import json
import sys, os
from utils import map_parser
from scene import SceneLevel, get_center

def get_global_config():
    config = {}
    config["GRAVITY"]   = (0.0, 900.0)
    config["DAMPING"]   = 0.8 
    config["FRICTION"]  = 1.0
    config["FPS"]       = 50.0
    config["CHARA_MASS"] = 100
    config["CHARA_MOVEMENT"] = 1000
    return config

def chara_data():
    chara_body_path = os.path.join("pic","CHARA_BODY.png")
    poly = map_parser.parse_image_to_polygons(chara_body_path)
    return get_center(poly[0])

def level_loader(chara_offset=(0,0)):
    level_name = "level1"
    level_path = os.path.join(SceneLevel.LEVEL_ROOT, level_name)
    assert os.path.isdir(level_path)
    
    map_body_path = os.path.join(level_path, SceneLevel.MAP_BODY_RAW_FILE)
    map_dump_path = os.path.join(level_path, SceneLevel.MAP_BODY_FILE)
    map_parser.parse_image_to_polygons(map_body_path, map_dump_path)

    local_config = get_global_config()

    chara_body_path = os.path.join(level_path, SceneLevel.CHARA_BODY_FILE)
    chara_poly = map_parser.parse_image_to_polygons(chara_body_path)
    chara_poly = chara_poly[0]
    local_config["CHARA_BODY"] = chara_poly
    local_config["CHARA_OFFSET"] = chara_offset

    config_path = os.path.join(level_path, SceneLevel.CONFIG_FILE)
    config_file_handler = open(config_path, "w")
    json.dump(local_config, config_file_handler)
    config_file_handler.close()

if __name__=="__main__":
    chara_pos = chara_data()
    print(chara_pos)
    level_loader(chara_offset=chara_pos)