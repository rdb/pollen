from wecs.core import Entity, Component, System
from wecs.core import and_filter

from panda3d import core

from .terrain import TerrainObject
from .general import Speed

import math


def smoothstep(x):
    return x * x * x * (x * (x * 6 - 15) + 10)


@Component()
class Camera:
    target: Entity
    distance: float = 7.0
    elevation: float = 5
    fov: float = 100
    fast_fov: float = 110


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
        camera._lens = cam_node.get_lens()
        camera._lens.set_fov(camera.fov)
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

            fov = camera.fov

            if Speed in camera.target:
                speed = camera.target[Speed]
                if speed.max is not None:
                    t = (speed.current - speed.min) / (speed.max - speed.min)
                    t = smoothstep(t)
                    fov = t * camera.fast_fov + (1 - t) * fov

            camera._lens.set_fov(fov)