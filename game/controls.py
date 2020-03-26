from wecs.core import Component, System
from wecs.core import and_filter

from direct.showbase.DirectObject import DirectObject
from panda3d import core

from .terrain import TerrainObject
from .general import Speed
from .animation import Character
from .audio import Music

import math


@Component()
class Controls:
    forward: str = 'mouse1'

    acceleration: float = 3.0
    deceleration: float = 2.0

    # degrees per second
    turn_speed: float = 150

    enabled: bool = True


class PlayerController(System, DirectObject):
    entity_filters = {
        'player': and_filter([Controls, TerrainObject, Speed]),
    }

    def __init__(self):
        System.__init__(self)

        self.last_ptr = None

        base.win.request_properties(core.WindowProperties(mouse_mode=core.WindowProperties.M_confined))

    def init_entity(self, filter_name, entity):
        controls = entity[Controls]
        controls._states = {}

        for control in ('forward',):
            controls._states[control] = 0.0
            self.accept(getattr(controls, control), self._button_pressed, [entity, control])
            self.accept(getattr(controls, control) + '-up', self._button_released, [entity, control])

    def destroy_entity(self, filter_name, entity):
        controls = entity[Controls]
        del controls._states

    def _button_pressed(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 1.0

        if action == 'forward':
            base.music[Music].play('chase')

    def _button_released(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 0.0

        if action == 'forward':
            base.music[Music].play('peace')

    def update(self, entities_by_filter):
        for entity in entities_by_filter['player']:
            obj = entity[TerrainObject]
            controls = entity[Controls]
            speed = entity[Speed]

            dt = globalClock.dt

            ptr = base.win.get_pointer(0)
            if ptr.in_window:
                if self.last_ptr:
                    lean = ptr.x - base.win.get_x_size() / 2
                    lean_norm = lean / base.win.get_x_size()
                    obj.direction -= lean_norm * controls.turn_speed * dt
                    base.cam.set_x(lean_norm * 3)

                    elevate = (ptr.y / base.win.get_y_size()) - 0.5
                    base.cam.set_z(0 - elevate)
                else:
                    base.win.move_pointer(0, base.win.get_x_size() // 2, base.win.get_y_size() // 2)

                self.last_ptr = ptr
            else:
                self.last_ptr = None

            if controls.enabled and controls._states['forward']:
                speed.accelerate(controls._states['forward'] * controls.acceleration)
            else:
                speed.accelerate(-controls.deceleration)

            dir_rad = math.radians(obj.direction)
            obj.position = (
                obj.position[0] - math.sin(dir_rad) * speed.current * dt,
                obj.position[1] + math.cos(dir_rad) * speed.current * dt,
                obj.position[2],
            )
