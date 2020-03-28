from wecs.core import Component, System
from wecs.core import and_filter

from direct.showbase.DirectObject import DirectObject
from panda3d import core

from .terrain import TerrainObject
from .general import Speed
from .animation import Character
from .audio import Music

import math


RESPONSIVENESS = 1.5


@Component()
class Controls:
    forward: str = 'mouse1'

    acceleration: float = 3.0
    deceleration: float = 2.0

    # degrees per second
    turn_speed: float = 150

    enabled: bool = True

    _collision = 0.0


class PlayerController(System, DirectObject):
    entity_filters = {
        'player': and_filter([Controls, TerrainObject, Speed]),
    }

    def __init__(self):
        System.__init__(self)

        self.last_ptr = None

        base.win.request_properties(core.WindowProperties(mouse_mode=core.WindowProperties.M_confined))

        self.gamepads = set()

        for dev in base.devices.get_devices(core.InputDevice.DeviceClass.gamepad):
            self._device_connected(dev, switch=False)

        base.accept('connect-device', self._device_connected)
        base.accept('disconnect-device', self._device_disconnected)

        self._control_mode = 'mouse'
        self._current_vec = core.Vec2(0)
        self._speed_target = 0.0

    def init_entity(self, filter_name, entity):
        controls = entity[Controls]
        controls._states = {}

        controls._states['forward'] = 0.0

        for key in 'mouse1', 'shift', 'gamepad-ltrigger', 'gamepad-rtrigger', 'gamepad-lshoulder', 'gamepad-rshoulder', 'gamepad-face_a', 'gamepad-lgrip', 'gamepad-rgrip', 'gamepad-lstick', 'gamepad-rstick':
            self.accept(key, self._button_pressed, [entity, 'forward'])
            self.accept(key + '-up', self._button_released, [entity, 'forward'])

    def destroy_entity(self, filter_name, entity, components={}):
        controls = components.get(Controls)
        if not controls:
            return

        del controls._states

        self.ignore_all()
        base.world.music[Music].play('peace')

        if Speed in entity:
            entity[Speed].current = 0.0

    def _device_connected(self, device, switch=True):
        if device.device_class == core.InputDevice.DeviceClass.gamepad and device not in self.gamepads:
            print("Detected", device)
            self.gamepads.add(device)
            base.attach_input_device(device, "gamepad")

            if switch:
                self.ensure_control_mode("gamepad")

    def _device_disconnected(self, device):
        if device in self.gamepads:
            print("Disconnected", device)
            self.gamepads.discard(device)
            base.detach_input_device(device)

            if not self.gamepads:
                self.ensure_control_mode("mouse")

    def _button_pressed(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 1.0

    def _button_released(self, entity, action):
        controls = entity[Controls]
        controls._states[action] = 0.0

    def ensure_control_mode(self, mode):
        if mode == self._control_mode:
            return

        self._control_mode = mode
        base.win.move_pointer(0, base.win.get_x_size() // 2, base.win.get_y_size() // 2)

        print("Switched to", mode, "controls")

        if mode == 'mouse':
            base.win.request_properties(core.WindowProperties(
                mouse_mode=core.WindowProperties.M_confined,
                cursor_hidden=False,
            ))
        else:
            base.win.request_properties(core.WindowProperties(
                mouse_mode=core.WindowProperties.M_absolute,
                cursor_hidden=True,
            ))

    def update(self, entities_by_filter):
        if not base.started or base.paused:
            return

        for entity in entities_by_filter['player']:
            obj = entity[TerrainObject]
            controls = entity[Controls]
            speed = entity[Speed]

            dt = globalClock.dt

            input = core.Vec2(0)

            ptr = base.win.get_pointer(0)
            if ptr.in_window:
                if self.last_ptr:
                    lean = ptr.x - base.win.get_x_size() / 2
                    lean_norm = (lean / base.win.get_x_size()) * 2
                    elevate = ((ptr.y / base.win.get_y_size()) - 0.5) * 2
                    input.set(lean_norm, -elevate)

                    if input.length_squared() > 0.02:
                        self.ensure_control_mode("mouse")
                else:
                    base.win.move_pointer(0, base.win.get_x_size() // 2, base.win.get_y_size() // 2)

                self.last_ptr = ptr
            else:
                self.last_ptr = None

            boost_input = 0.0

            for gamepad in self.gamepads:
                x_axis = gamepad.find_axis(core.InputDevice.Axis.right_x)
                y_axis = gamepad.find_axis(core.InputDevice.Axis.right_y)
                z_axis = gamepad.find_axis(core.InputDevice.Axis.right_trigger)
                xy = core.Vec2(x_axis.value, y_axis.value)
                if xy.length_squared() > 0.5:
                    self.ensure_control_mode("gamepad")
                xy *= xy.length()
                if xy.length_squared() > input.length_squared():
                    input.set(*xy)

                if z_axis.value > boost_input:
                    boost_input = z_axis.value

                x_axis = gamepad.find_axis(core.InputDevice.Axis.left_x)
                y_axis = gamepad.find_axis(core.InputDevice.Axis.left_y)
                z_axis = gamepad.find_axis(core.InputDevice.Axis.left_trigger)
                xy = core.Vec2(x_axis.value, y_axis.value)
                if xy.length_squared() > 0.5:
                    self.ensure_control_mode("gamepad")
                xy *= xy.length()
                if xy.length_squared() > input.length_squared():
                    input.set(*xy)

                if z_axis.value > boost_input:
                    boost_input = z_axis.value

            input.y *= abs(input.y)

            if controls._collision > input.y:
                input.y = controls._collision

            cur = core.Vec2(self._current_vec)
            delta = input.xy - cur
            dist = delta.length()
            if dist > 0:
                delta /= dist
                cur += delta * min(dt * RESPONSIVENESS, dist)

            if base.cam.parent.name != "dolly" and base.started:
                base.cam.set_z(cur.y)
                base.cam.set_x(cur.x * abs(cur.x) * 1.5)
                obj.direction -= cur.x * 0.5 * controls.turn_speed * dt

            self._current_vec = cur

            if not base.started:
                self._speed_target = 0.0
            elif (core.Vec2(base.world.dolmen[TerrainObject].position[0], base.world.dolmen[TerrainObject].position[1]) - core.Vec2(base.world.player[TerrainObject].position[0], base.world.player[TerrainObject].position[1])).length_squared() < 600:
                self._speed_target = speed.min
            elif controls._states['forward'] and base.cam.parent.name != 'dolly':
                self._speed_target = speed.max
            else:
                target_speed = boost_input * (speed.max - speed.min) + speed.min
                diff = target_speed - self._speed_target
                responsiveness = (speed.max - speed.min)
                if diff > 0:
                    self._speed_target += min(dt * responsiveness, diff)
                else:
                    self._speed_target -= min(dt * responsiveness, -diff)

                if self._speed_target < speed.min:
                    self._speed_target = speed.min
                if self._speed_target > speed.max:
                    self._speed_target = speed.max

            if controls.enabled and speed.current <= self._speed_target:
                speed.accelerate(controls.acceleration, max=self._speed_target)
            else:
                speed.accelerate(-controls.deceleration, min=self._speed_target)

            speed_t = (speed.current - speed.min) / (speed.max - speed.min)
            if speed_t > 0.8:
                base.world.music[Music].play('chase')
            elif speed_t < 0.2:
                base.world.music[Music].play('peace')

            base.world.player[Character]._state_actors['fly'].set_play_rate(speed_t*0.5+0.5, 'flap', partName='morphs')

            dir_rad = math.radians(obj.direction)
            obj.position = (
                obj.position[0] - math.sin(dir_rad) * speed.current * dt,
                obj.position[1] + math.cos(dir_rad) * speed.current * dt,
                obj.position[2],
            )
