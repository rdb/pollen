from wecs.core import Entity, Component, System
from wecs.core import and_filter

from panda3d import core

from dataclasses import field


@Component()
class Terrain:
    # pixels per meter, should be power of 2
    resolution: float = 1

    size: float = 512
    seed: int = 100
    octaves: tuple = (
        # bump height, bump width in metres
        (10, 32),
        (2, 10),
        (0.1, 3),
    )


@Component()
class TerrainObject:
    """Components for objects that are positioned relative to the terrain."""

    terrain: Entity
    model: core.NodePath = None
    position: tuple = (0, 0, 0)
    scale: float = 1.0
    direction: float = 0.0


class TerrainSystem(System):
    entity_filters = {
        'terrain': and_filter([Terrain]),
        'object': and_filter([TerrainObject]),
    }

    def __init__(self):
        System.__init__(self)

        self.terrains = {}
        self.objects = {}

    def init_entity(self, filter_name, entity):
        if filter_name == 'terrain':
            return self.init_terrain(entity)
        elif filter_name == 'object':
            return self.init_terrain_object(entity)

    def init_terrain(self, entity):
        component = entity[Terrain]

        noise = core.StackedPerlinNoise2()

        scaled_size = int(component.size * component.resolution)
        heightmap_size = scaled_size + 1

        print(f"Terrain complexity: {scaled_size}")

        max_mag = 0.0
        for mag, scale in component.octaves:
            if mag > max_mag:
                max_mag = mag

        for mag, scale in component.octaves:
            scale /= component.size
            noise.add_level(core.PerlinNoise2(scale, scale, 256, component.seed), mag / max_mag)

        heightfield = core.PNMImage(heightmap_size, heightmap_size)
        heightfield.set_maxval(0xffff)
        heightfield.perlin_noise_fill(noise)

        tex = core.Texture()
        tex.clear_color = (1, 1, 1, 1)
        tex.load(heightfield)

        terrain = core.GeoMipTerrain(entity._uid.name)
        terrain.set_heightfield(heightfield)
        terrain.set_bruteforce(True)
        terrain.set_block_size(min(32, scaled_size))

        root = terrain.get_root()
        root.set_scale(1.0 / component.resolution, 1.0 / component.resolution, max_mag)
        root.reparent_to(base.render)
        root.set_texture(tex)
        terrain.generate()

        mat = core.Material()
        mat.base_color = (0.198, 0.223, 0.076, 1)
        mat.roughness = 0.5
        root.set_material(mat)

        self.terrains[entity] = terrain

    def init_terrain_object(self, entity):
        obj = entity[TerrainObject]

        path = base.render.attach_new_node(entity._uid.name)
        obj._root = path

        if obj.model:
            model = loader.load_model(obj.model)
            model.reparent_to(path)

    def update(self, entities_by_filter):
        for entity in entities_by_filter['object']:
            obj = entity[TerrainObject]
            pos = obj.position

            res = obj.terrain[Terrain].resolution
            terrain = self.terrains[obj.terrain]
            z = terrain.get_elevation(pos[0] * res, pos[1] * res)
            obj._root.set_pos(pos[0], pos[1], pos[2] + z * terrain.get_root().get_sz())
            obj._root.set_scale(obj.scale)
            obj._root.set_h(obj.direction)

    def destroy_entity(self, filter_name, entity):
        if filter_name == 'terrain':
            terrain = self.terrains.pop(entity)
            terrain.get_root().remove_node()
        elif filter_name == 'object':
            entity[TerrainObject]._root.remove_node()
