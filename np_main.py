from dataclasses import dataclass
from typing import Union

import click
import numpy as np
import pygame as pg


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
    speed_initial_value: float
    radius: int
    spring: float
    determinist: bool


class Universe:
    def __init__(self, ctx: Context):
        self.number_of_dots = ctx.number_of_dots
        self.dims = (self.number_of_dots, 2, 2)
        self.dots = np.zeros(self.dims, dtype=float)
        self.positions = self.dots[:, 0]
        self.speeds = self.dots[:, 1]


def init_speeds(speeds: np.ndarray, ctx: Context):
    size = len(speeds)
    angle_dist = np.random.normal(0., np.pi, size)
    scale_dist = np.random.normal(1., 1., size)
    speed_value = (np.cos(angle_dist), np.sin(angle_dist))
    speed_vector = np.vstack(speed_value).T
    speed_vector *= scale_dist[:, None]
    speeds[:] = speed_vector * ctx.speed_initial_value


def init_positions(positions: np.ndarray, ctx: Context):
    center = ctx.window.center
    size = len(positions)
    if ctx.determinist:
        positions[:] = np.linspace(center.x -10, center.x + 10, 2*ctx.number_of_dots).reshape(ctx.number_of_dots, 2)
    else:
        angle_dist = np.random.normal(0., np.pi, size)
        positions[:] = np.vstack((np.cos(angle_dist) + center.x, np.sin(angle_dist) + center.y)).T
        #positions[:] = np.random.normal((center.x, center.y),
        #                            (10, 10),
        #                            (size, 2))  # [center.x, center.y] + (np.random.random((size, 2)) - 0.5) * 2


def init_universe(universe: Universe, ctx: Context):
    init_positions(universe.positions, ctx)
    init_speeds(universe.speeds, ctx)


def draw_dots(screen: pg.Surface, positions: np.ndarray, ctx: Context, color):
    int_positions = positions.astype(int)
    length = ctx.window.size.x
    high = ctx.window.size.y
    for p in int_positions:
        screen.set_at((p[0], p[1]), color)


def get_new_values_for_outside(radius: int, center, size: int) -> Union[int, np.ndarray]:
    angle_dist = np.random.normal(0., np.pi, size)
    return np.cos(angle_dist) * radius + center
    #return np.random.randint(-radius + center, +radius + center, size)


def get_mask_for_axe(pos_axe: np.ndarray, max_value: int) -> np.ma.MaskedArray:
    return np.ma.masked_outside(pos_axe, 0, max_value)


def center_position_axe(pos_axe: np.ndarray, mask: np.ma.MaskedArray, radius: int, center: int) -> np.ndarray:
    size = np.count_nonzero(mask.mask == True)
    if size:
        values = get_new_values_for_outside(radius, center, size)
        pos_axe[mask.mask] = values
    return mask


def compute_distances(p, ref, ctx: Context):
    a = p[:, 0] - ref[0]
    b = p[:, 1] - ref[1]
    return np.sqrt(np.square(a) + np.square(b))[:, None]


def update_speeds(positions, speeds, ctx: Context):
    forces = np.zeros(speeds.shape)
    forces += (0., ctx.gravity)

    if ctx.rand_ratio:
        nb_vectors = speeds.shape[0]
        alteration = (1 - 2 * np.random.random(2 * nb_vectors).reshape(nb_vectors, 2))
        forces[:] += ctx.rand_ratio * alteration

    distances = compute_distances(positions, (ctx.window.center.x, ctx.window.center.y), ctx)
    springs = (positions - (ctx.window.center.x, ctx.window.center.y)) * distances * ctx.spring
    speeds[:] += forces
    speeds[:] -= springs


def move(universe: Universe, ctx: Context):
    length = ctx.window.size.x
    high = ctx.window.size.y
    center = ctx.window.center

    positions = universe.positions
    speeds = universe.speeds
    positions[:] += speeds

    mask_x: np.ma.MaskedArray = get_mask_for_axe(positions[:, 0], length)
    mask_y: np.ma.MaskedArray = get_mask_for_axe(positions[:, 1], high)

    if ctx.bounce:
        speeds[:, 0][mask_x.mask] *= -1
        speeds[:, 1][mask_y.mask] *= -1
    else:
        if np.any(mask_y.mask) or np.any(mask_x.mask):
            selection = positions[mask_x.mask | mask_y.mask]
            size = selection.shape[0]
            new_pos = np.vstack(
                (get_new_values_for_outside(10, center.x, size), get_new_values_for_outside(10, center.y, size))).T
            positions[mask_x.mask | mask_y.mask] = new_pos

            speed_selection = speeds[mask_x.mask | mask_y.mask]
            init_speeds(speed_selection, ctx=ctx)
            speeds[mask_x.mask | mask_y.mask] = speed_selection

    update_speeds(positions, speeds, ctx)


@click.command()
@click.option('-b', '--bounce', is_flag=True, type=bool, help='Bounce.')
@click.option('-n', '--number_of_dots', default=1000, type=int, help='Number of stars.')
@click.option('-r', '--rand_ratio', default=0.001, type=float, help='Random ration.')
@click.option('-xs', '--x_size', default=800, type=int, help='X windows size.')
@click.option('-ys', '--y_size', default=800, type=int, help='Y windows size.')
@click.option('-s', '--speed_initial_value', default=5, type=float, help='Initial speed.')
@click.option('-g', '--gravity', default=0, type=float, help='Gravity.')
@click.option('-yc', '--y_center', default=None, type=int, help='X center.')
@click.option('-d', '--radius', default=5, type=int, help='Radius used for particle settings')
@click.option('-k', '--spring', default=0.001, type=float, help='Spring ratio')
@click.option('-t', '--tick', default=20, type=int, help='Clock tick')
@click.option('-h', '--halt', is_flag=True, help='Halt on startup')
@click.option('-e', '--determinist', is_flag=True, help='Determinist')
@click.option('-q', '--queue', default=5, type=int, help='Radius used for particle settings')
def run_main(bounce: bool, number_of_dots: int, rand_ratio: float, x_size: int, y_size: int,
             speed_initial_value: float, gravity: float,
             y_center: int,
             radius: int,
             spring: float,
             tick: int,
             halt: bool,
             determinist: bool,
             queue: int):
    used_y_center = y_size // 2 if y_center is None else y_center
    window = Window(Position(x_size, y_size), Position(x_size // 2, used_y_center))

    ctx = Context(window=window,
                  bounce=bounce,
                  rand_ratio=rand_ratio,
                  number_of_dots=number_of_dots,
                  speed_initial_value=speed_initial_value,
                  gravity=gravity,
                  radius=radius,
                  spring=spring,
                  determinist=determinist)

    print(ctx)

    universe = Universe(ctx)

    init_universe(universe, ctx)

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
    past = np.zeros((10, ctx.number_of_dots, 2))
    i_past_1dim = past.shape[0] - 1
    i_past_put = 0
    i_past_read_start = 1
    i_past_read = 0
    start_draw_past = False
    i_past_black_start = False
    i_past_black = 0
    follow = False
    done = False

    while not done:

        if not halt:



            draw_dots(screen, universe.positions, ctx, black)
            move(universe, ctx)

            past[i_past_put, :] = universe.positions.astype(int)

            i_past_put = 0 if i_past_put >= i_past_1dim else i_past_put + 1

            if not start_draw_past:
                if i_past_put > i_past_read_start:
                    start_draw_past = True
            else:
                draw_dots(screen, past[i_past_read], ctx, red)
                i_past_read += 1
                i_past_read = 0 if i_past_read > i_past_1dim else i_past_read

            if not i_past_black_start and i_past_read == queue:
                i_past_black_start = True

            if i_past_black_start:
                i_past_black = i_past_read - queue
                i_past_black = i_past_read + i_past_1dim + 1 - queue if i_past_black < 0 else i_past_black

                draw_dots(screen, past[i_past_black], ctx, black)

            draw_dots(screen, universe.positions, ctx, white)

            pg.display.update()

        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                done = 1
                break
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                window.center.copy(e.pos)
            elif follow and e.type == pg.MOUSEMOTION:
                window.center.copy(e.pos)
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    halt = not halt
                if e.key == pg.K_a:
                    ctx.spring *= 1.2
                    print(ctx.spring)
                elif e.key == pg.K_z:
                    ctx.spring *= 0.8
                    print(ctx.spring)
                elif e.key == pg.K_f:
                    follow = not follow
                elif e.key == pg.K_q:
                    print("Bye !")
                    done = 1
                    break

        clock.tick(tick)


if __name__ == '__main__':
    run_main()
