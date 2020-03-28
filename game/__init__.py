from direct.showbase.ShowBase import ShowBase
from wecs.panda3d.core import ECSShowBase
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from panda3d.core import load_prc_file
from panda3d import core

from .world import World


class Game(ECSShowBase):
    def __init__(self):
        main_dir = core.ExecutionEnvironment.get_environment_variable("MAIN_DIR")
        main_dir = core.Filename.from_os_specific(main_dir)
        core.load_prc_file(core.Filename(main_dir, "settings.prc"))

        ShowBase.__init__(self)
        self.disable_mouse()

        self.world = World()

        self.accept('f12', self.screenshot)
        self.accept('1', self.oobeCull)
        self.accept('2', self.world.press_2)
        self.accept('3', self.world.press_3)
        self.accept('4', self.world.ending)
        self.accept('p', self.world.print_pos)



def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
