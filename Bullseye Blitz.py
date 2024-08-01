import math
import random
import time
import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullseye Blitz")

TARGET_CREATION_INTERVAL = 400
CREATE_TARGET_EVENT = pygame.USEREVENT

TARGET_MARGIN = 30

BACKGROUND_COLOR = (0, 25, 40)
MAX_LIVES = 3
HEADER_HEIGHT = 50

FONT_LABEL = pygame.font.SysFont("Comicsans", 24)


class ExpandingTarget:
    MAX_DIAMETER = 30
    EXPANSION_RATE = 0.2
    PRIMARY_COLOR = "red"
    SECONDARY_COLOR = "white"

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.diameter = 0
        self.expanding = True

    def update(self):
        if self.diameter + self.EXPANSION_RATE >= self.MAX_DIAMETER:
            self.expanding = False

        if self.expanding:
            self.diameter += self.EXPANSION_RATE
        else:
            self.diameter -= self.EXPANSION_RATE

    def draw(self, surface):
        pygame.draw.circle(surface, self.PRIMARY_COLOR, (self.pos_x, self.pos_y), self.diameter)
        pygame.draw.circle(surface, self.SECONDARY_COLOR, (self.pos_x, self.pos_y), self.diameter * 0.8)
        pygame.draw.circle(surface, self.PRIMARY_COLOR, (self.pos_x, self.pos_y), self.diameter * 0.6)
        pygame.draw.circle(surface, self.SECONDARY_COLOR, (self.pos_x, self.pos_y), self.diameter * 0.4)

    def is_colliding(self, x, y):
        distance = math.sqrt((x - self.pos_x) ** 2 + (y - self.pos_y) ** 2)
        return distance <= self.diameter


def draw_elements(surface, targets_list):
    surface.fill(BACKGROUND_COLOR)

    for target in targets_list:
        target.draw(surface)


def format_duration(seconds):
    millis = math.floor(int(seconds * 1000 % 1000) / 100)
    secs = int(round(seconds % 60, 1))
    mins = int(seconds // 60)

    return f"{mins:02d}:{millis}"


def draw_header(surface, time_elapsed, hits, missed):
    pygame.draw.rect(surface, "grey", (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
    time_text = FONT_LABEL.render(f"Time: {format_duration(time_elapsed)}", 1, "black")

    hit_rate = round(hits / time_elapsed, 1)
    hit_rate_text = FONT_LABEL.render(f"Speed: {hit_rate} t/s", 1, "black")

    hits_text = FONT_LABEL.render(f"Hits: {hits}", 1, "black")

    lives_text = FONT_LABEL.render(f"Lives: {MAX_LIVES - missed}", 1, "black")

    surface.blit(time_text, (5, 5))
    surface.blit(hit_rate_text, (200, 5))
    surface.blit(hits_text, (450, 5))
    surface.blit(lives_text, (650, 5))


def get_center_position(surface):
    return SCREEN_WIDTH / 2 - surface.get_width() / 2


def show_end_screen(surface, time_elapsed, hits, total_clicks):
    surface.fill(BACKGROUND_COLOR)
    time_text = FONT_LABEL.render(f"Time: {format_duration(time_elapsed)}", 1, "white")

    hit_rate = round(hits / time_elapsed, 1)
    hit_rate_text = FONT_LABEL.render(f"Speed: {hit_rate} t/s", 1, "white")

    hits_text = FONT_LABEL.render(f"Hits: {hits}", 1, "white")

    accuracy_percentage = round(hits / total_clicks * 100, 1) if total_clicks > 0 else 0
    accuracy_text = FONT_LABEL.render(f"Accuracy: {accuracy_percentage}%", 1, "white")

    surface.blit(time_text, (get_center_position(time_text), 100))
    surface.blit(hit_rate_text, (get_center_position(hit_rate_text), 200))
    surface.blit(hits_text, (get_center_position(hits_text), 300))
    surface.blit(accuracy_text, (get_center_position(accuracy_text), 400))

    pygame.display.update()

    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                return


def main_game():
    game_running = True
    target_objects = []
    game_clock = pygame.time.Clock()

    hit_count = 0
    click_count = 0
    missed_targets = 0
    start_time = time.time()

    pygame.time.set_timer(CREATE_TARGET_EVENT, TARGET_CREATION_INTERVAL)

    while game_running:
        game_clock.tick(60)
        click_detected = False
        cursor_position = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                break

            if event.type == CREATE_TARGET_EVENT:
                pos_x = random.randint(TARGET_MARGIN, SCREEN_WIDTH - TARGET_MARGIN)
                pos_y = random.randint(TARGET_MARGIN + HEADER_HEIGHT, SCREEN_HEIGHT - TARGET_MARGIN)
                
                new_target = ExpandingTarget(pos_x, pos_y)

                target_objects.append(new_target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_detected = True
                click_count += 1

        for target in target_objects:
            target.update()

            if target.diameter <= 0:
                target_objects.remove(target)
                missed_targets += 1

            if click_detected and target.is_colliding(*cursor_position):
                target_objects.remove(target)
                hit_count += 1

        if missed_targets >= MAX_LIVES:
            show_end_screen(DISPLAY, elapsed_time, hit_count, click_count)
            return

        draw_elements(DISPLAY, target_objects)
        draw_header(DISPLAY, elapsed_time, hit_count, missed_targets)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main_game()