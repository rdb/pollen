from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
import direct.gui.DirectGuiGlobals as DGG
from panda3d import core
from direct.interval.IntervalGlobal import Sequence, Func


class Menu:
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

        self.root.stash()

    def _focus_button(self, i, param):
        btn = self.buttons[i]
        btn.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()

    def _unfocus_button(self, i, param):
        btn = self.buttons[i]
        btn.colorScaleInterval(0.2, (1, 1, 1, 0.6), blendType='easeInOut').start()

    def show(self):
        self.root.set_color_scale((1, 1, 1, 0))
        self.root.unstash()
        self.root.colorScaleInterval(1.5, (1, 1, 1, 1)).start()

    def hide(self):
        Sequence(self.root.colorScaleInterval(1.5, (1, 1, 1, 0)), Func(self.root.stash)).start()
