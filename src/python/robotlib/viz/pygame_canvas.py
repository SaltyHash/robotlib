from typing import Tuple

import pygame
import pygame.gfxdraw

from robotlib.viz.color import Color, Colors
from robotlib.viz.drawing import Canvas, Corner, FILLED, Width, Size2d


def to_pygame_color(color: Color) -> pygame.Color:
    color = color.to_int8()
    return pygame.Color(color)


class PygameCanvas(Canvas):
    def __init__(self, pygame_surface: 'pygame.Surface'):
        self.surface = pygame_surface
        self.fill(Colors.WHITE)

    def get_size(self) -> Size2d:
        size = self.surface.get_size()
        return Size2d(*size)

    def draw_line(self, p1, p2, color: Color = Colors.BLACK, width: Width = 1.0):
        p1 = self._to_pygame_point(p1)
        p2 = self._to_pygame_point(p2)
        color = to_pygame_color(color)

        pygame.draw.line(self.surface, color, p1, p2, width=round(width))

    def draw_circle(self, center, radius: float, color: Color = Colors.BLACK, width: Width = FILLED) -> None:
        if self._circle_is_out_of_bounds(center, radius):
            return

        center = self._to_pygame_point(center)
        color = to_pygame_color(color)

        args = (center, radius, color, width)

        if radius < sum(self.size) and (width == FILLED or round(width) == 1):
            # Drawing antialiased circles is expensive, so we only do it in certain circumstances
            self._draw_circle_antialiased(*args)
        else:
            self._draw_circle_simple(*args)

    def _circle_is_out_of_bounds(self, center, radius: float) -> bool:
        x, y = center
        return (
                x + radius < 0
                or x - radius > self.width
                or y + radius < 0
                or y - radius > self.height
        )

    def _draw_circle_antialiased(self, center, radius: float, color: Color, width: Width) -> None:
        x, y = center
        radius = round(radius)

        if width == FILLED:
            pygame.gfxdraw.filled_circle(self.surface, x, y, radius, color)

        pygame.gfxdraw.aacircle(self.surface, x, y, radius, color)

    def _draw_circle_simple(self, center, radius: float, color: Color, width: Width) -> None:
        width = 0 if width == FILLED else round(width)
        pygame.draw.circle(self.surface, color, center, radius, width=width)

    def draw_rect(self, left_bottom, width_height, color: Color = Colors.BLACK, width: Width = FILLED):
        left, bottom = left_bottom
        _, height = width_height
        left_top = (left, bottom + height)
        left_top = self._to_pygame_point(left_top)
        rect = pygame.Rect(left_top, width_height)
        color = to_pygame_color(color)
        width = 0 if width == FILLED else round(width)

        pygame.draw.rect(self.surface, color, rect, width=width)

    def draw_text(
            self,
            message: str,
            position,
            corner: Corner = Corner.LEFT_BOTTOM,
            color: Color = Colors.BLACK,
            background: Color = None,
            font_name: str = '',
            font_size: int = 24,
            bold: bool = False,
            italic: bool = False,
            antialias: bool = True,
    ) -> Size2d:
        font = pygame.font.SysFont(font_name, font_size, bold=bold, italic=italic)

        color = to_pygame_color(color)
        if background is not None:
            background = to_pygame_color(background)

        text = font.render(message, antialias, color, background)

        x, y = position
        if corner in {Corner.RIGHT_BOTTOM, Corner.RIGHT_TOP}:
            x -= text.get_width()
        if corner in {Corner.LEFT_BOTTOM, Corner.RIGHT_BOTTOM}:
            y += text.get_height()

        position = self._to_pygame_point((x, y))

        self.surface.blit(text, position)

        return Size2d(text.get_width(), text.get_height())

    def fill(self, color: Color):
        color = to_pygame_color(color)
        self.surface.fill(color)

    def render(self):
        pygame.display.flip()

    def _to_pygame_point(self, p: Tuple[float, float]) -> tuple[int, int]:
        x = round(p[0])
        y = round(self.height - p[1])
        return x, y


def main():
    pygame.init()
    surface = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption('pygame_canvas')
    canvas = PygameCanvas(surface)

    clock = pygame.time.Clock()

    running = True
    while running:
        canvas.fill(Colors.WHITE)

        canvas.draw_line((450, 50), (600, 250))
        canvas.draw_line(canvas.left_top, canvas.right_bottom, color=Colors.RED, width=10)
        canvas.draw_rect((20, 10), (200, 100))
        canvas.draw_rect((100, 50), (200, 100), color=Colors.YELLOW, width=15)
        canvas.draw_square((600, 300), 50, color=Colors.MAGENTA)
        canvas.draw_square((625, 325), 50, width=5)
        canvas.draw_circle((200, 200), 50, color=Colors.GRAY, width=10)
        canvas.draw_text('left-bottom', (0, 0), corner=Corner.LEFT_BOTTOM, background=Colors.YELLOW)

        y = canvas.height
        text = canvas.draw_text('left-top (bold)', (0, y), corner=Corner.LEFT_TOP, bold=True)
        y -= text.get_height()
        canvas.draw_text(f'{round(clock.get_fps())} FPS', (0, y), corner=Corner.LEFT_TOP)
        canvas.draw_text('right-bottom (italic)', (canvas.width, 0), corner=Corner.RIGHT_BOTTOM, italic=True)
        canvas.draw_text('right-top (serif)', canvas.size, corner=Corner.RIGHT_TOP, font_name='serif')

        canvas.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        clock.tick(60)


if __name__ == '__main__':
    main()
