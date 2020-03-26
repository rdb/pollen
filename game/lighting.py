from wecs.core import Component, System
from wecs.core import and_filter

from panda3d import core
import math


@Component()
class Sun:
    azimuth: float = 90
    elevation: float = 45
    color_temperature: float = 6500
    intensity: float = 5
    priority: float = 0


@Component()
class AmbientLight:
    color: tuple
    intensity: float = 1


class LightingSystem(System):
    entity_filters = {
        'sun': and_filter([Sun]),
        'ambient': and_filter([AmbientLight]),
    }

    def __init__(self):
        System.__init__(self)

        self.lights = {}

    def init_entity(self, filter_name, entity):
        if filter_name == 'sun':
            sun = entity[Sun]
            light = core.DirectionalLight(entity._uid.name)
            light.priority = sun.priority
            path = base.render.attach_new_node(light)
            path.set_h(sun.azimuth)
            self.lights[entity] = path

        elif filter_name == 'ambient':
            ambient = entity[AmbientLight]
            light = core.AmbientLight(entity._uid.name)
            light.color = core.LVecBase4(*ambient.color, 0) * ambient.intensity
            path = base.render.attach_new_node(light)
            self.lights[entity] = path

        base.render.set_light(path)

    def update(self, entities_by_filter):
        for entity in entities_by_filter['sun']:
            sun = entity[Sun]
            elev_rad = math.radians(sun.elevation)

            light = self.lights[entity].node()
            light.direction = (0, math.cos(elev_rad), -math.sin(elev_rad))
            light.color_temperature = sun.color_temperature
            light.color = light.color * sun.intensity
            self.lights[entity].set_h(entity[Sun].azimuth)

    def destroy_entity(self, filter_name, entity):
        path = self.lights.pop(entity)
        path.remove_node()
