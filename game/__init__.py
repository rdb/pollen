from direct.showbase.ShowBase import ShowBase
import direct.gui.DirectGuiGlobals as DGG
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, LerpFunctionInterval
from panda3d import core
import sys

import simplepbr


from .audio import Music
from .menu import Menu
from .world import World


QUALITY_HIGH = 3
QUALITY_MEDIUM = 2
QUALITY_LOW = 1
QUALITY_POTATO = 0


class Game(ShowBase):
    def __init__(self):
        main_dir = core.ExecutionEnvironment.get_environment_variable("MAIN_DIR")
        main_dir = core.Filename.from_os_specific(main_dir)
        core.load_prc_file(core.Filename(main_dir, "settings.prc"))

        ShowBase.__init__(self)
        self.disable_mouse()

        DGG.setDefaultRolloverSound(loader.load_sfx('sfx/ui-a.ogg'))
        DGG.setDefaultClickSound(loader.load_sfx('sfx/ui-b.ogg'))

        base.setBackgroundColor((0, 0, 0, 1))

        self.quality_menu = Menu('quality.', [
            ('high.', self.setup_high),
            ('medium.', self.setup_medium),
            ('low.', self.setup_low),
            ('none.', self.setup_potato),
        ])
        self.quality_menu.show()

    def setup_high(self):
        self.setup(QUALITY_HIGH)

    def setup_medium(self):
        self.setup(QUALITY_MEDIUM)

    def setup_low(self):
        self.setup(QUALITY_LOW)

    def setup_potato(self):
        self.setup(QUALITY_POTATO)

    def setup(self, quality):
        self.quality_menu.hide()
        base.quality = quality

        is_fullscreen = self.win.get_properties().fullscreen

        self.main_menu = Menu('pollen.', [
            ('begin.', self.start_game),
            ('no music.', self.toggle_music),
            ('window.' if is_fullscreen else 'fullscreen.', self.toggle_fullscreen),
            ('leave.', self.stop_game),
        ])

        self.pause_menu = Menu('paused.', [
            ('resume.', self.resume),
            ('no music.', self.toggle_music),
            ('stop.', self.stop_game),
        ])

        base.paused = False

        #base.cam.set_pos(-3, 0, 10)
        base.cam.set_pos(0, 0, 10)
        base.cam.set_hpr(0, 5, 0)

        if base.quality >= QUALITY_HIGH:
            samples = 8
        elif base.quality >= QUALITY_MEDIUM:
            samples = 4
        else:
            samples = 0
        simplepbr.init(msaa_samples=samples, max_lights=2)

        self.world = World()

        self.accept('f12', self.screenshot)
        self.accept('1', self.oobeCull)
        self.starting = False
        self.started = False
        self.music_on = True

        self.main_menu.show()

        self.setBackgroundColor((0.6, 1.0, 1.4, 1.0))

    def stop_game(self):
        self.main_menu.hide()
        self.pause_menu.hide()
        base.transitions.setFadeColor(0, 0, 0)
        base.transitions.getFadeOutIval(1.0).start()
        taskMgr.doMethodLater(1.5, lambda task: sys.exit(), 'exit')

    def start_game(self):
        if self.starting:
            return

        self.starting = True

        self.main_menu.hide()
        #self.world.start_game()

        Sequence(
            base.cam.hprInterval(2, hpr=(0, 30, 0), blendType="easeInOut"),
            Func(self.start_starting),
            #Func(self.finish_starting),
        ).start()

    def start_starting(self):
        self.world.finish_loading()

        old_hpr = base.cam.get_hpr()
        base.cam.look_at(base.camera.get_parent(), (0, 0, 0))
        base.cam.set_h(old_hpr[0])
        cam_hpr = base.cam.get_hpr()
        base.cam.set_hpr(old_hpr)

        old_hpr = base.camera.get_hpr()
        base.camera.look_at(0, 0, 0)
        camera_hpr = base.camera.get_hpr()
        base.camera.set_hpr(old_hpr)

        #self.world.activate()
        self.started = True
        Sequence(
            Wait(0.5),
            Parallel(
                LerpFunctionInterval(base.camLens.set_fov, 2.0, fromData=base.camLens.get_fov(), toData=80, blendType='easeIn'),
                base.cam.hprInterval(2, hpr=(0, 0, 0), blendType="easeInOut"),
                base.camera.hprInterval(2, hpr=camera_hpr, blendType="easeInOut"),
            ),
            Func(self.finish_starting),
        ).start()

    def finish_starting(self):
        self.started = True
        self.world.activate()
        self.accept('2', self.world.press_2)
        self.accept('3', self.world.press_3)
        self.accept('4', self.world.ending)
        self.accept('p', self.world.print_pos)

        self.accept('pause', self.pause)
        self.accept('escape', self.pause)

    def pause(self):
        if self.paused:
            return
        self.world.music[Music].play('pause')
        self.paused = True
        self.pause_menu.show()

    def resume(self):
        self.pause_menu.hide()
        self.paused = False

    def toggle_fullscreen(self):
        is_fullscreen = self.win.get_properties().fullscreen
        if is_fullscreen:
            print("Disabling fullscreen")
            size = core.WindowProperties.get_default().size
            self.win.request_properties(core.WindowProperties(fullscreen=False, origin=(-2, -2), size=size))
            self.main_menu.buttons[2]['text'] = 'fullscreen.'
        else:
            print("Enabling fullscreen")
            size = self.pipe.get_display_width(), self.pipe.get_display_height()
            self.win.request_properties(core.WindowProperties(fullscreen=True, size=size))
            self.main_menu.buttons[2]['text'] = 'window.'

    def toggle_music(self):
        if self.music_on:
            print("Disabling music")
            self.enable_music(False)
            self.main_menu.buttons[1]['text'] = 'yes music.'
            self.pause_menu.buttons[1]['text'] = 'yes music.'
            self.music_on = False
        else:
            print("Enabling music")
            self.enable_music(True)
            self.main_menu.buttons[1]['text'] = 'no music.'
            self.pause_menu.buttons[1]['text'] = 'no music.'
            self.music_on = True


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
