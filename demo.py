import ppb
import ppb.keycodes as kc
from ppb import Vector
from ppb.events import ReplaceScene
from ppb.features.animation import Animation

ANIMATED = {
    'down', 'downleft', 'downright', 'down_wall', 'itch', 'left', 'left_wall',
    'right', 'right_wall', 'sleep', 'up', 'upleft', 'upright', 'up_wall',
}


class Neko(ppb.BaseSprite):
    character = 'neko'

    @property
    def pose(self):
        return vars(self)['pose']

    @pose.setter
    def pose(self, value):
        vars(self)['pose'] = value

        if value in ANIMATED:
            self.image = Animation(f"ppb_oneko/{self.character}/{value}{{1..2}}.png", frames_per_second=6)
        else:
            self.image = f"ppb_oneko/{self.character}/{value}.png"


class NekoScene(ppb.BaseScene):
    character = 'neko'

    def __init__(self, **args):
        super().__init__(**args)

        cam = self.main_camera
        cam.pixel_ratio = 32
        self.add(Neko(character=self.character, pose='neutral', position=( 0,  0)))
        self.add(Neko(character=self.character, pose='cursor',  position=( 1,  0)))
        self.add(Neko(character=self.character, pose='idle_a',  position=(-1, -1)))
        self.add(Neko(character=self.character, pose='yawn',    position=( 0, -1)))
        self.add(Neko(character=self.character, pose='awake',   position=( 1, -1)))
        self.add(Neko(character=self.character, pose='itch',    position=( 0,  1)))
        self.add(Neko(character=self.character, pose='sleep',    position=( 1,  1)))

        self.add(Neko(character=self.character, pose='up', position=(0, cam.frame_top / 2)))
        self.add(Neko(character=self.character, pose='down', position=(0, cam.frame_bottom / 2)))
        self.add(Neko(character=self.character, pose='left', position=(cam.frame_left / 2, 0)))
        self.add(Neko(character=self.character, pose='right', position=(cam.frame_right / 2, 0)))
        self.add(Neko(character=self.character, pose='upright', position=(cam.frame_right / 2, cam.frame_top / 2)))
        self.add(Neko(character=self.character, pose='upleft', position=(cam.frame_left / 2, cam.frame_top / 2)))
        self.add(Neko(character=self.character, pose='downright', position=(cam.frame_right / 2, cam.frame_bottom / 2)))
        self.add(Neko(character=self.character, pose='downleft', position=(cam.frame_left / 2, cam.frame_bottom / 2)))

        self.add(Neko(character=self.character, pose='up_wall',    position=Vector(0, cam.frame_top - 0.5)))
        self.add(Neko(character=self.character, pose='down_wall',  position=Vector(0, cam.frame_bottom + 0.5)))
        self.add(Neko(character=self.character, pose='left_wall',  position=Vector(cam.frame_left + 0.5, 0)))
        self.add(Neko(character=self.character, pose='right_wall', position=Vector(cam.frame_right - 0.5, 0)))

    def on_key_pressed(self, event, signal):
        if event.key is kc.B:
            signal(ReplaceScene(NekoScene(character='bsd')))
        elif event.key is kc.D:
            signal(ReplaceScene(NekoScene(character='dog')))
        elif event.key is kc.N and event.mods == {kc.ShiftLeft}:
            signal(ReplaceScene(NekoScene(character='tora')))
        elif event.key is kc.N:
            signal(ReplaceScene(NekoScene(character='neko')))
        elif event.key is kc.S:
            signal(ReplaceScene(NekoScene(character='sakura')))
        elif event.key is kc.T:
            signal(ReplaceScene(NekoScene(character='tomoyo')))


ppb.run(starting_scene=NekoScene)
