from panda3d.core import *
from random import random


assets_dir = Filename(ExecutionEnvironment.expand_string("$MAIN_DIR/../assets"))
models_dir = Filename(assets_dir, "models")


def generate(model, size, ground_density, grass_density, min_scale=1.0, max_scale=1.0):
    root = NodePath("patch")

    model = NodePath(ModelPool.load_model(Filename(models_dir, model)))
    model.clear_model_nodes()
    model.flatten_strong()

    ground_dimension = int(round(size * ground_density))
    if ground_dimension == 0:
        ground_dimension = 1
    ground_spacing = size / ground_dimension

    for x in range(-1, ground_dimension + 1):
        for y in range(-1, ground_dimension + 1):
            cm = CardMaker("ground")
            cm.set_frame(
                ((x - 0.5) * ground_spacing, (y - 0.5) * ground_spacing, 0),
                ((x + 0.5) * ground_spacing, (y - 0.5) * ground_spacing, 0),
                ((x + 0.5) * ground_spacing, (y + 0.5) * ground_spacing, 0),
                ((x - 0.5) * ground_spacing, (y + 0.5) * ground_spacing, 0),
            )
            cm.set_uv_range((0, 0), (1, 0))
            root.attach_new_node(cm.generate())

    grass_dimension = int(round(size * grass_density))
    if grass_dimension > 0:
        grass_spacing = size / grass_dimension

    for x in range(grass_dimension):
        for y in range(grass_dimension):
            inst = model.copy_to(root)
            inst.set_pos((x + random() - 0.5) * grass_spacing, (y + random() - 0.5) * grass_spacing, 0)
            inst.set_h(random() * 360)

            t = random()
            inst.set_scale(min_scale * t + max_scale * (1 - t))
            inst.set_sz(inst.get_sz() * 1.5)

    root.set_pos(-size * 0.5, -size * 0.5, 0)
    root.flatten_strong()
    root = root.find("**/+GeomNode")
    root.set_tag('patch_size', str(size))

    bmin, bmax = root.get_tight_bounds()
    #root.node().set_bounds_type(BoundingVolume.BT_box)
    #root.node().set_final(True)
    #root.node().set_bounds(BoundingBox((size * -0.5 - 5, size * -0.5 - 5, 0), (size * 0.5 + 5, size * 0.5 + 5, 20)))
    return root


if __name__ == '__main__':
    size = 16
    ul = generate("star3-sub.egg", size=size, ground_density=1.0, grass_density=2.0, min_scale=0.8*0.5, max_scale=1.2*0.5)
    hi = generate("star3.egg", size=size, ground_density=1.0, grass_density=1.5, min_scale=0.8*0.5, max_scale=1.2*0.5)
    md = generate("star3.egg", size=size, ground_density=1.0, grass_density=1.0, min_scale=0.8*0.5, max_scale=1.2*0.5)
    lo = generate("star3.egg", size=size, ground_density=1.0, grass_density=0.5, min_scale=0.8*0.5, max_scale=1.2*0.5)
    no = generate("star3.egg", size=size, ground_density=1.0, grass_density=0)

    #ul.set_color_scale((1, 0, 1, 1),  100000)
    #hi.set_color_scale((1, 0, 0, 1),  100000)
    #md.set_color_scale((1, 1, 0, 1),  100000)

    lod = FadeLODNode("patch")
    lod.add_child(no.node())
    lod.add_switch(1000, 120)

    lod.add_child(md.node())
    lod.add_switch(120, 80)

    lod.add_child(hi.node())
    lod.add_switch(80, 32)

    lod.add_child(ul.node())
    lod.add_switch(32, 0)

    lod.set_tag('patch_size', str(size))

    #lod.set_bounds(BoundingBox((0, 0, 0), (size, size, 1)))
    #lod.set_final(True)

    sga = SceneGraphAnalyzer()
    sga.add_node(lod)
    print(sga)

    NodePath(lod).write_bam_file(Filename(assets_dir, "models/patch.bam"))
    print("Written to assets/models/patch.bam")
