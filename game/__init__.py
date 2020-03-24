from wecs.panda3d.core import ECSShowBase
from panda3d.core import load_prc_file
from panda3d import core
import simplepbr

from random import random, choice

from .controls import Controls, PlayerController
from .terrain import Terrain, TerrainObject, TerrainSystem
from .lighting import Sun, AmbientLight, LightingSystem
from .camera import Camera, CameraSystem
from .general import Speed
from .animation import Character, Animation, AnimationPlayer


class Game(ECSShowBase):
    def __init__(self):
        load_prc_file('settings.prc')
        ECSShowBase.__init__(self)

        mat = core.Material()
        mat.twoside = True
        mat.base_color = (0.2, 0.2, 0.2, 1)
        mat.roughness = 0

        self.terrain = self.ecs_world.create_entity(Terrain(), name="Terrain")
        self.sun = self.ecs_world.create_entity(Sun())
        self.player = self.ecs_world.create_entity(
            #TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 64, 1), scale=0.09),
            TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 64, 1), scale=0.2, shadeless=True, material=mat),
            Character(
                animations={
                    "fly": [("butterfly", "forward"), ("morphs", "flap")],
                },
                subparts={
                    "butterfly": ["root", "butterfly.000", "butterfly.001", "butterfly.002", "butterfly.003", "butterfly.004", "butterfly.005", "butterfly.006", "butterfly.007", "butterfly.008", "butterfly.009", "butterfly.010", "butterfly.011", "butterfly.012", "butterfly.013", "butterfly.014", "butterfly.015", "butterfly.016", "butterfly.017", "butterfly.018", "butterfly.019", "butterfly.020", "butterfly.021", "butterfly.022", "butterfly.023", "butterfly.024", "butterfly.025", "butterfly.026", "butterfly.027", "butterfly.028", "butterfly.029", "butterfly.030", "butterfly.031", "butterfly.032", "butterfly.033", "butterfly.034", "butterfly.035", "butterfly.036", "butterfly.037", "butterfly.038", "butterfly.039", "butterfly.040", "butterfly.041", "butterfly.042", "butterfly.043", "butterfly.044", "butterfly.045", "butterfly.046", "butterfly.047", "butterfly.048", "butterfly.049", "butterfly.050", "butterfly.051", "butterfly.052", "butterfly.053", "butterfly.054", "butterfly.055", "butterfly.056", "butterfly.057", "butterfly.058", "butterfly.059", "butterfly.060", "butterfly.061", "butterfly.062", "butterfly.063"],
                    "morphs": ["Key 1", "Key 2", "Key 3", "Key 4", "Key 5", "Key 6", "Key 7", "Key 8"],
                },
            ),
            Controls(),
            Animation(),
            Speed(min=3.0, max=5.0),
            name="player",
        )

        self.player[Animation].play("fly")

        self.camera = self.ecs_world.create_entity(
            Camera(target=self.player),
            name="camera",
        )

        mat = core.Material()
        mat.twoside = True
        mat.base_color = (1, 1, 1, 1)

        self.flower = self.ecs_world.create_entity(
            TerrainObject(self.terrain, model='models/flower.bam', position=(128, 64+16, 0), scale=0.5, material=mat),
        )

        self.rocks = []
        for i in range(100):
            sub = choice([
                '**/rock.000',
                '**/rock.001',
                '**/rock.002',
                '**/rock.003',
                '**/rock.004',
                '**/rock.005',
                '**/rock.006',
            ])
            rocks = self.ecs_world.create_entity(
                TerrainObject(self.terrain, model='models/rocks.bam', path=sub, scale=random()*4+1, position=(random() * 256, random() * 256, 0), material=mat),
            )

        #self.ecs_world.create_entity(AmbientLight(intensity=0.1, color=(0.15, 0.3, 1.0)))

        self.add_system(PlayerController(), sort=-1)
        self.add_system(TerrainSystem(), sort=0)
        self.add_system(LightingSystem(), sort=1)
        self.add_system(CameraSystem(), sort=2)
        self.add_system(AnimationPlayer(), sort=3)

        self.disable_mouse()
        self.set_main_camera(self.camera)
        simplepbr.init(msaa_samples=0, max_lights=1)

        self.accept('f12', self.screenshot)

    def set_main_camera(self, entity):
        path = entity[Camera]._root
        base.cam = path
        base.camLens = path.node().get_lens()
        self.win.display_regions[1].set_camera(path)


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
