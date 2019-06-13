import ppb
from ppb_oneko import LivingNeko


class MouseNeko(LivingNeko):
    def on_mouse_motion(self, event, signal):
        self.target = event.position


def setup(scene):
    scene.add(MouseNeko())
    scene.main_camera.pixel_ratio = 32


ppb.run(setup)
