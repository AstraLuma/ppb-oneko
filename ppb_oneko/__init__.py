import ppb
from ppb import Vector
from pathlib import Path


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
    # name: (speed, idle, time)
    'neko':   (13/32, 0.1875, 0.125),
    'tora':   (16/32, 0.1875, 0.125),
    'dog':    (10/32, 0.1875, 0.125),
    'bsd':    (10/32, 0.1875, 0.25),
    'sakura': (13/32, 0.1875, 0.125),
    'tomoyo': (10/32, 0.1875, 0.125)
}


class LivingNeko(ppb.BaseSprite):
    character = 'neko'

    tick_count = 0
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

    MAX_TICK = 9999  # Odd only

    resource_path = Path(__file__).absolute().parent

    @property
    def speed(self):
        speed, idle, time = SETTINGS[self.character]
        return speed

    @property
    def idle_space(self):
        speed, idle, time = SETTINGS[self.character]
        return idle

    @property
    def interval_time(self):
        speed, idle, time = SETTINGS[self.character]
        return time

    def _update_window(self, cam):
        self.window_left = cam.frame_left
        self.window_right = cam.frame_right
        self.window_top = cam.frame_top
        self.window_bottom = cam.frame_bottom

    def _animation(self):
        if self.state != 'sleep':
            frame = ANIMATIONS[self.state][self.tick_count & 0x1]
        else:
            frame = ANIMATIONS[self.state][(self.tick_count >> 2) & 0x1]

        self.image = f'{self.character}/{frame}.png'

    def increment_tick(self):
        self.tick_count += 1

        if self.tick_count >= self.MAX_TICK:
            self.tick_count = 0

        if self.tick_count % 2 == 0:
            if self.state_count < self.MAX_TICK:
                self.state_count += 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            print("Set state:", value)
        self._state = value
        self.tick_count = 0
        self.state_count = 0

    def direction(self, move_delta):
        if move_delta == (0, 0):
            new_state = 'stop'
        else:
            new_state = _find_closest_vector(move_delta, {
                (1, 0): 'move:right',
                (1, 1): 'move:upright',
                (0, 1): 'move:up',
                (-1, 1): 'move:upleft',
                (-1, 0): 'move:left',
                (-1, -1): 'move:downleft',
                (0, -1): 'move:down',
                (1, -1): 'move:downright',
            })

        if self.state != new_state:
            self.state = new_state

    def is_window_over(self):
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

    def is_dont_move(self):
        return self.position == self.prev_position

    def is_move_start(self):
        if (self.target - self.prev_target).length > self.idle_space:
            return True

    def calc_dx_dy(self):
        """
        Calculate distance to target
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

    def think_draw(self):
        move_delta = self.calc_dx_dy()

        self._animation()

        self.increment_tick()

        if self.state == 'stop':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.STOP_TIME:
                pass
            elif move_delta.x < 0 and self.left <= self.window_left:
                self.state = 'wall:left'
            elif move_delta.x > 0 and self.right >= self.window_right:
                self.state = 'wall:right'
            elif move_delta.y > 0 and self.top >= self.window_top:  # Omitting some ToFocus behavior
                self.state = 'wall:up'
            elif move_delta.y < 0 and self.bottom <= self.window_bottom:  # Omitting some ToFocus behavior
                self.state = 'wall:down'
            else:
                self.state = 'fidget'

        elif self.state == 'fidget':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.FIDGET_TIME:
                pass
            else:
                self.state = 'itch'

        elif self.state == 'itch':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.ITCH_TIME:
                pass
            else:
                self.state = 'yawn'

        elif self.state == 'yawn':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.YAWN_TIME:
                pass
            else:
                self.state = 'sleep'

        elif self.state == 'sleep':
            if self.is_move_start():
                self.state = 'awake'

        elif self.state == 'awake':
            if self.state_count < self.AWAKE_TIME:
                pass
            else:
                self.direction(move_delta)

        elif self.state.startswith('move:'):
            self.position += move_delta
            self.direction(move_delta)
            if self.is_window_over():
                if self.is_dont_move():
                    self.state = 'stop'

        elif self.state.startswith('wall:'):
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.WALL_SCRATCH_TIME:
                pass
            else:
                self.state = 'itch'

        else:
            # Shouldn't happen
            self.state = 'stop'

    _time_left = 0

    # We're using our own timer because the 8Hz tick doesn't line up with the 60Hz PPB Update
    def on_idle(self, event, signal):
        self._update_window(event.scene.main_camera)

        self._time_left -= event.time_delta

        if self._time_left <= 0:
            self.think_draw()
            self._time_left = self.interval_time
            self.prev_target = self.target
            self.prev_position = self.position


    def on_mouse_motion(self, event, signal):
        self.target = event.position


if __name__ == '__main__':
    def setup(scene):
        scene.add(LivingNeko)

    ppb.run(setup)