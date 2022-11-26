import math
import random
import time
from dataclasses import dataclass

import pygame

from robotlib.viz.color import Color, Colors
from robotlib.viz.drawing import Corner, Width, FILLED
from robotlib.viz.pygame_canvas import PygameCanvas


@dataclass
class Body:
    name: str
    radius: float  # km
    orbit: float  # AU
    period: float  # years
    color: Color
    width: Width = FILLED


sun = Body('Sun', 696_340, 0, 0, Color.from_hex('fdfbd3'))

planets = [
    Body('Mercury', 2440, 0.39, 0.24, Color.from_hex('ada8a5')),
    Body('Venus', 6052, 0.72, 0.62, Color.from_hex('e6e6e6')),
    Body('Earth', 6371, 1.0, 1.0, Color.from_hex('0000ff')),
    Body('Mars', 3390, 1.5, 1.9, Color.from_hex('993d00')),
    Body('Jupiter', 69911, 5.2, 12, Color.from_hex('b07f35')),
    Body('', 58232, 9.5, 30, Color.from_hex('b07f35')),
    Body('Saturn', 120000, 9.5, 30, Color.from_hex('ab604a'), width=0.1),
    Body('Uranus', 25362, 19, 84, Color.from_hex('4fd0e7')),
    Body('Neptune', 24622, 30, 165, Color.from_hex('2990b5')),
]

solar_system = [sun, *planets]


def draw_stars(canvas: PygameCanvas, density: float = 0.0001) -> None:
    # TODO This is pretty slow

    stars = int(canvas.width * canvas.height * density)
    r = random.Random(0)

    for _ in range(stars):
        x = r.randint(0, canvas.width - 1)
        y = r.randint(0, canvas.height - 1)

        canvas.surface.set_at((x, y), sun.color.to_int8())


def draw_body(
        canvas: PygameCanvas,
        body: Body,
        t: float,
        radius_scale: float = 0.003,
        draw_name: bool = True
) -> None:
    x, y = canvas.center

    if body.orbit > 0:
        t_scale = 2 * math.pi / (10 * body.period)
        orbit_radius = 50 * (body.orbit + 2)
        orbit_radius = orbit_radius ** 0.85

        dx, dy = math.sin(t * t_scale) * orbit_radius, math.cos(t * t_scale) * orbit_radius
    else:
        dx, dy = 0, 0

    body_radius = body.radius * radius_scale
    body_radius = body_radius ** .45

    width = body.width
    if width != FILLED:
        width *= body_radius

    canvas.draw_circle((x + dx, y + dy), body_radius, body.color, width=width)

    if body.name and draw_name:
        offset = 1
        dx += body_radius * offset
        dy -= body_radius * offset
        canvas.draw_text(body.name, (x + dx, y + dy), corner=Corner.LEFT_TOP, color=Colors.WHITE, font_size=22)


def draw_solar_system() -> None:
    pygame.init()
    surface = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption('Solar System')
    canvas = PygameCanvas(surface)

    clock = pygame.time.Clock()

    running = True
    while running:
        canvas.fill(Colors.BLACK)

        draw_stars(canvas)

        t = time.monotonic()

        for body in solar_system:
            draw_body(canvas, body, t)

        canvas.draw_text(
            f'{round(clock.get_fps())} FPS',
            (0, canvas.height), corner=Corner.LEFT_TOP, color=Colors.WHITE
        )

        canvas.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        clock.tick(60)


def main():
    draw_solar_system()


if __name__ == '__main__':
    main()
