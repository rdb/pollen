from wecs.panda3d.core import ECSShowBase
from panda3d.core import load_prc_file
import simplepbr

from .controls import Controls, PlayerController
from .terrain import Terrain, TerrainObject, TerrainSystem
from .lighting import Sun, LightingSystem
from .camera import Camera, CameraSystem
from .general import Speed


class Game(ECSShowBase):
    def __init__(self):
        load_prc_file('settings.prc')
        ECSShowBase.__init__(self)

        self.terrain = self.ecs_world.create_entity(Terrain(), name="Terrain")
        self.sun = self.ecs_world.create_entity(Sun())
        self.player = self.ecs_world.create_entity(
            TerrainObject(self.terrain, model='jack', position=(128, 64, 1.5), scale=0.5),
            Controls(),
            Speed(min=3.0, max=5.0),
            name="player",
        )

        self.camera = self.ecs_world.create_entity(
            Camera(target=self.player),
            name="camera",
        )

        self.add_system(PlayerController(), sort=-1)
        self.add_system(TerrainSystem(), sort=0)
        self.add_system(LightingSystem(), sort=1)
        self.add_system(CameraSystem(), sort=2)

        self.disable_mouse()
        self.set_main_camera(self.camera)
        simplepbr.init(msaa_samples=0, max_lights=1)

    def set_main_camera(self, entity):
        path = entity[Camera]._root
        base.cam = path
        base.camLens = path.node().get_lens()
        self.win.display_regions[1].set_camera(path)


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
