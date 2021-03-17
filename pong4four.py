"""
 Pong4four by aLaix

 TODO:
 EL chequeo de colisiones esta en absoluto y se ocupa pasar a relativo al tiempo, osea
  multiplicar por delta
"""
import array
import collections
import math
import random

import pygame

SCREEN_W = 800
SCREEN_H = 600


class Sprite:
    def __init__(self, x, y, w, h, color):
        self._x, self._y = x, y
        self._gx, self._gy = x, y
        self.w = w
        self.h = h
        self.color = color
        self._vx, self._vy = 0, 0
        self._dvx, self._dvy = 0, 0
        self._delta = float(1) / 30
        self._touched_left_event = None
        self._touched_right_event = None
        self._touched_up_event = None
        self._touched_down_event = None
        self.active = True

    def setx(self, x):
        self._x = x
        self._gx = x

    def sety(self, y):
        self._y = y
        self._gy = y

    def setvx(self, vx):
        self._vx = vx
        self._dvx = self._delta * vx

    def setvy(self, vy):
        self._vy = vy
        self._dvy = self._delta * vy

    def getx(self):
        return self._x

    def gety(self):
        return self._y

    def getvx(self):
        return self._vx

    def getvy(self):
        return self._vy

    x = property(getx, setx)
    y = property(gety, sety)
    vx = property(getvx, setvx)
    vy = property(getvy, setvy)

    def moveto(self, x, y):
        self.x, self.y = x, y

    def move_vel(self, vx, vy):
        self.vx, self.vy = vx, vy

    def update_pos(self):
        if self.active:
            rect = self._getrect()
            if rect[0] + self._dvx < 0:
                if self._touched_left_event:
                    self._touched_left_event(self)
            elif rect[2] + self._dvx >= SCREEN_W:
                if self._touched_right_event:
                    self._touched_right_event(self)
            elif rect[1] + self._dvy < 0:
                if self._touched_up_event:
                    self._touched_up_event(self)
            elif rect[3] + self._dvy >= SCREEN_H:
                if self._touched_down_event:
                    self._touched_down_event(self)
            self.x, self.y = self.x + self._dvx, self.y + self._dvy
            # print(self._dvx, self._dvy)

    def interpolate(self, screen):
        delta = 0
        self._gx += self.vx * delta
        self._gy += self.vy * delta
        self.draw(screen)

    def draw(self, screen):
        if self.active:
            w2, h2 = self.w / 2, self.h / 2
            pygame.draw.rect(screen, self.color, (self._gx - w2, self._gy - h2, self.w, self.h))
            # print(self.vx, self.vy)

    def _getrect(self):
        w2, h2 = self.w / 2, self.h / 2
        return self.x - w2, self.y - h2, self.x + w2, self.y + h2

    def collide(self, sprite: 'Sprite'):
        if self.active:
            if sprite.active:
                sprect = sprite._getrect()
                rect = self._getrect()
                return rect[2] >= sprect[0] and rect[3] >= sprect[1] and \
                    sprect[2] >= rect[0] and sprect[3] >= rect[1]

    def set_touched_left_event(self, func):
        self._touched_left_event = func

    def set_touched_right_event(self, func):
        self._touched_right_event = func

    def set_touched_up_event(self, func):
        self._touched_up_event = func

    def set_touched_down_event(self, func):
        self._touched_down_event = func


class Player(Sprite):
    def __init__(self, x, y, is_vertical, color, game):
        self.left, self.right, self.up, self.down = None, None, None, None
        self.is_vertical = is_vertical
        self.game = game
        if is_vertical:
            w, h = self.game.PADDLE_HEIGHT, self.game.PADDLE_WIDTH
        else:
            w, h = self.game.PADDLE_WIDTH, self.game.PADDLE_HEIGHT
        Sprite.__init__(self, x, y, w, h, color)
        self.vel = self.game.PADDLE_VEL
        self.lives = self.game.LIVES
        self.set_touched_left_event(self.limit_left)
        self.set_touched_right_event(self.limit_right)
        self.set_touched_up_event(self.limit_up)
        self.set_touched_down_event(self.limit_down)
        self.keysbuffer = collections.deque()
        self.joy_is_center = False
        self.counters = (Counter0(game, self), Counter1(game, self), Counter2(game, self),
                         Counter3(game, self), Counter4(game, self), Counter5(game, self))

    def leftpressed(self):
        self.vx = -self.vel
        self.keysbuffer.append('1')
        self._checkcounters()

    def rightpressed(self):
        self.vx = self.vel
        self.keysbuffer.append('0')
        self._checkcounters()

    def uppressed(self):
        self.vy = -self.vel
        self.keysbuffer.append('0')
        self._checkcounters()

    def downpressed(self):
        self.vy = self.vel
        self.keysbuffer.append('1')
        self._checkcounters()

    def keyup(self):
        self.vx, self.vy = 0, 0

    def leftup(self):
        if self.keysbuffer[-1] == '1':
            self.keyup()

    def rightup(self):
        if self.keysbuffer[-1] == '0':
            self.keyup()

    def upup(self):
        if self.keysbuffer[-1] == '0':
            self.keyup()

    def downup(self):
        if self.keysbuffer[-1] == '1':
            self.keyup()

    def joy(self, x, y):
        if self.is_vertical:
            if y > 0.5:
                if self.joy_is_center:
                    self.joy_is_center = False
                    self.downpressed()
            elif y < -0.5:
                if self.joy_is_center:
                    self.joy_is_center = False
                    self.uppressed()
            else:
                self.vy = 0
                self.joy_is_center = True
        else:
            if x > 0.5:
                if self.joy_is_center:
                    self.joy_is_center = False
                    self.rightpressed()
            elif x < -0.5:
                if self.joy_is_center:
                    self.joy_is_center = False
                    self.leftpressed()
            else:
                self.vx = 0
                self.joy_is_center = True
        # self.move_vel(x * self.vel, y * self.vel)

    def limit_left(self, x):
        x.x, x.vx = self.w / 2, 0

    def limit_right(self, x):
        x.x, x.vx = SCREEN_W - self.w / 2, 0

    def limit_up(self, x):
        x.y, x.vy = self.h / 2, 0

    def limit_down(self, x):
        x.y, x.vy = SCREEN_H - self.h / 2, 0

    def die(self):
        active = self.active
        if active:
            self.lives -= 1
            if self.lives <= 0:
                self.active = False
        return active

    def _checkcounters(self):
        if len(self.keysbuffer) > 8:
            self.keysbuffer.popleft()
        cur_counter = ''.join(self.keysbuffer)
        try:
            counter = self.game.countercombos[cur_counter]
            self.counters[counter].start()
        except KeyError:
            length = len(cur_counter)
            if length > 6:
                cur_counter_len6 = cur_counter[length - 6:]
                try:
                    counter = self.game.countercombos[cur_counter_len6]
                    self.counters[counter].start()
                except KeyError:
                    pass

    def run(self):
        for counter in self.counters:
            counter.run()
        self.update_pos()


class Pelota(Sprite):
    def __init__(self, x, y, w, h, color, vel):
        super(Pelota, self).__init__(x, y, w, h, color)
        self._check_collisions = []
        self.move_vel(math.cos(math.radians(45)), math.sin(math.radians(45)))
        self.vel = vel
        self.colliding = False
        self.collided_event = None

    def setvel(self, vel):
        self._vel = vel
        self.set_direction(self.vx, self.vy)

    def getvel(self):
        return self._vel

    vel = property(getvel, setvel)

    def update_pos(self):
        for sprite in self._check_collisions:
            if self.collide(sprite):
                if not self.colliding:
                    self.colliding = True
                    if self.collided_event:
                        self.collided_event(self, sprite)
                break
        else:
            self.colliding = False
        Sprite.update_pos(self)
        # self.moveto(self.x + self.vx, self.y + self.vy)

    def check_append(self, sprite):
        self._check_collisions.append(sprite)

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy

    def set_collided_event(self, func):
        self.collided_event = func

    def set_direction(self, dirx, diry):
        length = math.sqrt(dirx ** 2 + diry ** 2)
        self.move_vel(dirx * self._vel / length, diry * self._vel / length)


class Counter:
    def __init__(self, game, player):
        self.game = game
        self.player = player


class Counter0(Counter):
    def __init__(self, game, player):
        super(Counter0, self).__init__(game, player)
        self.time = 0

    def start(self):
        print('COUNTER0')
        if self.player.active:
            self.time = 1

    def run(self):
        if self.time:
            if self.time == 1:
                if self.player.is_vertical:
                    self.player.h = self.game.BIG_PADDLE
                else:
                    self.player.w = self.game.BIG_PADDLE
            if self.time < self.game.COUNTER_TIME:
                self.time += 1
            else:
                if self.player.is_vertical:
                    self.player.h = self.game.PADDLE_WIDTH
                else:
                    self.player.w = self.game.PADDLE_WIDTH
                self.time = 0


class Counter1(Counter):
    def __init__(self, game, player):
        super(Counter1, self).__init__(game, player)
        self.time = 0

    def start(self):
        print('COUNTER1')
        if self.player.active:
            self.time = 1

    def run(self):
        if self.time:
            if self.time == 1:
                self.player.vel = int(self.game.PADDLE_VEL * 2.5)
            if self.time < self.game.COUNTER_TIME:
                self.game.bgcolor = random.choice(self.game.color_palette[1:-1])
                self.game.fps = self.game.FPS / 2
                self.time += 1
            else:
                self.game.bgcolor = self.game.color_palette[0]
                self.game.fps = self.game.FPS
                self.time = 0
                self.player.vel = self.game.PADDLE_VEL


class Counter2(Counter):
    def __init__(self, game, player):
        super(Counter2, self).__init__(game, player)
        self.time = 0

    def start(self):
        print('COUNTER2')
        if self.player.active:
            self.time = 1

    def run(self):
        if self.time:
            if self.time == 1:
                self.game.cuadro.w = SCREEN_W - self.game.PADDLE_WIDTH * 2
                self.game.cuadro.h = SCREEN_H - self.game.PADDLE_WIDTH * 2
            if self.time < self.game.COUNTER_TIME * 2:
                self.time += 1
            else:
                self.game.cuadro.w = self.game.PADDLE_WIDTH
                self.game.cuadro.h = self.game.PADDLE_WIDTH
                self.time = 0


class Counter3(Counter):
    def __init__(self, game, player):
        super(Counter3, self).__init__(game, player)
        self.state = 0
        self.backup_color = self.player.color

    def start(self):
        print('COUNTER3')
        self.state = 1

    def run(self):
        if self.state:
            if self.state == 1:
                self.player.color = random.choice(self.game.color_palette[1:])
            if self.state == 2:
                self.game.pelota.color = random.choice(self.game.color_palette[1:])

    def start_pelota(self):
        self.player.color = self.backup_color
        self.game.pelota.vel *= 3
        self.state = 2

    def stop_pelota(self):
        self.game.pelota.color = self.game.COLOR_PELOTA
        self.game.pelota.vel = self.game.PELOTA_VEL
        if self.state == 2:
            self.state = 0


class Counter4(Counter):
    def __init__(self, game, player):
        super(Counter4, self).__init__(game, player)

    def start(self):
        print('COUNTER4')
        self.player.lives += 1
        self.player.active = True

    def run(self):
        pass


class Counter5(Counter):
    def __init__(self, game, player):
        super(Counter5, self).__init__(game, player)
        self.time = 0

    def start(self):
        print('COUNTER5')
        self.time = 1

    def run(self):
        if self.time:
            print('RUN')
            if self.time % 5 == 0:
                num = 40
                particles = [Sprite(self.player.x, self.player.y, 20, 20, (0, 255, 255)) for _ in range(num)]
                for i, p in enumerate(particles):
                    angle = i * 360.0 / num
                    p.move_vel(math.cos(math.radians(angle)) * 300,
                               math.sin(math.radians(angle)) * 300)
                    p.set_touched_down_event(self.game.particles.remove)
                    p.set_touched_up_event(self.game.particles.remove)
                    p.set_touched_left_event(self.game.particles.remove)
                    p.set_touched_right_event(self.game.particles.remove)
                self.game.particles.extend(particles)
            if self.time < self.game.COUNTER_TIME:
                self.time += 1
            else:
                self.time = 0


SAMPLE_RATE = 44100
BITS = 16


def square_wave(freq, volume=25000):
    period = int(round(SAMPLE_RATE / freq))
    samples = array.array('h',
                          (volume if time < period / 2 else -volume
                           for time in range(period))
                          )
    return samples


def make_sound(arr):
    return pygame.sndarray.make_sound(arr)


def make_square_wave(freq=1000):
    return make_sound(square_wave(freq))


class Sound:
    def __init__(self):
        self.active_sound = None
        self.frames_to_finish = 0
        self.bounce_sound = make_square_wave(1000)
        self.die_sound = make_square_wave(125)

    def run(self):
        if self.frames_to_finish:
            self.frames_to_finish -= 1
            if self.frames_to_finish == 0:
                self.active_sound.stop()

    def bounce(self):
        if self.active_sound:
            self.active_sound.stop()
        self.active_sound = self.bounce_sound
        self.active_sound.play(loops=-1)
        self.frames_to_finish = 6

    def die(self):
        if self.active_sound:
            self.active_sound.stop()
        self.active_sound = self.die_sound
        self.active_sound.play(loops=-1)
        self.frames_to_finish = 6


class Game:
    def __init__(self):
        self.cuadro = None
        self.particles = []
        self.pelota = None
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.players = None
        self.gaming = True
        self.running = True
        self.exe_counters = []
        pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-BITS, channels=1)
        pygame.init()
        self.sound = Sound()
        self.color_palette = ((0, 0, 0),
                              (0, 0, 170),
                              (0, 170, 0),
                              (0, 170, 170),
                              (170, 0, 0),
                              (170, 0, 170),
                              (170, 85, 0),
                              (170, 170, 170),
                              (85, 85, 85),
                              (85, 85, 255),
                              (85, 255, 85),
                              (85, 255, 255),
                              (255, 85, 85),
                              (255, 85, 255),
                              (255, 255, 85),
                              (255, 255, 255)
                              )
        self.countercombos = {'000111': 0,  # barra crece
                              '11001010': 1,  # slo motion
                              '01110100': 2,  # cuadro crece
                              '11100100': 3,  # barra brilla y cuando toca la pelota sale rapida
                              '01101001': 4,  # revivir
                              '10010111': 5,  # estorbo
                              # '01101011': 6   # muchas pelotas
                              }
        self.PADDLE_WIDTH = 100
        self.PADDLE_HEIGHT = 25
        self.COUNTER_TIME = 200
        self.BIG_PADDLE = 200
        self.PADDLE_VEL = 500
        self.PELOTA_VEL = 300
        self.LIVES = 3
        self.FPS = 30
        self.fps = self.FPS
        self.COLOR_PADDLE = (0, 128, 255)
        self.COLOR_PELOTA = (255, 255, 255)
        self.screen = None
        self.bgcolor = (0, 0, 0)

    def pelota_collided(self, pelota, sprite):
        self.sound.bounce()
        if sprite is self.cuadro:
            nx, ny = random.random() - 0.5, random.random() - 0.5
        else:
            nx, ny = pelota.x - sprite.x, pelota.y - sprite.y
        pelota.set_direction(nx, ny)
        for p in self.players:
            if sprite == p and p.counters[3].state == 1:
                p.counters[3].start_pelota()

    def particle_delete(self, x):
        self.particles.remove(x)

    def particle_explosion(self, x):
        particles = [Sprite(x.x, x.y, 20, 20, (255, 0, 0)) for _ in range(40)]
        for p in particles:
            p.move_vel((random.random() - 0.5) * 200, (random.random() - 0.5) * 200)
            p.set_touched_down_event(self.particles.remove)
            p.set_touched_up_event(self.particles.remove)
            p.set_touched_left_event(self.particles.remove)
            p.set_touched_right_event(self.particles.remove)
        return particles

    def die_p1(self, _):
        self.die(self.p1, self.pelota.bounce_y)

    def die_p2(self, _):
        self.die(self.p2, self.pelota.bounce_x)

    def die_p3(self, _):
        self.die(self.p3, self.pelota.bounce_y)

    def die_p4(self, _):
        self.die(self.p4, self.pelota.bounce_x)

    def die(self, player, bounce_func):
        if player.die():
            self.sound.die()
            self.particles.extend(self.particle_explosion(player))
            for p in self.players:
                p.counters[3].stop_pelota()
            p_winner = -1
            total_active_players = 0
            for i, p in enumerate(self.players):
                if p.active:
                    p_winner = i
                    total_active_players += 1
            if total_active_players == 1:
                self.winner(p_winner)
        else:
            self.sound.bounce()
        bounce_func()

    def winner(self, player):
        self.screen.fill(self.bgcolor)
        if self.sound.active_sound:
            self.sound.active_sound.stop()
        font = pygame.font.SysFont("couriernew", 32)
        text = font.render('Ganador jugador numero {}'.format(player + 1), True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_W / 2 - text.get_width() / 2, 260))
        pygame.display.flip()
        while self.gaming:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gaming = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_RETURN:
                        return

    def menu(self, clock):
        self.screen.fill(self.bgcolor)
        if self.sound.active_sound:
            self.sound.active_sound.stop()
        font = pygame.font.SysFont("couriernew", 32)
        title = font.render('Pong4four by ZSEDCX', True, (0, 128, 255))
        choice = 0

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gaming = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.gaming = False
                        self.running = False
                    elif event.key == pygame.K_UP:
                        if choice == 1:
                            choice = 0
                    elif event.key == pygame.K_DOWN:
                        if choice == 0:
                            choice = 1
                    elif event.key == pygame.K_RETURN:
                        if choice == 1:
                            self.gaming = False
                            self.running = False
                        else:
                            self.gaming = True
                        return

            if choice == 0:
                color_start = random.choice(self.color_palette[1:])
                color_exit = (255, 255, 255)
            else:
                color_exit = random.choice(self.color_palette[1:])
                color_start = (255, 255, 255)
            start_text = font.render('Start', True, color_start)
            exit_text = font.render('Exit', True, color_exit)

            self.screen.blit(title, (SCREEN_W / 2 - title.get_width() / 2, 200))
            self.screen.blit(start_text, (SCREEN_W / 2 - start_text.get_width() / 2, 230))
            self.screen.blit(exit_text, (SCREEN_W / 2 - exit_text.get_width() / 2, 260))
            pygame.display.flip()
            clock.tick(10)

    def main(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))  # , pygame.FULLSCREEN)
        pygame.display.set_caption("Pong4Four")
        self.gaming = True
        clock = pygame.time.Clock()

        # Count the joysticks the computer has
        joystick_count = pygame.joystick.get_count()
        if joystick_count >= 1:
            joy0 = pygame.joystick.Joystick(0)
            joy0.init()
        if joystick_count >= 2:
            joy1 = pygame.joystick.Joystick(1)
            joy1.init()
        if joystick_count >= 3:
            joy2 = pygame.joystick.Joystick(2)
            joy2.init()
        if joystick_count >= 4:
            joy3 = pygame.joystick.Joystick(3)
            joy3.init()

        while self.running:
            self.particles = []

            self.p1 = Player(400, 600 - 25, False, self.COLOR_PADDLE, self)
            self.p1.left = pygame.K_LEFT
            self.p1.right = pygame.K_RIGHT

            self.p2 = Player(800 - 25, 300, True, self.COLOR_PADDLE, self)
            self.p2.up = pygame.K_DELETE
            self.p2.down = pygame.K_BACKSPACE

            self.p3 = Player(400, 25, False, self.COLOR_PADDLE, self)
            self.p3.left = pygame.K_h
            self.p3.right = pygame.K_j

            self.p4 = Player(25, 300, True, self.COLOR_PADDLE, self)
            self.p4.up = pygame.K_q
            self.p4.down = pygame.K_a

            self.players = (self.p1, self.p2, self.p3, self.p4)

            self.cuadro = Sprite(400, 300, 101, 101, (128, 128, 128))
            self.cuadro.framecount = 0

            self.pelota = Pelota(400, 300, 25, 25, self.COLOR_PELOTA, self.PELOTA_VEL)
            self.pelota.check_append(self.p1)
            self.pelota.check_append(self.p2)
            self.pelota.check_append(self.p3)
            self.pelota.check_append(self.p4)
            self.pelota.check_append(self.cuadro)
            self.pelota.set_collided_event(self.pelota_collided)
            self.pelota.set_touched_down_event(self.die_p1)
            self.pelota.set_touched_right_event(self.die_p2)
            self.pelota.set_touched_up_event(self.die_p3)
            self.pelota.set_touched_left_event(self.die_p4)

            controls = {self.p1.left: (self.p1.leftpressed, self.p1.leftup),
                        self.p1.right: (self.p1.rightpressed, self.p1.rightup),
                        self.p2.up: (self.p2.uppressed, self.p2.upup),
                        self.p2.down: (self.p2.downpressed, self.p2.downup),
                        self.p3.left: (self.p3.leftpressed, self.p3.leftup),
                        self.p3.right: (self.p3.rightpressed, self.p3.rightup),
                        self.p4.up: (self.p4.uppressed, self.p4.upup),
                        self.p4.down: (self.p4.downpressed, self.p4.downup)
                        }

            self.menu(clock)

            # -------- Main Program Loop -----------
            while self.gaming:
                # --- Main event loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.gaming = False
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.gaming = False
                        try:
                            controls[event.key][0]()
                        except KeyError:
                            pass
                    elif event.type == pygame.KEYUP:
                        try:
                            controls[event.key][1]()
                        except KeyError:
                            pass

                # --- Game logic should go here
                if joystick_count >= 1:
                    horiz_axis_pos = joy0.get_axis(0)
                    vert_axis_pos = joy0.get_axis(1)
                    self.p1.joy(horiz_axis_pos, vert_axis_pos)
                if joystick_count >= 2:
                    horiz_axis_pos = joy1.get_axis(0)
                    vert_axis_pos = joy1.get_axis(1)
                    self.p2.joy(horiz_axis_pos, vert_axis_pos)
                if joystick_count >= 3:
                    horiz_axis_pos = joy2.get_axis(0)
                    vert_axis_pos = joy2.get_axis(1)
                    self.p3.joy(horiz_axis_pos, vert_axis_pos)
                if joystick_count >= 4:
                    horiz_axis_pos = joy3.get_axis(0)
                    vert_axis_pos = joy3.get_axis(1)
                    self.p4.joy(horiz_axis_pos, vert_axis_pos)
                self.p1.run()
                self.p2.run()
                self.p3.run()
                self.p4.run()
                self.cuadro.framecount += 1
                if self.cuadro.framecount == 30:
                    self.cuadro.color = random.choice(self.color_palette[1:-1])
                    self.cuadro.framecount = 0
                for p in self.particles:
                    p.update_pos()
                self.pelota.update_pos()

                # --- Screen-clearing code goes here
                self.screen.fill(self.bgcolor)
                # --- Drawing code should go here
                self.p1.draw(self.screen)
                self.p2.draw(self.screen)
                self.p3.draw(self.screen)
                self.p4.draw(self.screen)
                self.cuadro.draw(self.screen)
                for p in self.particles:
                    p.draw(self.screen)
                self.pelota.draw(self.screen)
                # --- Go ahead and update the screen with what we've drawn.
                pygame.display.flip()
                self.sound.run()
                # --- Limit to 30 frames per second
                clock.tick(self.fps)

        # Close the window and quit.
        pygame.mixer.quit()
        pygame.quit()


if __name__ == '__main__':
    pong4four = Game()
    pong4four.main()
