from panda3d.core import *
from random import random


assets_dir = Filename(ExecutionEnvironment.expand_string("$MAIN_DIR/../assets"))


def generate(size, density, min_scale=1.0, max_scale=1.0):
    root = NodePath("patch")

    model = NodePath(ModelPool.load_model(Filename(assets_dir, "models/star3-sub.egg")))
    model.clear_model_nodes()
    model.flatten_strong()

    dimension = int(round(size * density))
    spacing = size / dimension

    for x in range(dimension):
        for y in range(dimension):
            cm = CardMaker("ground")
            cm.set_frame(
                ((x - 0.5) * spacing, (y - 0.5) * spacing, 0),
                ((x + 0.5) * spacing, (y - 0.5) * spacing, 0),
                ((x + 0.5) * spacing, (y + 0.5) * spacing, 0),
                ((x - 0.5) * spacing, (y + 0.5) * spacing, 0),
            )
            cm.set_uv_range((0, 0), (1, 0))
            #root.attach_new_node(cm.generate())

            inst = model.copy_to(root)
            inst.set_pos((x + random() - 0.5) * spacing, (y + random() - 0.5) * spacing, 0)
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
    root = generate(size=32, density=1.75, min_scale=0.8*0.5, max_scale=1.2*0.5)

    sga = SceneGraphAnalyzer()
    sga.add_node(root.node())
    print(sga)

    root.write_bam_file(Filename(assets_dir, "models/patch.bam"))
    print("Written to assets/models/patch.bam")
