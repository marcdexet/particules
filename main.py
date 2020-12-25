#!/usr/bin/env python
""" pg.examples.stars

    We are all in the gutter,
    but some of us are looking at the stars.
                                            -- Oscar Wilde

A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management.
"""
import math
import random
from dataclasses import dataclass
from typing import List, Any, Tuple

import click
import pygame as pg

# constants
from pygame.examples import stars

from utils import CircQueue


@dataclass
class Position:
    x: int
    y: int

    def copy(self, p: 'Position'):
        self.x, self.y = p.x, p.y

    def move(self, o):
        self.x, self.y = self.x + o.x, self.y + o.y

    def clone(self):
        return Position(self.x, self.y)

    def __truediv__(self, other):
        return Position(self.x // 2, self.y // 2)

    def as_tuple(self):
        return (int(self.x), int(self.y))


@dataclass
class Vect:
    x: float
    y: float

    def copy(self, p: 'Vect'):
        self.x, self.y = p.x, p.y

    def __add__(self, o):
        return Vect(self.x + o.x, self.y + o.y)

    def __mul__(self, o):
        return Vect(self.x * o, self.y * o)

    def __truediv__(self, o):
        return Vect(self.x / o, self.y / o)

    def increase(self, o):
        if type(o) is float:
            self.x, self.y = self.x * o, self.y * o
        else:
            self.x, self.y = self.x + o.x, self.y + o.y

    def inverse(self):
        self.x, self.y = -self.x, -self.y


@dataclass
class Star:
    velocity: Vect
    position: Position

    def copy(self, p: 'Star'):
        self.position, self.velocity = p.position, p.velocity
        return self

    def __add__(self, o):
        self.position, self.velocity = self.position + o.position, self.velocity + o.velocity

    def __mul__(self, o):
        self.position, self.velocity = self.position * o, self.velocity * o


@dataclass
class Context:
    WINSIZE: Position
    WINCENTER: Position
    number_of_stars: int
    bounce: bool
    rand_ratio: float


def init_star(ctx: Context):
    "creates new star values"
    direction = random.randrange(1000000)
    vel_x_rand_div = random.randint(1, 3)
    vel_y_rand_div = random.randint(1, 3)
    velocity_factor = random.random() * 0.6 + 0.4
    vel = Vect(math.sin(direction) * velocity_factor / vel_x_rand_div,
               math.cos(direction) * velocity_factor / vel_y_rand_div)
    return Star(velocity=vel, position=ctx.WINCENTER.clone())


def initialize_stars(ctx: Context) -> List:
    "creates a new starfield"
    stars = []
    for x in range(ctx.number_of_stars):
        star = init_star(ctx)
        steps = random.randint(0, ctx.WINCENTER.x)
        star.position.move(star.velocity * steps)
        star.velocity.increase(steps * 0.09)
        stars.append(star)
    return stars


def get_star_positions(stars: List[Star]) -> List[Position]:
    return [s.position for s in stars]


def clone_position(positions: List[Position]) -> List[Position]:
    return [p.clone() for p in positions]


def draw_stars(surface, positions, color):
    "used to draw (and clear) the stars"
    for p in positions:
        surface.set_at(p.as_tuple(), color)


def vrand(rand_ratio: float):
    return rand_ratio * (0.5 - random.random())


def move_stars(stars, ctx: Context) -> List[Position]:
    "animate the star values"
    # print(len(stars))
    positions = []
    WINSIZE = ctx.WINSIZE
    rand_ratio = ctx.rand_ratio
    bounce = ctx.bounce

    for star in stars:
        star.position.move(star.velocity)

        if not 0 <= star.position.x <= WINSIZE.x or not 0 <= star.position.y <= WINSIZE.y:
            if not bounce:
                star.copy(init_star(ctx))
            else:
                if not 0 <= star.position.x <= WINSIZE.x:
                    star.velocity.x = - star.velocity.x
                if not 0 <= star.position.y <= WINSIZE.y:
                    star.velocity.y = - star.velocity.y
        else:
            star.velocity.increase(Vect(vrand(rand_ratio), 0.002 - vrand(rand_ratio)))

        positions.append(star.position.clone())
    return positions


@dataclass
class Text(Position):
    img: Any


def create_text(ctx: Context):
    font = pg.font.SysFont(None, 24)
    img = font.render('hello', True, (120, 120, 0))
    return Text(x=ctx.WINCENTER.x, y=ctx.WINCENTER.y / 3, img=img)


def draw_past(screen, index: int, last_positions, past_positions, colors):
    if past_positions[index]:
        draw_stars(screen, past_positions[index], colors[index])

    past_positions[index] = last_positions



@click.command()
@click.option('--bounce', default=False, type=bool, help='Bounce.')
@click.option('--number_of_dots', default=1000, type=int, help='Number of stars.')
@click.option('--rand_ratio', default=0.001, type=float, help='Random ration.')
@click.option('--x_size', default=800, type=int, help='X windows size.')
@click.option('--y_size', default=800, type=int, help='Y windows size.')
def run_my_game(bounce: bool, number_of_stars: int, rand_ratio: float, x_size: int, y_size: int):
    WINSIZE = Position(x=x_size, y=y_size)
    WINCENTER = WINSIZE / 2

    ctx = Context(WINSIZE=WINSIZE,
                  WINCENTER=WINCENTER,
                  number_of_stars=number_of_stars,
                  bounce=bounce,
                  rand_ratio=rand_ratio)

    "This is the starfield code"
    # create our starfield
    random.seed()
    stars = initialize_stars(ctx=ctx)
    current_positions = move_stars(stars, ctx)
    clock = pg.time.Clock()
    # initialize and prepare screen
    pg.init()
    screen = pg.display.set_mode((WINSIZE.x, WINSIZE.y))
    pg.display.set_caption("Bonne année 2021")
    white = 255, 240, 200
    golden = 86, 101, 115  # 205, 120, 20
    red = 115, 91, 86
    black = 20, 20, 40
    grey = 40, 40, 40
    dark_grey = 30, 30, 40
    screen.fill(black)
    # text = create_text()
    # screen.blit(text.img, (text.x, text.y))

    # main game loop
    done = 0
    past_positions = [[], []]
    past_colors = [(black[0] + i*10, black[1] + i, black[2] + i) for i in reversed(range(10))]

    past_queue = CircQueue()

    while not done:

        draw_stars(screen, current_positions, black)
        #draw_stars(screen, current_positions, golden)
        past_queue.put(current_positions)
        current_positions = move_stars(stars, ctx)

#        draw_past(screen, 0, current_positions, past_positions, past_colors)
        #        draw_stars(screen, current_positions, golden)

        #        current_positions = move_stars(stars, ctx)
        #        blacked_it = clone_position(current_positions)
        #        draw_past(screen, 1, current_positions, past_positions, past_colors)
        draw_stars(screen, current_positions, white)
        past_queue.put(current_positions)

#        if past_queue.has_data_for_index(10):
#            for nb in reversed(range(5)):
#                draw_stars(screen, past_queue.get_before(nb), past_colors[nb])
        #        current_positions = move_stars(stars, ctx)

        #        draw_stars(screen, blacked_it, black)
        pg.display.update()
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                done = 1
                break
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                WINCENTER.x, WINCENTER.y = list(e.pos)
                #golden = (golden[0] + 5, golden[1] + 5, golden[2] + 5)
        clock.tick(100)


if __name__ == "__main__":
    run_my_game()
