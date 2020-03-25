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
    backward: str = 'raw-s'
    right: str = 'raw-d'

    acceleration: float = 3.0
    deceleration: float = 2.0

    # degrees per second
    turn_speed: float = 45.0

    enabled: bool = True


class PlayerController(System, DirectObject):
    entity_filters = {
        'player': and_filter([Controls, TerrainObject, Speed]),
    }

    def __init__(self):
        System.__init__(self)

    def init_entity(self, filter_name, entity):
        controls = entity[Controls]
        controls._states = {}

        for control in ('forward', 'backward', 'left', 'right'):
            controls._states[control] = 0.0
            self.accept(getattr(controls, control), self._button_pressed, [entity, control])
            self.accept(getattr(controls, control) + '-up', self._button_released, [entity, control])

    def destroy_entity(self, filter_name, entity):
        controls = entity[Controls]
        del controls._states

    def _button_pressed(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 1.0

    def _button_released(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 0.0

    def update(self, entities_by_filter):
        for entity in entities_by_filter['player']:
            obj = entity[TerrainObject]
            controls = entity[Controls]
            speed = entity[Speed]

            if controls.enabled:
                if controls._states['forward'] or controls._states['backward']:
                    speed.accelerate((controls._states['forward'] - controls._states['backward']) * controls.acceleration)
                else:
                    speed.accelerate(-controls.deceleration)

            dt = globalClock.dt
            turn = controls._states['right'] - controls._states['left']
            obj.direction -= turn * controls.turn_speed * dt

            dir_rad = math.radians(obj.direction)
            obj.position = (
                obj.position[0] - math.sin(dir_rad) * speed.current * dt,
                obj.position[1] + math.cos(dir_rad) * speed.current * dt,
                obj.position[2],
            )
