from wecs.core import Component, System
from wecs.core import and_filter

from direct.showbase.DirectObject import DirectObject
from panda3d import core

from .terrain import TerrainObject

import math


@Component()
class Controls:
    forward: str = 'raw-w'
    left: str = 'raw-a'
    right: str = 'raw-d'

    direction: float = 0.0
    speed: float = 0.0
    acceleration: float = 4.0
    deceleration: float = 4.0
    min_speed: float = 1.0
    max_speed: float = 5.0


class PlayerController(System, DirectObject):
    entity_filters = {
        'player': and_filter([Controls, TerrainObject]),
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

            dt = globalClock.dt
            if controls._states['forward']:
                controls.speed += controls._states['forward'] * controls.acceleration * dt
            else:
                controls.speed -= controls.deceleration * dt

            if controls.speed > controls.max_speed:
                controls.speed = controls.max_speed
            elif controls.speed < controls.min_speed:
                controls.speed = controls.min_speed

            dir_rad = math.radians(controls.direction)

            obj.position = (
                obj.position[0] + math.sin(dir_rad) * controls.speed * dt,
                obj.position[1] + math.cos(dir_rad) * controls.speed * dt,
                obj.position[2],
            )
