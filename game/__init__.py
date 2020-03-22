from wecs.panda3d.core import ECSShowBase
from .terrain import Terrain, TerrainSystem
from .lighting import Sun, LightingSystem
import simplepbr


class Game(ECSShowBase):
    def __init__(self):
        ECSShowBase.__init__(self)
        simplepbr.init()

        self.terrain = self.ecs_world.create_entity(Terrain(), name="Terrain")
        self.sun = self.ecs_world.create_entity(Sun())

        self.add_system(TerrainSystem(), sort=0)
        self.add_system(LightingSystem(), sort=1)

        self.disable_mouse()
        self.cam.set_pos(-32, -32, 64)
        self.cam.look_at(64, 64, 1)


def main():
    game = Game()
    game.run()
