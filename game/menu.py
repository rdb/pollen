from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
import direct.gui.DirectGuiGlobals as DGG
from panda3d import core
from direct.interval.IntervalGlobal import Sequence, Func


FADE_TIME = 1.0


class Menu(DirectObject):
    def __init__(self, title, button_defs):
        self.root = base.a2dBottomLeft.attach_new_node("menu")

        self.title = OnscreenText(parent=self.root, text=title, align=core.TextNode.A_left, pos=(0.07, 0.625), scale=0.1, fg=(1, 1, 1, 1))

        text_fg = (1, 1, 1, 0.6)

        #x = (0.9 + 0.4) / 2
        x = 0.08
        spacing = 0.08
        scale=0.05
        y = 0.51
        btns = []
        for text, command in button_defs:
            btns.append(DirectButton(text=text, command=command, parent=self.root, text_align=core.TextNode.A_left, pos=(x, 0.0, y), scale=scale, text_fg=(1, 1, 1, 1), relief=None))
            y -= spacing
        self.buttons = btns

        for i, btn in enumerate(btns):
            btn.set_color_scale(text_fg)
            btn.bind(DGG.ENTER, self._focus_button, [i])
            btn.bind(DGG.EXIT, self._unfocus_button, [i])

        self._selected = None

        self.root.stash()
        self._fade_interval = None

    def _press_down(self, gamepad=False):
        base.assume_gamepad = gamepad
        if self._selected is None:
            self._selected = 0
        else:
            self._unfocus_button(self._selected)
            self._selected = (self._selected + 1) % len(self.buttons)
        self._focus_button(self._selected)
        DGG.getDefaultRolloverSound().play()

    def _press_up(self, gamepad=False):
        base.assume_gamepad = gamepad
        if self._selected is None:
            self._selected = len(self.buttons) - 1
        else:
            self._unfocus_button(self._selected)
            self._selected = (self._selected - 1) % len(self.buttons)
        self._focus_button(self._selected)
        DGG.getDefaultRolloverSound().play()

    def _press_select(self, gamepad=False):
        base.assume_gamepad = gamepad
        if self._selected is None:
            self._press_down()
        else:
            self.buttons[self._selected]['command']()
            DGG.getDefaultClickSound().play()

    def _focus_button(self, i, param=None):
        btn = self.buttons[i]
        btn.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()

    def _unfocus_button(self, i, param=None):
        btn = self.buttons[i]
        btn.colorScaleInterval(0.2, (1, 1, 1, 0.6), blendType='easeInOut').start()

    def show(self):
        self.accept('gamepad-dpad_down', self._press_down, [True])
        self.accept('gamepad-dpad_up', self._press_up, [True])
        self.accept('gamepad-face_a', self._press_select, [True])
        self.accept('arrow_down', self._press_down, [False])
        self.accept('arrow_up', self._press_up, [False])
        self.accept('enter', self._press_select, [False])

        self.root.set_color_scale((1, 1, 1, 0))
        self.root.unstash()

        if self._fade_interval:
            self._fade_interval.pause()

        self._fade_interval = self.root.colorScaleInterval(FADE_TIME, (1, 1, 1, 1))
        self._fade_interval.start()

        if base.assume_gamepad and self.buttons:
            self._selected = 0
            self._focus_button(0)

    def hide(self):
        self.ignoreAll()
        if self._selected is not None:
            self._unfocus_button(self._selected)
            self._selected = None

        if self._fade_interval:
            self._fade_interval.pause()

        self._fade_interval = Sequence(self.root.colorScaleInterval(FADE_TIME, (1, 1, 1, 0)), Func(self.root.stash))
        self._fade_interval.start()
