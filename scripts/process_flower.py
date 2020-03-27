from panda3d import core

mat = core.Material()
mat.base_color = (2.0, 0.75, 0.6, 1)
model = core.NodePath(core.ModelPool.load_model("assets/models/flower.bam"))
model.find('**/petals').set_material(mat, 10000000)
model.find('**/petals').set_light_off(100)
model.find('**/leafs').remove_node()
model.find('**/vine').remove_node()

# Work around blend2bam bug that manifests when flattening
for gnode in model.find_all_matches("**/+GeomNode"):
    for geom in gnode.node().modify_geoms():
        vdata = geom.modify_vertex_data()
        if not vdata.get_format().has_column("transform_blend") and vdata.get_transform_blend_table():
            vdata.clear_transform_blend_table()

model.flatten_strong()

gnode = model.find("**/+GeomNode")
gnode.name = "flower"

#character = model.get_child(0)
#model = core.NodePath(core.LODNode("flower"))
#model.node().add_child(character.node())
#model.node().add_switch(50, 0)

model.write_bam_file("assets/models/flower.bam")

sga = core.SceneGraphAnalyzer()
sga.add_node(model.node())
print(sga)
model.ls()
