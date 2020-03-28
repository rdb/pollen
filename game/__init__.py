from direct.showbase.ShowBase import ShowBase
from wecs.panda3d.core import ECSShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, LerpFunctionInterval
from panda3d import core
import sys

import simplepbr


from .world import World


class Game(ECSShowBase):
    def __init__(self):
        main_dir = core.ExecutionEnvironment.get_environment_variable("MAIN_DIR")
        main_dir = core.Filename.from_os_specific(main_dir)
        core.load_prc_file(core.Filename(main_dir, "settings.prc"))

        ShowBase.__init__(self)
        self.disable_mouse()

        mat = core.Material()
        mat.twoside = True
        mat.roughness = 1
        mat.base_color = (1, 1, 1, 1)

        #self.flower = Actor('assets/models/flower.bam')
        #self.flower.reparent_to(render)
        #self.flower.set_scale(0.5)
        #self.flower.set_material(mat, 100)
        #self.flower.loop('closed_idle')
        #self.flower.set_pos((251.887-256+3, 43.6127-5, 8.90506))
        #self.flower.set_fog_off(100)
        #self.flower.set_shader_off(100)

        self.draw_menu()

        #base.cam.set_pos(-3, 0, 10)
        base.cam.set_pos(0, 0, 10)
        base.cam.set_hpr(0, 5, 0)

        simplepbr.init(msaa_samples=0, max_lights=2)

        self.world = World()

        self.accept('f12', self.screenshot)
        self.accept('1', self.oobeCull)
        self.starting = False
        self.started = False

    def draw_menu(self):
        self.menu = base.a2dBottomLeft.attach_new_node("menu")

        self.title = OnscreenText(parent=self.menu, text='pollen.', align=core.TextNode.A_left, pos=(0.07, 0.625), scale=0.1, fg=(1, 1, 1, 1))

        text_fg = (1, 1, 1, 0.6)

        is_fullscreen = self.win.get_properties().fullscreen

        #x = (0.9 + 0.4) / 2
        x = 0.08
        spacing = 0.08
        scale=0.05
        y = 0.51
        btns = []
        btns.append(DirectButton(text='start.', command=self.start_game, parent=self.menu, text_align=core.TextNode.A_left, pos=(x, 0.0, y), scale=scale, text_fg=text_fg, relief=None))
        btns.append(DirectButton(text='windowed.' if is_fullscreen else 'fullscreen.', command=self.toggle_fullscreen, parent=self.menu, text_align=core.TextNode.A_left, pos=(x, 0.0, y-spacing*1), scale=scale, text_fg=text_fg, relief=None))
        btns.append(DirectButton(text='leave.', command=sys.exit, parent=self.menu, text_align=core.TextNode.A_left, pos=(x, 0.0, y-spacing*2), scale=scale, text_fg=text_fg, relief=None))
        self.menu_buttons = btns

    def start_game(self):
        if self.starting:
            return

        self.starting = True

        Sequence(self.menu.colorScaleInterval(1.5, (1, 1, 1, 0)), Func(self.menu.stash)).start()
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

        Parallel(
            LerpFunctionInterval(base.camLens.set_fov, fromData=base.camLens.get_fov(), toData=80),
            base.cam.hprInterval(2, hpr=(0, 0, 0), blendType="easeInOut"),
            base.camera.hprInterval(2, hpr=camera_hpr, blendType="easeInOut"),
            Func(self.finish_starting),
        ).start()

    def finish_starting(self):
        self.started = True
        self.world.activate()
        self.accept('2', self.world.press_2)
        self.accept('3', self.world.press_3)
        self.accept('4', self.world.ending)
        self.accept('p', self.world.print_pos)


    def toggle_fullscreen(self):
        is_fullscreen = self.win.get_properties().fullscreen
        if is_fullscreen:
            print("Disabling fullscreen")
            size = core.WindowProperties.get_default().size
            self.win.request_properties(core.WindowProperties(fullscreen=False, origin=(-2, -2), size=size))
            self.menu_buttons[1]['text'] = 'fullscreen.'
        else:
            print("Enabling fullscreen")
            size = self.pipe.get_display_width(), self.pipe.get_display_height()
            self.win.request_properties(core.WindowProperties(fullscreen=True, size=size))
            self.menu_buttons[1]['text'] = 'windowed.'


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
