from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

load_prc_file_data("", "win-size 512 512")

base = ShowBase(windowType='offscreen')
base.disable_mouse()

assets_dir = Filename(ExecutionEnvironment.expand_string("$MAIN_DIR/../assets"))

tuft = base.loader.load_model(Filename(assets_dir, "/models/tuft.egg"))
tuft.set_two_sided(True)
tuft.reparent_to(base.render)

pmin, pmax = tuft.get_tight_bounds()
radius = tuft.get_bounds().get_radius()

dim = max(pmax[2] - pmin[2], radius * 2)

lens = OrthographicLens()
lens.set_near_far(-dim, dim * 3)
lens.set_film_size(dim, dim)
lens.film_offset = (0, dim * 0.5)
base.cam.node().set_lens(lens)

base.cam.set_y(-dim)

tex = Texture()
base.win.add_render_texture(tex, GraphicsOutput.RTM_copy_ram)

base.camera.set_h(0)
base.graphicsEngine.render_frame()
base.graphicsEngine.render_frame()
tex.write(Filename(assets_dir, "/textures/tuft0.png"))

base.camera.set_h(60)
base.graphicsEngine.render_frame()
base.graphicsEngine.render_frame()
tex.write(Filename(assets_dir, "/textures/tuft1.png"))

base.camera.set_h(120)
base.graphicsEngine.render_frame()
base.graphicsEngine.render_frame()
tex.write(Filename(assets_dir, "/textures/tuft2.png"))
