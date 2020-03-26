from wecs.core import Entity, Component, System
from wecs.core import and_filter

from direct.actor.Actor import Actor
from panda3d import core

from .animation import Character
from .general import Speed

from dataclasses import field


@Component()
class Terrain:
    # pixels per meter, should be power of 2
    resolution: float = 1 / 2

    size: float = 256
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
    material: core.Material = None
    path: str = None
    shadeless: bool = False
    shader: core.Shader = None


class TerrainSystem(System):
    entity_filters = {
        'terrain': and_filter([Terrain]),
        'object': and_filter([TerrainObject]),
        'movable': and_filter([TerrainObject, Speed]),
    }

    def __init__(self):
        System.__init__(self)

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
        heightmap_size = scaled_size# + 1

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
        #heightfield.perlin_noise_fill(noise)
        heightfield.read('assets/textures/heightmap.png')
        #heightfield.make_grayscale()
        #assert heightfield.is_grayscale()

        # We use GeoMipTerrain just for determining the normals at the moment.
        heightfield2 = core.PNMImage(heightmap_size + 1, heightmap_size + 1, 1)
        heightfield2.set_maxval(0xffff)
        heightfield2.copy_sub_image(heightfield, 0, 0)

        terrain = core.GeoMipTerrain(entity._uid.name)
        terrain.set_heightfield(heightfield2)
        terrain.set_bruteforce(True)
        terrain.set_block_size(min(32, scaled_size))
        #terrain.set_color_map(heightfield)

        # Store both height and normal in the same texture.
        nimg = core.PNMImage(heightmap_size, heightmap_size, 4, color_space=core.CS_linear)

        for x in range(heightmap_size):
            for y in range(heightmap_size):
                normal = terrain.get_normal(x, y)
                normal.x *= component.resolution
                normal.y *= component.resolution
                normal.z /= max_mag
                normal.normalize()
                nimg.set_xel(x, y, normal * 0.5 + 0.5)
                #nimg.set_alpha(x, y, terrain.get_elevation(x, y))
                nimg.set_alpha(x, y, heightfield.get_gray(x, y))

        ntex = core.Texture("normal")
        ntex.load(nimg)
        ntex.wrap_u = core.SamplerState.WM_repeat
        ntex.wrap_v = core.SamplerState.WM_repeat
        ntex.set_keep_ram_image(True)
        component._peeker = ntex.peek()

        root = terrain.get_root()
        root.set_scale(1.0 / component.resolution, 1.0 / component.resolution, max_mag)
        #root.reparent_to(base.render)
        #root.set_texture(htex)
        #terrain.generate()

        mat = core.Material()
        #mat.base_color = (0.16, 0.223, 0.076, 1)
        mat.base_color = (0.4, 0.6, 0.4, 1)
        mat.base_color = (
            41.6/255.0,
            73.7/255.0,
            29.0/255.0,
            1)
        #print(mat.base_color)
        mat.roughness = 1
        #root.set_material(mat)

        component._scale = core.VBase3(component.resolution / scaled_size, component.resolution / scaled_size, max_mag)

        component._wind_map = loader.load_texture("assets/textures/wind.png")
        component._wind_sound = loader.load_sfx("assets/sfx/wind-low.ogg")
        component._wind_sound.set_loop(True)
        component._wind_sound.play()

        grass_root = render.attach_new_node("grass")
        grass_root.set_shader(core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/grass.vert", "assets/shaders/grass.frag"), 20)
        render.set_shader_input("scale", component.resolution / scaled_size, component.resolution / scaled_size, max_mag)
        grass_root.set_shader_input("terrainmap", ntex)
        render.set_shader_input("windmap", component._wind_map)
        grass_root.set_material(mat)

        #grass_root.node().set_bounds(core.BoundingSphere())
        #grass_root.node().set_final(True)

        grass_root.set_bin('background', 10)

        patch = loader.load_model("assets/models/patch.bam")
        patch_size = int(patch.get_tag('patch_size'))

        self._r_build_grass_octree(grass_root, patch, patch_size, component.size * 2)
        grass_root.set_pos(-0.5 * component.size, -0.5 * component.size, 0)

        component._grass_root = grass_root

    def _r_build_grass_octree(self, parent, patch, patch_size, total_size):
        num_patches = int(total_size // patch_size)

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
                #inst.node().set_final(True)
                #inst.node().set_bounds(core.BoundingBox((x, y, 0), (x+patch_size, y+patch_size, 100)))

    def init_terrain_object(self, entity):
        obj = entity[TerrainObject]

        path = base.render.attach_new_node(entity._uid.name)
        obj._root = path

        if obj.model:
            model = loader.load_model(obj.model)

            if obj.path:
                model = model.find(obj.path)
                model.clear_transform()

            #model.flatten_strong()

            if model.find("**/+Character"):
                if Character in entity:
                    model = Actor(obj.model)
                    char = entity[Character]
                    char._actor = model
                    model.set_transparency(1)

                    for part, joints in char.subparts.items():
                        char._actor.make_subpart(part, joints)

                    #if obj.shadeless:
                    #    model.set_light_off(1)

            if 'flower' in obj.model:
                mat = core.Material()
                #mat.base_color = (0.3, 0.3, 2, 1)
                mat.base_color = (2.0, 0.75, 0.6, 1)
                model.find('**/petals').set_material(mat, 10000000)
                model.find('**/petals').set_light_off(100)
                model.find('**/leafs').hide()
                #model.find('**/petals').set_two_sided(True)

            if obj.material:
                model.set_material(obj.material, 1)

            if obj.shader:
                model.set_shader(obj.shader, 10)
            model.reparent_to(path)

        component = obj.terrain[Terrain]

        pos = obj.position
        res = component.resolution
        col = core.LColor()
        component._peeker.lookup_bilinear(
            col,
            (pos[0] * component._scale.x) % 1.0,
            (pos[1] * component._scale.y) % 1.0,
        )
        height = col.w * component._scale.z
        obj._root.set_pos(pos[0], pos[1], pos[2] + height)
        obj._root.get_child(0).set_scale(obj.scale)
        obj._root.set_h(obj.direction)

        for tex in obj._root.find_all_textures():
            tex.wrap_u = core.SamplerState.WM_clamp
            tex.wrap_v = core.SamplerState.WM_clamp

    def update(self, entities_by_filter):
        for entity in entities_by_filter['movable']:
            obj = entity[TerrainObject]

            component = obj.terrain[Terrain]
            while obj.position[0] < 0:
                obj.position = (obj.position[0] + component.size, obj.position[1], obj.position[2])
            while obj.position[1] < 0:
                obj.position = (obj.position[0], obj.position[1] + component.size, obj.position[2])

            while obj.position[0] > component.size:
                obj.position = (obj.position[0] - component.size, obj.position[1], obj.position[2])
            while obj.position[1] > component.size:
                obj.position = (obj.position[0], obj.position[1] - component.size, obj.position[2])

            pos = obj.position
            res = component.resolution
            col = core.LColor()
            component._peeker.lookup_bilinear(
                col,
                (pos[0] * component._scale.x) % 1.0,
                (pos[1] * component._scale.y) % 1.0,
            )
            height = col.w * component._scale.z
            obj._root.set_pos(pos[0], pos[1], pos[2] + height)
            obj._root.get_child(0).set_scale(obj.scale)
            obj._root.set_h(obj.direction)

            #obj._root.set_texture_off(10)

            if entity._uid.name == "player": #haack
                t = 0
                if Speed in entity:
                    speed = entity[Speed]
                    if speed.max is not None:
                        #t = (speed.current - speed.min) / (speed.max - speed.min)
                        t = speed.current / speed.max

                obj.terrain[Terrain]._grass_root.set_shader_input("player", pos[0], pos[1], t)

                wspos = base.cam.get_pos(render).xy
                peeker = component._wind_map.peek()
                wind_coord = core.Vec2(pos[0], pos[1]) * component._scale[0] * 4 + core.Vec2(globalClock.frame_time * 0.06, 0)
                wind = core.LColor()
                peeker.lookup(wind, wind_coord.x, wind_coord.y)
                #wind = max(1.0 - wind.x - 0.5, 0.0) + 0.5
                wind = abs(1.0 - wind.x - 0.5) + 0.5
                component._wind_sound.set_play_rate(wind * 2 + 0.5)
                component._wind_sound.set_volume(max(0, wind - 0.35))

    def destroy_entity(self, filter_name, entity):
        if filter_name == 'terrain':
            pass
        elif filter_name == 'object':
            entity[TerrainObject]._root.remove_node()
