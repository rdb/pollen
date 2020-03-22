from wecs.core import Component, System
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


class TerrainSystem(System):
    entity_filters = {
        'terrain': and_filter([Terrain]),
    }

    def __init__(self):
        System.__init__(self)

        self.terrains = {}

    def init_entity(self, filter_name, entity):
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

    def destroy_entity(self, filter_name, entity):
        terrain = self.terrains.pop(entity)
        terrain.get_root().remove_node()
