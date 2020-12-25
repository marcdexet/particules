from dataclasses import dataclass
import numpy as np
import pygame as pg
import click


@dataclass
class Position:
    x: int
    y: int

    def as_tuple(self):
        return self.x, self.y

    def copy(self, pos):
        self.x, self.y = pos


@dataclass
class Window:
    size: Position
    center: Position


@dataclass
class Context:
    window: Window
    number_of_dots: int
    bounce: bool
    rand_ratio: float
    gravity: float
    speed_initial_value: float = 5
    reset_speed = None
    reset_position = None


class Universe:
    def __init__(self, ctx: Context):
        self.number_of_dots = ctx.number_of_dots
        self.dims = (self.number_of_dots, 2, 2)
        self.dots = np.zeros(self.dims, dtype=float)
        self.positions = self.dots[:, 0]
        self.speeds = self.dots[:, 1]

    def get_all_positions(self):
        return


def init_speeds(speeds: np.ndarray, ctx: Context):
    size = len(speeds) if speeds.ndim == 2 else 1

    speed_dist = (np.random.random(size) * 2. - 1.) * np.pi
    speed_value = (np.cos(speed_dist), np.sin(speed_dist))

    if speeds.ndim == 2:
        speed_vector = np.vstack(speed_value).T
    else:
        speed_vector = speed_value

    speeds[:] = speed_vector


def init_positions(positions: np.ndarray, ctx: Context):
    center = ctx.window.center
    size = len(positions)
    positions[:] = [center.x, center.y] + (np.random.random((size, 2)) - 0.5) * 10


def init_dots(universe: Universe, ctx: Context):
    init_positions(universe.positions, ctx)
    init_speeds(universe.speeds, ctx)

def draw_dots(screen: pg.Surface, universe: Universe, ctx: Context, color):
    for p in universe.positions:
        screen.set_at((int(p[0]), int(p[1])), color)


def init_function(ctx: Context):
    length = ctx.window.size.x
    high = ctx.window.size.y
    center = ctx.window.center

    X_CHANGE = np.array([-1, 1])
    Y_CHANGE = np.array([1, -1])

    if ctx.bounce :
        def fn(speed, axes):
            speed[:] *= axes

        def gn(coord):
            changed = False
            matrix = np.array([1, 1])

            if not 0 < coord[0] < length:
                matrix *= X_CHANGE
                changed = True
            if not 0 < coord[1] < high:
                matrix *= Y_CHANGE
                changed = True
            return changed, matrix

        ctx.reset_speed = fn
        ctx.reset_position = gn

    else:
        def fn(speed, axes):
            init_speeds(speed, ctx)

        def gn(coord):
            changed = False
            matrix = np.array([0, 0])

            if not 0 < coord[0] < length:
                coord[0] = center.x + np.random.random(1)
                matrix += Y_CHANGE
                changed = True
            if not 0 < coord[1] < high:
                coord[1] = center.y + np.random.random(1)
                matrix += Y_CHANGE
                changed = True

            return changed, matrix

        ctx.reset_speed = fn
        ctx.reset_position = gn



def move(universe: Universe, ctx: Context):

    for dot in universe.dots:
        coord = dot[0]
        speed = dot[1]

        coord[:] += speed
        changed, matrix = ctx.reset_position(coord)

        if changed:
            coord[:] -= speed
            ctx.reset_speed(speed, matrix)
            coord[:] += speed
        else:
            speed[:] += ctx.rand_ratio * (1 - 2 * np.random.random(2) )
            speed[:] += (0., ctx.gravity)


@click.command()
@click.option('--bounce', default=False, type=bool, help='Bounce.')
@click.option('--number_of_dots', default=1000, type=int, help='Number of stars.')
@click.option('--rand_ratio', default=0.001, type=float, help='Random ration.')
@click.option('--x_size', default=800, type=int, help='X windows size.')
@click.option('--y_size', default=800, type=int, help='Y windows size.')
@click.option('--speed_initial_value', default=5, type=float, help='Initial speed.')
@click.option('--gravity', default=0, type=float, help='Gravity.')
@click.option('--y_center', default=None, type=int, help='X center.')

def run_main(bounce: bool, number_of_dots: int, rand_ratio: float, x_size: int, y_size: int,
             speed_initial_value: float, gravity: float,
             y_center: int):
    used_y_center = y_size // 2 if y_center is None else y_center
    window = Window(Position(x_size, y_size), Position(x_size // 2, used_y_center))

    ctx = Context(window=window,
                  bounce=bounce,
                  rand_ratio=rand_ratio,
                  number_of_dots=number_of_dots,
                  speed_initial_value=speed_initial_value,
                  gravity=gravity)

    init_function(ctx)

    universe = Universe(ctx)

    init_dots(universe, ctx)

    clock = pg.time.Clock()
    pg.init()
    screen = pg.display.set_mode(ctx.window.size.as_tuple())
    white = 255, 240, 200
    golden = 86, 101, 115  # 205, 120, 20
    red = 115, 91, 86
    black = 20, 20, 40
    grey = 40, 40, 40
    dark_grey = 30, 30, 40
    screen.fill(black)

    done = False

    while not done:

        draw_dots(screen, universe, ctx, black)
        move(universe, ctx)
        draw_dots(screen, universe, ctx, white)

        pg.display.update()
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                done = 1
                break
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                window.center.copy(e.pos)
                # golden = (golden[0] + 5, golden[1] + 5, golden[2] + 5)
        clock.tick(100)


if __name__ == '__main__':
    run_main()
