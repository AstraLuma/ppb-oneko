import ppb
from ppb_oneko import LivingNeko


def setup(scene):
    scene.add(LivingNeko())
    scene.main_camera.pixel_ratio = 32


ppb.run(setup)
