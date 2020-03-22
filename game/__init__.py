from wecs.panda3d.core import ECSShowBase
from panda3d.core import load_prc_file
import simplepbr

from .controls import Controls, PlayerController
from .terrain import Terrain, TerrainObject, TerrainSystem
from .lighting import Sun, LightingSystem
from .camera import Camera, CameraSystem


class Game(ECSShowBase):
    def __init__(self):
        load_prc_file('settings.prc')
        ECSShowBase.__init__(self)

        self.terrain = self.ecs_world.create_entity(Terrain(), name="Terrain")
        self.sun = self.ecs_world.create_entity(Sun())
        self.player = self.ecs_world.create_entity(
            TerrainObject(self.terrain, model='jack', position=(64, 64, 0.5), scale=0.5),
            Controls())

        self.camera = self.ecs_world.create_entity(
            Camera(target=self.player),
        )

        self.add_system(PlayerController(), sort=-1)
        self.add_system(TerrainSystem(), sort=0)
        self.add_system(LightingSystem(), sort=1)
        self.add_system(CameraSystem(), sort=2)

        self.disable_mouse()
        self.set_main_camera(self.camera)

    def set_main_camera(self, entity):
        path = entity[Camera]._root
        base.cam = path
        base.camLens = path.node().get_lens()
        self.win.display_regions[1].set_camera(path)
        simplepbr.init(msaa_samples=0, max_lights=1)


def main():
    game = Game()
    game.run()
