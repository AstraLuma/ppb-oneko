import ppb
from ppb import Vector
from pathlib import Path
from dataclasses import dataclass


def _find_closest_vector(needle, mapping):
    max_dot = -1e300
    max_value = None
    for hay, value in mapping.items():
        dot = needle * Vector(hay).normalize()
        if dot > max_dot:
            max_dot = dot
            max_value = value

    return max_value


ANIMATIONS = {
    'stop': ['neutral', 'neutral'],
    'fidget': ['fidget', 'neutral'],
    'itch': ['itch1', 'itch2'],
    'yawn': ['yawn', 'yawn'],
    'sleep': ['sleep1', 'sleep2'],
    'awake': ['awake', 'awake'],
    'move:right': ['right1', 'right2'],
    'move:upright': ['upright1', 'upright2'],
    'move:up': ['up1', 'up2'],
    'move:upleft': ['upleft1', 'upleft2'],
    'move:left': ['left1', 'left2'],
    'move:downleft': ['downleft1', 'downleft2'],
    'move:down': ['down1', 'down2'],
    'move:downright': ['downright1', 'downright2'],
    'wall:left': ['left_wall1', 'left_wall2'],
    'wall:right': ['right_wall1', 'right_wall2'],
    'wall:up': ['up_wall1', 'up_wall2'],
    'wall:down': ['down_wall1', 'down_wall2'],
}


SETTINGS = {
    # name: (speed, idle)
    'neko':   (13/32, 0.1875),
    'tora':   (16/32, 0.1875),
    'dog':    (10/32, 0.1875),
    'bsd':    (10/32, 0.1875),  # FIXME: Runs half as fast as the others?
    'sakura': (13/32, 0.1875),
    'tomoyo': (10/32, 0.1875)
}


@dataclass
class NekoTick:
    count: int


class BaseNeko(ppb.BaseSprite):
    # The current character, one of: neko, tora, dog, bsd, sakura, tomoyo
    character = 'neko'
    #: The current pose, one of: stop, fidget, itch, yawn, sleep, awake, move, wall
    pose = 'neutral'

    resource_path = Path(__file__).absolute().parent

    # This overrides facing because there's a bunch of assets for different rotations
    _facing = Vector(1, 0)

    _time_left = 0
    _tick = 0

    #: Tick rate in Hz
    tick_rate = 8

    # We're using our own timer because the 8Hz tick doesn't line up with the 60Hz PPB Update
    # FIXME: Make this a targeted event
    def on_idle(self, event, signal):
        self._time_left -= event.time_delta

        if self._time_left <= 0:
            self._time_left = 1/self.tick_rate
            self._tick += 1
            signal(NekoTick(count=self._tick))

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, value):
        self._facing = value
        self._wall_facing = _find_closest_vector(value, {
            (1, 0): 'right',
            (0, 1): 'up',
            (-1, 0): 'left',
            (0, -1): 'down',
        })
        self._move_facing = _find_closest_vector(value, {
            (1, 0): 'right',
            (1, 1): 'upright',
            (0, 1): 'up',
            (-1, 1): 'upleft',
            (-1, 0): 'left',
            (-1, -1): 'downleft',
            (0, -1): 'down',
            (1, -1): 'downright',
        })

    def on_pre_render(self, event, signal):
        if self.pose == 'move':
            pose = f'move:{self._move_facing}'
        elif self.pose == 'wall':
            pose = f'wall:{self._wall_facing}'
        else:
            pose = self.pose

        if self.pose != 'sleep':
            frame = ANIMATIONS[pose][self._tick & 0x1]
        else:
            frame = ANIMATIONS[pose][(self._tick >> 2) & 0x1]

        self.image = f'{self.character}/{frame}.png'


class LivingNeko(BaseNeko):
    state_count = 0
    target = Vector(0, 0)
    _state = 'stop'

    prev_target = Vector(0, 0)
    prev_position = Vector(0, 0)

    window_left = window_right = window_top = window_bottom = 0

    STOP_TIME = 4
    FIDGET_TIME = 10
    ITCH_TIME = 4
    YAWN_TIME = 6
    AWAKE_TIME = 3
    WALL_SCRATCH_TIME = 10

    resource_path = Path(__file__).absolute().parent

    @property
    def speed(self):
        speed, idle = SETTINGS[self.character]
        return speed

    @property
    def idle_space(self):
        speed, idle = SETTINGS[self.character]
        return idle

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            print("Set state:", value)
        self._state = value
        self.state_count = 0

    def on_update(self, event, signal):
        cam = event.scene.main_camera

        self.window_left = cam.frame_left
        self.window_right = cam.frame_right
        self.window_top = cam.frame_top
        self.window_bottom = cam.frame_bottom

    def clamp_to_frame(self):
        """
        Limit us to the current frame, returning True if clamping happened.
        """
        rv = False
        if self.bottom <= self.window_bottom:
            self.bottom = self.window_bottom
            rv = True
        elif self.top >= self.window_top:
            self.top = self.window_top
            rv = True
        if self.left <= self.window_left:
            self.left = self.window_left
            rv = True
        elif self.right >= self.window_right:
            self.right = self.window_right
            rv = True

        return rv

    def will_not_move(self):
        return self.position == self.prev_position

    def should_start_moving(self, delta):
        if delta.length > self.idle_space:
            return True

    def calc_movement(self):
        """
        Calculate our movement
        """
        delta = self.target - self.position
        if delta:
            if delta.length <= self.speed:
                move = delta
            else:
                move = delta.scale_to(self.speed)
        else:
            move = Vector(0, 0)
        return move

    def on_neko_tick(self, event, signal):
        if event.count % 2 == 0:
            self.state_count += 1

        self.run_state_machine()
        self.prev_target = self.target
        self.prev_position = self.position

    def run_state_machine(self):
        move_delta = self.calc_movement()

        self.facing = move_delta
        self.pose = self.state

        if self.state == 'stop':
            if self.should_start_moving(move_delta):
                self.state = 'awake'
            elif self.state_count < self.STOP_TIME:
                pass
            elif move_delta and self.clamp_to_frame():  # Side-effect: might move self
                self.state = 'wall'
            else:
                self.state = 'fidget'

        elif self.state == 'fidget':
            if self.should_start_moving(move_delta):
                self.state = 'awake'
            elif self.state_count < self.FIDGET_TIME:
                pass
            else:
                self.state = 'itch'

        elif self.state == 'itch':
            if self.should_start_moving(move_delta):
                self.state = 'awake'
            elif self.state_count < self.ITCH_TIME:
                pass
            else:
                self.state = 'yawn'

        elif self.state == 'yawn':
            if self.should_start_moving(move_delta):
                self.state = 'awake'
            elif self.state_count < self.YAWN_TIME:
                pass
            else:
                self.state = 'sleep'

        elif self.state == 'sleep':
            if self.should_start_moving(move_delta):
                self.state = 'awake'

        elif self.state == 'awake':
            if self.state_count < self.AWAKE_TIME:
                pass
            else:
                self.state = 'move'

        elif self.state == 'move':
            self.position += move_delta
            if not move_delta:
                self.state = 'stop'
            elif self.clamp_to_frame():
                if self.will_not_move():
                    # Really, we were clamped this tick and last
                    self.state = 'stop'

        elif self.state == 'wall':
            if self.should_start_moving(move_delta):
                self.state = 'awake'
            elif self.state_count < self.WALL_SCRATCH_TIME:
                pass
            else:
                self.state = 'itch'

        else:
            # Shouldn't happen
            self.state = 'stop'
