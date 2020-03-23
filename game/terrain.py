from wecs.core import Entity, Component, System
from wecs.core import and_filter

from panda3d import core

from dataclasses import field


@Component()
class Terrain:
    # pixels per meter, should be power of 2
    resolution: float = 1

    size: float = 128
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

        heightfield = core.PNMImage(heightmap_size, heightmap_size, 1)
        heightfield.set_maxval(0xffff)
        heightfield.perlin_noise_fill(noise)
        assert heightfield.is_grayscale()

        htex = core.Texture("height")
        htex.load(heightfield)

        # Don't clamp this!  We also use it for wind
        #htex.wrap_u = core.SamplerState.WM_clamp
        #htex.wrap_v = core.SamplerState.WM_clamp

        terrain = core.GeoMipTerrain(entity._uid.name)
        terrain.set_heightfield(heightfield)
        terrain.set_bruteforce(True)
        terrain.set_block_size(min(32, scaled_size))
        #terrain.set_color_map(heightfield)

        nimg = core.PNMImage(heightmap_size, heightmap_size, 3)
        for x in range(heightmap_size):
            for y in range(heightmap_size):
                normal = terrain.get_normal(x, y)
                normal.x *= component.resolution
                normal.y *= component.resolution
                normal.z /= max_mag
                normal.normalize()
                nimg.set_xel(x, y, normal * 0.5 + 0.5)

        ntex = core.Texture("normal")
        ntex.load(nimg)
        ntex.wrap_u = core.SamplerState.WM_clamp
        ntex.wrap_v = core.SamplerState.WM_clamp

        root = terrain.get_root()
        root.set_scale(1.0 / component.resolution, 1.0 / component.resolution, max_mag)
        root.reparent_to(base.render)
        root.set_texture(htex)
        terrain.generate()

        mat = core.Material()
        mat.base_color = (0.198, 0.223, 0.076, 1)
        mat.roughness = 0.9
        root.set_material(mat)

        grass_root = render.attach_new_node("grass")
        grass_root.set_shader(core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/grass.vert", "assets/shaders/grass.frag"), 10)
        grass_root.set_shader_input("scale", component.resolution / scaled_size, component.resolution / scaled_size, max_mag)
        grass_root.set_shader_input("heightfield", htex)
        grass_root.set_shader_input("normal", ntex)
        grass_root.set_material(mat)

        grass_root.set_bin('background', 10)

        patch = loader.load_model("assets/models/patch.bam")
        patch_size = int(patch.get_tag('patch_size'))
        self._r_build_grass_octree(grass_root, patch, patch_size, component.size)

        self.terrains[entity] = terrain

    def _r_build_grass_octree(self, parent, patch, patch_size, total_size):
        num_patches = total_size // patch_size

        if num_patches >= 4:
            half_size = total_size // 2

            node = parent.attach_new_node("1")
            node.node().set_bounds_type(core.BoundingVolume.BT_box)
            node.set_pos(0, 0, 0)
            self._r_build_grass_octree(node, patch, patch_size, half_size)

            node = parent.attach_new_node("2")
            node.node().set_bounds_type(core.BoundingVolume.BT_box)
            node.set_pos(0, half_size, 0)
            self._r_build_grass_octree(node, patch, patch_size, half_size)

            node = parent.attach_new_node("3")
            node.node().set_bounds_type(core.BoundingVolume.BT_box)
            node.set_pos(half_size, 0, 0)
            self._r_build_grass_octree(node, patch, patch_size, half_size)

            node = parent.attach_new_node("4")
            node.node().set_bounds_type(core.BoundingVolume.BT_box)
            node.set_pos(half_size, half_size, 0)
            self._r_build_grass_octree(node, patch, patch_size, half_size)
            return

        for x in range(num_patches):
            for y in range(num_patches):
                inst = patch.copy_to(parent)
                inst.set_pos(x * patch_size, y * patch_size, 0)

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
