import random
import sys

import pygame


WIDTH, HEIGHT = 900, 620
FPS = 60
ARENA_PADDING = 28
TURTLE_SIZE = 48
SQUARE_SIZE = 58
MAX_HAZARDS = 7
HAZARD_INTERVAL = 10.0
WIN_TIME = 110.0
TURTLE_SPEED = 310

BACKGROUND = (236, 244, 232)
ARENA = (249, 252, 246)
INK = (35, 52, 42)
MUTED = (92, 113, 94)
TURTLE_GREEN = (67, 155, 91)
TURTLE_DARK = (35, 105, 60)
HAZARD_RED = (218, 71, 59)
HAZARD_DARK = (148, 42, 37)
WHITE = (255, 255, 255)


class Turtle:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, TURTLE_SIZE, TURTLE_SIZE)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.direction = pygame.Vector2(1, 0)

    def move(self, direction, dt):
        bounds = pygame.Rect(
            ARENA_PADDING,
            116,
            WIDTH - ARENA_PADDING * 2,
            HEIGHT - 116 - ARENA_PADDING,
        )
        next_rect = self.rect.move(
            round(direction.x * TURTLE_SPEED * dt),
            round(direction.y * TURTLE_SPEED * dt),
        )
        if next_rect.left < bounds.left or next_rect.right > bounds.right:
            self.direction.x *= -1
        if next_rect.top < bounds.top or next_rect.bottom > bounds.bottom:
            self.direction.y *= -1
        self.rect = next_rect.clamp(bounds)

    def turn(self, direction):
        self.direction = pygame.Vector2(direction)

    def draw(self, surface):
        center = self.rect.center
        shell_radius = TURTLE_SIZE // 2 - 4
        pygame.draw.ellipse(surface, TURTLE_DARK, self.rect)
        inner = self.rect.inflate(-8, -8)
        pygame.draw.ellipse(surface, TURTLE_GREEN, inner)
        pygame.draw.line(surface, (121, 194, 112), (center[0] - 11, center[1] - 14), (center[0] + 11, center[1] + 14), 3)
        pygame.draw.line(surface, (121, 194, 112), (center[0] + 11, center[1] - 14), (center[0] - 11, center[1] + 14), 3)

        head = pygame.Rect(0, 0, 18, 18)
        head.center = (
            center[0] + int(self.direction.x * (TURTLE_SIZE // 2 - 2)),
            center[1] + int(self.direction.y * (TURTLE_SIZE // 2 - 2)),
        )
        pygame.draw.circle(surface, TURTLE_GREEN, head.center, 9)
        eye_position = (
            head.centerx + int(self.direction.x * 3 - self.direction.y * 3),
            head.centery + int(self.direction.y * 3 + self.direction.x * 3),
        )
        pygame.draw.circle(surface, INK, eye_position, 2)

        for foot_center in (
            (self.rect.left + 8, self.rect.top + 5),
            (self.rect.left + 8, self.rect.bottom - 5),
            (self.rect.right - 10, self.rect.top + 5),
            (self.rect.right - 10, self.rect.bottom - 5),
        ):
            pygame.draw.circle(surface, TURTLE_DARK, foot_center, 6)


class Hazard:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
        self.move_to_random_spot()

    def move_to_random_spot(self):
        area = pygame.Rect(
            ARENA_PADDING + 10,
            126,
            WIDTH - (ARENA_PADDING + 10) * 2 - SQUARE_SIZE,
            HEIGHT - 126 - ARENA_PADDING - SQUARE_SIZE,
        )
        self.rect.topleft = (
            random.randint(area.left, area.right),
            random.randint(area.top, area.bottom),
        )

    def draw(self, surface):
        shadow = self.rect.move(4, 5)
        pygame.draw.rect(surface, (196, 211, 190), shadow, border_radius=8)
        pygame.draw.rect(surface, HAZARD_RED, self.rect, border_radius=8)
        pygame.draw.rect(surface, HAZARD_DARK, self.rect, width=3, border_radius=8)
        pygame.draw.line(surface, WHITE, self.rect.topleft, self.rect.bottomright, 4)
        pygame.draw.line(surface, WHITE, self.rect.topright, self.rect.bottomleft, 4)


def make_font(size, bold=False):
    return pygame.font.SysFont("trebuchet ms", size, bold=bold)


def draw_text(surface, font, text, color, position, center=False):
    rendered = font.render(text, True, color)
    target = rendered.get_rect()
    if center:
        target.center = position
    else:
        target.topleft = position
    surface.blit(rendered, target)


def new_round():
    turtle = Turtle()
    hazard = Hazard()
    while turtle.rect.colliderect(hazard.rect.inflate(45, 45)):
        hazard.move_to_random_spot()
    return turtle, hazard


def new_non_overlapping_hazard(hazards):
    hazard = Hazard()
    while any(hazard.rect.colliderect(existing.rect) for existing in hazards):
        hazard.move_to_random_spot()
    return hazard


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dont Make the Turtle Touch the Squares")
    clock = pygame.time.Clock()

    title_font = make_font(32, bold=True)
    body_font = make_font(19)
    score_font = make_font(24, bold=True)
    turtle, hazard = new_round()
    hazards = [hazard]
    survival_time = 0.0
    game_over = False
    game_won = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or game_won):
                    turtle, hazard = new_round()
                    hazards = [hazard]
                    survival_time = 0.0
                    game_over = False
                    game_won = False
                elif not game_over and not game_won and event.key == pygame.K_RIGHT:
                    turtle.turn((1, 0))
                elif not game_over and not game_won and event.key == pygame.K_LEFT:
                    turtle.turn((-1, 0))
                elif not game_over and not game_won and event.key == pygame.K_DOWN:
                    turtle.turn((0, 1))
                elif not game_over and not game_won and event.key == pygame.K_UP:
                    turtle.turn((0, -1))

        if not game_over and not game_won:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                turtle.turn((1, 0))
            elif keys[pygame.K_LEFT]:
                turtle.turn((-1, 0))
            elif keys[pygame.K_DOWN]:
                turtle.turn((0, 1))
            elif keys[pygame.K_UP]:
                turtle.turn((0, -1))
            turtle.move(turtle.direction, dt)
            survival_time += dt
            if survival_time >= WIN_TIME:
                game_won = True
            elif len(hazards) < MAX_HAZARDS and survival_time >= len(hazards) * HAZARD_INTERVAL:
                hazards.append(new_non_overlapping_hazard(hazards))
            if not game_won and any(turtle.rect.colliderect(hazard.rect) for hazard in hazards):
                game_over = True

        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, ARENA, (ARENA_PADDING, 104, WIDTH - ARENA_PADDING * 2, HEIGHT - 132), border_radius=14)
        pygame.draw.rect(screen, (201, 218, 198), (ARENA_PADDING, 104, WIDTH - ARENA_PADDING * 2, HEIGHT - 132), width=2, border_radius=14)

        draw_text(screen, title_font, "DONT MAKE THE TURTLE TOUCH THE SQUARES", INK, (ARENA_PADDING, 24))
        draw_text(screen, body_font, "Use the arrow keys. Stay away from the squares.", MUTED, (ARENA_PADDING, 70))
        draw_text(screen, score_font, f"{survival_time:05.1f}s", TURTLE_DARK, (WIDTH - 72, 34), center=True)
        draw_text(screen, body_font, "SURVIVED", MUTED, (WIDTH - ARENA_PADDING - 83, 70))

        for hazard in hazards:
            hazard.draw(screen)
        turtle.draw(screen)

        if game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((35, 52, 42, 165))
            screen.blit(overlay, (0, 0))
            draw_text(screen, title_font, "YOU WIN", WHITE, (WIDTH // 2, HEIGHT // 2 - 30), center=True)
            draw_text(screen, body_font, "You survived all 110 seconds!", (224, 239, 219), (WIDTH // 2, HEIGHT // 2 + 14), center=True)
            draw_text(screen, body_font, "Press R to play again or Esc to quit", WHITE, (WIDTH // 2, HEIGHT // 2 + 55), center=True)
        elif game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((35, 52, 42, 165))
            screen.blit(overlay, (0, 0))
            draw_text(screen, title_font, "SQUARE GOT YOU", WHITE, (WIDTH // 2, HEIGHT // 2 - 30), center=True)
            draw_text(screen, body_font, f"You lasted {survival_time:.1f} seconds", (224, 239, 219), (WIDTH // 2, HEIGHT // 2 + 14), center=True)
            draw_text(screen, body_font, "Press R to try again or Esc to quit", WHITE, (WIDTH // 2, HEIGHT // 2 + 55), center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
