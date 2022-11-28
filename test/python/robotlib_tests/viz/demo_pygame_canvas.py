"""Displays a basic simulation of the solar system using PygameCanvas."""

import math
import random
import time
from dataclasses import dataclass

import pygame

from robotlib.geometry import Point2d
from robotlib.viz.color import Color, Colors
from robotlib.viz.drawing import Corner, Width, FILLED
from robotlib.viz.pygame_canvas import PygameCanvas

KM_PER_AU = 149597870


@dataclass
class Settings:
    px_per_km: float
    fps: int = 60
    planet_scale: float = 1000
    seconds_per_year: float = 10


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
    Body('Mercury', radius=2440, orbit=0.39, period=0.24, color=Color.from_hex('ada8a5')),
    Body('Venus', radius=6052, orbit=0.72, period=0.62, color=Color.from_hex('e6e6e6')),
    Body('Earth', radius=6371, orbit=1.0, period=1.0, color=Color.from_hex('0000ff')),
    Body('Mars', radius=3390, orbit=1.5, period=1.9, color=Color.from_hex('993d00')),
    Body('Jupiter', radius=69911, orbit=5.2, period=12, color=Color.from_hex('b07f35')),
    Body('Saturn', radius=120000, orbit=9.5, period=30, color=Color.from_hex('ab604a'), width=0.1),
    Body('', radius=58232, orbit=9.5, period=30, color=Color.from_hex('b07f35')),
    Body('Uranus', radius=25362, orbit=19, period=84, color=Color.from_hex('4fd0e7')),
    Body('Neptune', radius=24622, orbit=30, period=165, color=Color.from_hex('2990b5')),
    # Honorable mention :)
    Body('Pluto', 1188, 40, 248, color=Color.from_hex('ccba99')),
]


def main():
    draw_solar_system()


def draw_solar_system() -> None:
    pygame.init()
    surface = pygame.display.set_mode(flags=pygame.RESIZABLE)
    pygame.display.set_caption('Solar System')
    canvas = PygameCanvas(surface)

    settings = get_settings(canvas)

    clock = pygame.time.Clock()

    running = True
    while running:
        canvas.fill(Colors.BLACK)

        draw_stars(canvas)

        t = time.monotonic()

        draw_body(canvas, sun, t, px_per_km=settings.px_per_km)

        for planet in planets:
            draw_body(
                canvas, planet, t,
                px_per_km=settings.px_per_km,
                size_scale=settings.planet_scale,
                seconds_per_year=settings.seconds_per_year
            )

        draw_hud(canvas, settings, clock)

        canvas.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break
            elif event.type == pygame.MOUSEWHEEL:
                scale_factor = 1.04
                px_per_km = settings.px_per_km * (scale_factor if event.y == 1 else 1 / scale_factor)
                settings.px_per_km = max(px_per_km, 0)

        clock.tick(settings.fps)

    pygame.quit()


def get_settings(canvas: PygameCanvas) -> Settings:
    screen_radius_px = min(canvas.size) / 2
    max_orbit_au = max(p.orbit for p in planets)
    max_orbit_km = max_orbit_au * KM_PER_AU
    px_per_km = (0.9 * screen_radius_px) / max_orbit_km

    return Settings(px_per_km)


def draw_stars(canvas: PygameCanvas, density: float = 0.0002) -> None:
    star_count = int(canvas.width * canvas.height * density)
    r = random.Random(0)

    for _ in range(star_count):
        x = r.randint(0, canvas.width - 1)
        y = r.randint(0, canvas.height - 1)

        p = r.randint(0, 255)
        canvas.set_pixel(Point2d(x, y), Color(p, p, p))


def draw_body(
        canvas: PygameCanvas,
        body: Body,
        t: float,
        px_per_km: float = 0.00001,
        size_scale: float = 1.0,
        seconds_per_year: float = ...,
        draw_orbit: bool = True,
        draw_name: bool = True,
) -> None:
    ss_center = canvas.center
    x, y = ss_center

    px_per_au = px_per_km * KM_PER_AU

    if body.orbit > 0:
        t_scale = (1 / seconds_per_year) / body.period * (2 * math.pi)
        orbit_radius = (body.orbit + 0) * px_per_au

        dx = -math.sin(t * t_scale) * orbit_radius
        dy = math.cos(t * t_scale) * orbit_radius

        if draw_orbit and orbit_radius < sum(canvas.size):
            canvas.draw_circle(ss_center, orbit_radius, color=body.color, width=1)
    else:
        dx, dy = 0, 0

    body_radius = body.radius * px_per_km * size_scale
    body_radius = max(body_radius, 1)

    width = body.width
    if width != FILLED:
        width *= body_radius

    canvas.draw_circle((x + dx, y + dy), body_radius, body.color, width=width)

    if body.name and draw_name:
        offset = 1
        dx += body_radius * offset
        dy -= body_radius * offset
        canvas.draw_text(body.name, (x + dx, y + dy), corner=Corner.LEFT_TOP, color=Colors.WHITE, font_size=22)


def draw_hud(canvas, settings: Settings, clock) -> None:
    messages = [
        f'FPS: {round(clock.get_fps())}',
        f'Scroll to zoom',
        f'Press Esc to quit',
        f'Planet scale: {settings.planet_scale}x',
        f'Time scale: 1 year every {settings.seconds_per_year} seconds'
    ]

    x, y = 10, canvas.height - 10
    for message in messages:
        y -= canvas.draw_text(message, (x, y), corner=Corner.LEFT_TOP, color=Colors.WHITE).height


if __name__ == '__main__':
    main()
