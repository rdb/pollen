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

    for x in range(ground_dimension):
        for y in range(ground_dimension):
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

    root.flatten_strong()
    root = root.find("**/+GeomNode")
    root.set_tag('patch_size', str(size))

    #bmin, bmax = root.get_tight_bounds()
    #root.node().set_bounds_type(BoundingVolume.BT_box)
    #root.node().set_final(True)
    #root.node().set_bounds(BoundingBox(bmin, bmax))
    return root


if __name__ == '__main__':
    size = 16
    hi = generate("star3-sub.egg", size=size, ground_density=1.0, grass_density=2.0, min_scale=0.8*0.5, max_scale=1.2*0.5)
    md = generate("star3.egg", size=size, ground_density=1.0, grass_density=1.0, min_scale=0.8*0.5, max_scale=1.2*0.5)
    lo = generate("star3.egg", size=size, ground_density=1.0, grass_density=0.5, min_scale=0.8*0.5, max_scale=1.2*0.5)
    no = generate("star3.egg", size=size, ground_density=1.0, grass_density=0)

    lod = FadeLODNode("patch")
    lod.add_child(no.node())
    lod.add_switch(100000, 200)

    lod.add_child(md.node())
    lod.add_switch(200, 50)

    lod.add_child(hi.node())
    lod.add_switch(50, 0)

    lod.set_tag('patch_size', str(size))

    sga = SceneGraphAnalyzer()
    sga.add_node(lod)
    print(sga)

    NodePath(lod).write_bam_file(Filename(assets_dir, "models/patch.bam"))
    print("Written to assets/models/patch.bam")
