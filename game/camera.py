from wecs.core import Entity, Component, System
from wecs.core import and_filter

from panda3d import core

from .terrain import TerrainObject

import math


@Component()
class Camera:
    target: Entity
    distance: float = 5.0
    elevation: float = 2.5
    fov: float = 90


class CameraSystem(System):
    entity_filters = {
        'camera': and_filter([Camera]),
    }

    def __init__(self):
        System.__init__(self)

    def init_entity(self, filter_name, entity):
        camera = entity[Camera]
        target_obj = camera.target[TerrainObject]

        cam_node = core.Camera(entity._uid.name)
        cam_node.get_lens().set_fov(camera.fov)
        camera._root = target_obj._root.attach_new_node(cam_node)
        camera._root.set_pos(0, -camera.distance, camera.elevation)
        camera._root.look_at(0, 0, 0)

    def button_pressed(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 1.0

    def button_released(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 0.0

    def update(self, entities_by_filter):
        for entity in entities_by_filter['camera']:
            camera = entity[Camera]
