from wecs.core import Component, System
from wecs.core import and_filter

from direct.showbase.DirectObject import DirectObject
from panda3d import core

from .terrain import TerrainObject
from .general import Speed

import math


@Component()
class Controls:
    forward: str = 'raw-w'
    left: str = 'raw-a'
    right: str = 'raw-d'

    direction: float = 0.0
    acceleration: float = 3.0
    deceleration: float = 3.0


class PlayerController(System, DirectObject):
    entity_filters = {
        'player': and_filter([Controls, TerrainObject, Speed]),
    }

    def __init__(self):
        System.__init__(self)

    def init_entity(self, filter_name, entity):
        controls = entity[Controls]
        controls._states = {'forward': 0.0}

        self.accept(controls.forward, self.button_pressed, [entity, 'forward'])
        self.accept(controls.forward + '-up', self.button_released, [entity, 'forward'])

    def button_pressed(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 1.0

    def button_released(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 0.0

    def update(self, entities_by_filter):
        for entity in entities_by_filter['player']:
            obj = entity[TerrainObject]
            controls = entity[Controls]
            speed = entity[Speed]

            if controls._states['forward']:
                speed.accelerate(controls._states['forward'] * controls.acceleration)
            else:
                speed.accelerate(-controls.deceleration)

            dir_rad = math.radians(controls.direction)
            dt = globalClock.dt
            obj.position = (
                obj.position[0] + math.sin(dir_rad) * speed.current * dt,
                obj.position[1] + math.cos(dir_rad) * speed.current * dt,
                obj.position[2],
            )
