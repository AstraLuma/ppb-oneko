import ppb
from ppb import Vector
from pathlib import Path

__all__ = 'Neko',


def _find_closest_vector(needle, mapping):
    max_dot = -99999
    max_value = None
    for hay, value in mapping.items():
        dot = needle * hay
        if dot > max_dot:
            max_dot = dot
            max_value = value

    return max_value


class NekoPuppet(ppb.BaseSprite):
    character = 'neko'

    resource_path = Path(__file__).absolute().parent

    def fall_asleep(self):
        ...

    def fidget(self):
        ...

    def move_in(self, direction):
        pose = _find_closest_vector(direction, {
            Vector(1, 0): 'right',
            Vector(1, 1): 'upright',
            Vector(0, 1): 'up',
            Vector(-1, 1): 'upleft',
            Vector(-1, 0): 'left',
            Vector(-1, -1): 'downleft',
            Vector(0, -1): 'down',
            Vector(1, -1): 'downright',
        })
        ...

    def hit_wall(self, direction):
        pose = _find_closest_vector(direction, {
            Vector(1, 0): 'right_wall',
            Vector(0, 1): 'up_wall',
            Vector(-1, 0): 'left_wall',
            Vector(0, -1): 'down_wall',
        })
        ...

    @property
    def image(self):
        ...


MAX_TICK = 9999  # Odd only


class LivingNeko(ppb.BaseSprite):
    tick_count = 0
    state_count = 0
    target = Vector(0, 0)
    _state = 'idle'

    # Character configuration
    speed = 0
    idle_space = 0

    STOP_TIME = 0
    JARE_TIME = 0
    KAKI_TIME = 0
    AKUBI_TIME = 0

    def tick_count(self):
        self.tick_count += 1

        if self.tick_count >= MAX_TICK:
            self.tick_count = 0

        if self.tick_count % 2 == 0:
            if self.state_count < MAX_TICK:
                self.state_count += 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.tick_count = 0
        self.state_count = 0

    def direction(self, move_delta):
        if move_delta == (0, 0):
            new_state = 'stop'  # TODO: idle?
        else:
            new_state = _find_closest_vector(move_delta, {
                Vector(1, 0): 'right',
                Vector(1, 1): 'upright',
                Vector(0, 1): 'up',
                Vector(-1, 1): 'upleft',
                Vector(-1, 0): 'left',
                Vector(-1, -1): 'downleft',
                Vector(0, -1): 'down',
                Vector(1, -1): 'downright',
            })

        if self.state != new_state:
            self.state = new_state

    def is_window_over(self):
        # EH? This is clearly clamping the position, but I'm not sure to what.
        rv = False
        if self.bottom <= 0:
            self.bottom = 0
            rv = True
        elif self.top >= WindowHeight:
            self.top = WindowHeight
            rv = True
        if self.left <= 0:
            self.left = 0
            rv = True
        elif self.right >= WindowWidth:
            self.right = WindowWidth
            rv = True

        return rv

    def is_dont_move(self):
        return self.position == self.last_position

    def is_move_start(self):
        if (self.target - self.prev_target).length > self.idle_spacee:
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

        if self.state != 'sleep':
            self.image = ANIMATION[self.state][self.tick_count & 0x1]
        else:
            self.image = ANIMATION[self.state][(self.tick_count >> 2) & 0x1]

        self.tick_count()

        if self.state == 'stop':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < STOP_TIME:
                pass
            elif move_delta.x < 0 and self.position.x <= 0:
                self.state = NEKO_L_TOGI
            elif move_delta.x > 0 and self.position.x >= 0:
                self.state = NEKO_R_TOGI
            elif move_delta.y > 0 and self.top >= WindowHeight:  # Omitting some ToFocus behavior
                self.state = NEKO_U_TOGI
            elif move_delta.y < 0 and self.bottom <= 0:
                self.state = NEKO_D_TOGI
            else:
                self.state = NEKO_JARE

        elif self.state == NEKO_JARE:
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.JARE_TIME:
                pass
            else:
                self.state = NEKO_KAKI

        elif self.state == NEKO_KAKI:
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.KAKI_TIME:
                pass
            else:
                self.state = NEKO_AKUBI

        elif self.state == NEKO_AKUBI:
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.AKUBI_TIME:
                pass
            else:
                self.state = 'sleep'

        elif self.state == 'sleep':
            if self.is_move_start():
                self.state = 'awake'

        elif self.state == 'awake':
            if self.state_count < self.AWAKE_TIME:
                pass
            self.direction(move_delta)

        elif self.state == 'move':
            self.position += move_delta
            self.direction(move_delta)
            if self.is_window_over():
                if self.is_dont_move():
                    self.state = 'stop'

        elif self.state == 'togi':
            if self.is_move_start():
                self.state = 'awake'
            elif self.state_count < self.TOGI_TIME:
                pass
            self.state = NEKO_KAKI

        else:
            # Shouldn't happen
            self.state = 'stop'
