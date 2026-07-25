import pygame
pygame.init()
from const import *
from math import sin, cos, radians, degrees, atan2
import random

time = 0
time_moving = 0
moving = False
pause = False
pause_duration_counter = 0
score = 0
floor = pygame.transform.scale(pygame.image.load('src/floor.png'), (WIDTH, HEIGHT / 2))
level = 1
super_points = 5
points = 100
master_volume = 0.5  # Global variable for master volume control

# Game Configuration Settings
game_mode = '3D'  # Options: '3D', 'Classic'
difficulty = 'Normal'  # Options: 'Easy', 'Normal', 'Hard'

def check_one_signed(a, b):
    if (a >= 0 and b >= 0) or (a <= 0 and b <= 0):
        return True
    return False


def dist_between_point(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def print_text(sc, x, y, text, size, color, align='left', font=None):
    font = pygame.font.Font(font, size)
    surf = font.render(text, True, color)
    if align == 'left':
        sc.blit(surf, (x, y))
    elif align == 'right':
        sc.blit(surf, (x - surf.get_width(), y))
    elif align == 'center':
        sc.blit(surf, (x - surf.get_width() / 2, y))
    return surf


class NPC:
    def __init__(self, x, y, sprite, sprite_super, color, angle=0.1, speed=3+level / 5):
        self.x, self.y = x, y
        self.angle = angle
        self.sprite = sprite
        self.sprite_super = sprite_super
        self.base_speed = speed
        self.speed = speed
        self.hunt = False
        self.way_to_roam = (self.x // TILE_SIZE, self.y // TILE_SIZE)
        self.color = color
        self.run_away = False

    def find_shortest_way(self, field, start, finish):  # made using BFS algorithm
        queue = [[start]]
        seen = {start}
        while queue:
            path = queue[0]
            queue = queue[1:len(queue)]
            x, y = path[-1]
            if y == finish[1] and x == finish[0]:
                return path
            for x2, y2 in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                x2 = int(x2)
                y2 = int(y2)
                if 0 <= x2 < field.size_x and 0 <= y2 < field.size_y and field.field[y2][x2] != 1 and (x2, y2) not in seen:
                    queue.append(path + [(x2, y2)])
                    seen.add((x2, y2))

    def move(self, sc, field, player, raycaster):
        diff_multiplier = 0.7 if difficulty == 'Easy' else (1.3 if difficulty == 'Hard' else 1.0)

        if self.x // TILE_SIZE >= 8 and self.x // TILE_SIZE <= 10 and self.y // TILE_SIZE == 9:
            self.run_away = False
        if self.run_away and not (self.x // TILE_SIZE >= 8 and self.x // TILE_SIZE <= 10 and self.y // TILE_SIZE == 9):
            way = self.find_shortest_way(field, (self.x // TILE_SIZE, self.y // TILE_SIZE), (9, 9))
            if len(way) >= 2:
                x_to = way[1][0] * TILE_SIZE + TILE_SIZE / 2
                y_to = way[1][1] * TILE_SIZE + TILE_SIZE / 2

                step = 10 * diff_multiplier
                if x_to > self.x:
                    self.x += step
                elif x_to < self.x:
                    self.x -= step

                if y_to > self.y:
                    self.y += step
                elif y_to < self.y:
                    self.y -= step
        elif (dist_between_point(self.x, self.y, player.x, player.y) <= (700 if difficulty == 'Hard' else 500) or not raycaster.check_intersection(sc, field, self.x, self.y, player.x, player.y)) and not player.super_mode:
            self.hunt = True
            way = self.find_shortest_way(field, (self.x // TILE_SIZE, self.y // TILE_SIZE), (player.x // TILE_SIZE, player.y // TILE_SIZE))

            if len(way) >= 2:
                x_to = way[1][0] * TILE_SIZE + TILE_SIZE / 2
                y_to = way[1][1] * TILE_SIZE + TILE_SIZE / 2

                current_speed = self.speed * diff_multiplier
                if x_to > self.x:
                    self.x += current_speed
                elif x_to < self.x:
                    self.x -= current_speed

                if y_to > self.y:
                    self.y += current_speed
                elif y_to < self.y:
                    self.y -= current_speed

        else:
            if self.x // TILE_SIZE == self.way_to_roam[0] and self.y // TILE_SIZE == self.way_to_roam[1]:
                to_choose = []
                for x in range(field.size_x):
                    for y in range(field.size_y):
                        if field.field[y][x] == 0 or field.field[y][x] == -1:
                            to_choose.append((x, y))

                self.way_to_roam = random.choice(to_choose)

            else:
                way = self.find_shortest_way(field, (self.x // TILE_SIZE, self.y // TILE_SIZE), self.way_to_roam)
                if way and len(way) >= 2:
                    x_to = way[1][0] * TILE_SIZE + TILE_SIZE / 2
                    y_to = way[1][1] * TILE_SIZE + TILE_SIZE / 2

                    current_speed = self.speed * diff_multiplier
                    if x_to > self.x:
                        self.x += current_speed
                    elif x_to < self.x:
                        self.x -= current_speed

                    if y_to > self.y:
                        self.y += current_speed
                    elif y_to < self.y:
                        self.y -= current_speed

            self.hunt = False


class Field:
    def __init__(self):
        self.field = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        self.size_x = len(self.field[0])
        self.size_y = len(self.field)
        to_choose = []
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.field[y][x] == 0:
                    to_choose.append((x, y))
        for i in range(super_points):
            el = random.choice(to_choose)
            self.field[el[1]][el[0]] = 2

    def draw_minimap(self, sc, player, frames, NPC_s, k=6):
        map_width = self.size_x * (TILE_SIZE / k)
        map_height = self.size_y * (TILE_SIZE / k)
        offset_x = WIDTH - map_width - 20
        offset_y = HEIGHT - map_height - 20

        map_surface = pygame.Surface((map_width, map_height))
        map_surface.set_alpha(150)
        map_surface.fill((20, 20, 20))
        sc.blit(map_surface, (offset_x, offset_y))

        for raw in range(self.size_x):
            for tile in range(self.size_y):
                if self.field[tile][raw] == 1:
                    pygame.draw.rect(sc, (80, 80, 120),
                                     (offset_x + raw * TILE_SIZE / k, offset_y + tile * TILE_SIZE / k, TILE_SIZE / k, TILE_SIZE / k))
                elif self.field[tile][raw] == 0 or self.field[tile][raw] == 2:
                    pygame.draw.rect(sc, (30, 30, 30),
                                     (offset_x + raw * TILE_SIZE / k, offset_y + tile * TILE_SIZE / k, TILE_SIZE / k, TILE_SIZE / k))
                    if self.field[tile][raw] == 0:
                        pygame.draw.circle(sc, (200, 200, 0), (offset_x + raw * TILE_SIZE / k + TILE_SIZE / 2 / k, offset_y + tile * TILE_SIZE / k + TILE_SIZE / 2 / k), max(1, TILE_SIZE / k / 6))

        for npc in NPC_s:
            ghost_color = (255, 0, 0) if npc.color == 'red' else (0, 100, 255) if npc.color == 'blue' else (255, 255, 0) if npc.color == 'yellow' else (255, 100, 200)
            if player.super_mode:
                ghost_color = (0, 0, 255)
            pygame.draw.circle(sc, ghost_color, (offset_x + npc.x / k, offset_y + npc.y / k), max(2, TILE_SIZE / k / 3))

        ind = int(time / (FPS / 20)) % len(frames)
        rotated_frame = pygame.transform.rotate(frames[ind], player.angle)
        scaled_frame = pygame.transform.scale(rotated_frame, (int(20 / (k/5)), int(20 / (k/5))))
        sc.blit(scaled_frame, (offset_x + player.x / k - scaled_frame.get_width() / 2, offset_y + player.y / k - scaled_frame.get_height() / 2))

    def draw_classic(self, sc, player, frames, NPC_s):
        tile_size_classic = min(WIDTH // self.size_x, HEIGHT // self.size_y)
        offset_x = (WIDTH - self.size_x * tile_size_classic) // 2
        offset_y = (HEIGHT - self.size_y * tile_size_classic) // 2

        sc.fill((5, 5, 8))

        for raw in range(self.size_x):
            for tile in range(self.size_y):
                rx = offset_x + raw * tile_size_classic
                ry = offset_y + tile * tile_size_classic
                if self.field[tile][raw] == 1:
                    pygame.draw.rect(sc, (10, 10, 80), (rx, ry, tile_size_classic, tile_size_classic))
                elif self.field[tile][raw] == 0:
                    pygame.draw.circle(sc, (200, 200, 0), (rx + tile_size_classic // 2, ry + tile_size_classic // 2), max(2, tile_size_classic // 6))
                elif self.field[tile][raw] == 2:
                    pygame.draw.circle(sc, (200, 80, 80), (rx + tile_size_classic // 2, ry + tile_size_classic // 2), max(4, tile_size_classic // 3))

        for npc in NPC_s:
            ghost_img = npc.sprite_super if player.super_mode else npc.sprite
            scaled_ghost = pygame.transform.scale(ghost_img, (int(tile_size_classic * 0.8), int(tile_size_classic * 0.8)))
            nx = offset_x + (npc.x / (self.size_x * TILE_SIZE)) * (self.size_x * tile_size_classic)
            ny = offset_y + (npc.y / (self.size_y * TILE_SIZE)) * (self.size_y * tile_size_classic)
            sc.blit(scaled_ghost, (nx - scaled_ghost.get_width() / 2, ny - scaled_ghost.get_height() / 2))

        ind = int(time / (FPS / 20)) % len(frames)
        rotated_frame = pygame.transform.rotate(frames[ind], player.angle)
        scaled_frame = pygame.transform.scale(rotated_frame, (int(tile_size_classic * 0.8), int(tile_size_classic * 0.8)))
        px = offset_x + (player.x / (self.size_x * TILE_SIZE)) * (self.size_x * tile_size_classic)
        py = offset_y + (player.y / (self.size_y * TILE_SIZE)) * (self.size_y * tile_size_classic)
        sc.blit(scaled_frame, (px - scaled_frame.get_width() / 2, py - scaled_frame.get_height() / 2))

class Player:
    def __init__(self, x, y, angle=0.1, speed=5, angle_speed=5):
        self.x, self.y = x, y
        self.angle = angle
        self.angle_speed = angle_speed
        self.speed = speed
        self.mouse_prev_x = WIDTH // 2
        self.score = 0
        self.score_super = 0
        self.super_mode = False
        self.super_mode_duration = 0

    def check_movements(self, field):
        global moving
        pressed_keys = pygame.key.get_pressed()

        if game_mode == '3D':
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x != WIDTH // 2:
                self.angle -= (mouse_x - WIDTH // 2) * SENSITIVITY / 5
                pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))

            # 3D relative controls (W/S forward/back, A/D strafe)
            move_vectors = []
            if pressed_keys[pygame.K_w] or pressed_keys[pygame.K_UP]:
                move_vectors.append(self.angle)
            if pressed_keys[pygame.K_s] or pressed_keys[pygame.K_DOWN]:
                move_vectors.append(self.angle + 180)
            if pressed_keys[pygame.K_a]:
                move_vectors.append(self.angle + 90)
            if pressed_keys[pygame.K_d]:
                move_vectors.append(self.angle - 90)

            moving_now = False
            for ang in move_vectors:
                x1 = self.x + self.speed * cos(radians(ang))
                y1 = self.y - self.speed * sin(radians(ang))
                if field.field[int(y1 // TILE_SIZE)][int(x1 // TILE_SIZE)] != 1 and \
                        (x1 // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2 - x1) ** 2 + (y1 // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2 - y1) ** 2 <= TILE_SIZE ** 2:
                    self.x = x1
                    self.y = y1
                    moving = True
                    moving_now = True
                    self.handle_collectibles(field, x1, y1)
                    break
            if not moving_now:
                moving = False
        else:
            # Classic Mode direct cardinal controls (Up, Down, Left, Right)
            move_vector = None
            if pressed_keys[pygame.K_UP]:
                move_vector = 90
                self.angle = 90
            elif pressed_keys[pygame.K_DOWN]:
                move_vector = 270
                self.angle = 270
            elif pressed_keys[pygame.K_LEFT]:
                move_vector = 180
                self.angle = 180
            elif pressed_keys[pygame.K_RIGHT]:
                move_vector = 0
                self.angle = 0

            if move_vector is not None:
                x1 = self.x + self.speed * cos(radians(move_vector))
                y1 = self.y - self.speed * sin(radians(move_vector))
                if field.field[int(y1 // TILE_SIZE)][int(x1 // TILE_SIZE)] != 1:
                    self.x = x1
                    self.y = y1
                    moving = True
                    self.handle_collectibles(field, x1, y1)
                else:
                    moving = False
            else:
                moving = False

    def handle_collectibles(self, field, x1, y1):
        tx, ty = int(x1 // TILE_SIZE), int(y1 // TILE_SIZE)
        if (x1 // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2 - x1) ** 2 + (y1 // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2 - y1) ** 2 <= TILE_SIZE ** 2:
            if field.field[ty][tx] == 0:
                self.score += 1
                field.field[ty][tx] = -1
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('src/point_claim.wav'))
            elif field.field[ty][tx] == 2:
                self.super_mode = True
                self.super_mode_duration = 0
                field.field[ty][tx] = -1
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('src/bonus_claim.wav'))


class RayCaster:
    def draw(self, player, field, sc):
        add_y = sin(time_moving / 5) * 30
        sc.blit(floor, (0, HEIGHT / 2))

        angle0 = player.angle + FOV / 2
        angle_delta = FOV / RAYS_AMOUNT
        to_draw = []
        for ray_cur in range(RAYS_AMOUNT):
            angle_cur = angle0 - ray_cur * angle_delta
            ray_cur_length_total = RAY_LENGTH

            x_tile = player.x // TILE_SIZE * TILE_SIZE
            y_tile = player.y // TILE_SIZE * TILE_SIZE

            sin_a = sin(radians(angle_cur))
            cos_a = cos(radians(angle_cur))

            x_cur, delta_x = (x_tile, -1) if cos_a < 0 else (x_tile + TILE_SIZE, 1)
            y_cur, delta_y = (y_tile, -1) if sin_a > 0 else (y_tile + TILE_SIZE, 1)

            for i in range(0, field.size_x * TILE_SIZE, TILE_SIZE):
                dist_x = (x_cur - player.x) / (cos_a if cos_a != 0 else 0.0001)
                y = player.y - dist_x * sin_a
                ind_x = int((x_cur + delta_x) // TILE_SIZE)
                ind_y = int(y // TILE_SIZE)
                if (ind_x < 0 or ind_x >= field.size_x or ind_y < 0 or ind_y >= field.size_y) or field.field[ind_y][ind_x] == 1:
                    break
                x_cur += delta_x * TILE_SIZE

            for i in range(0, field.size_y * TILE_SIZE, TILE_SIZE):
                dist_y = (player.y - y_cur) / (sin_a if sin_a != 0 else 0.0001)
                x = player.x + dist_y * cos_a
                ind_x = int(x // TILE_SIZE)
                ind_y = int((y_cur + delta_y) // TILE_SIZE)
                if (ind_x < 0 or ind_x >= field.size_x or ind_y < 0 or ind_y >= field.size_y) or field.field[ind_y][ind_x] == 1:
                    break
                y_cur += delta_y * TILE_SIZE

            ray_cur_length_total = min(dist_x, dist_y)

            ray_cur_length_total *= cos(radians(abs(angle_cur - player.angle)))
            angle_in_screen_tan = (WALL_HEIGHT / 2) / ray_cur_length_total
            fragment_height = angle_in_screen_tan * DISTANCE_TO_SCREEN * 2
            fragment_x = ray_cur * WIDTH / RAYS_AMOUNT
            fragment_width = angle_delta / FOV * WIDTH

            k = min(max(RAY_LENGTH - ray_cur_length_total, 0) / (RAY_LENGTH + 500), 1)

            to_draw.append(('rect', ray_cur_length_total, (50 * k, 50 * k, 200 * k), (fragment_x, HEIGHT / 2 - fragment_height / 2 + add_y, fragment_width, fragment_height)))

        return to_draw

    def check_intersection(self, sc, field, x1, y1, x2, y2):
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        cos_a = (x2 - x1) / dist
        sin_a = (y1 - y2) / dist
        for i in range(int(dist)):
            x = int((x1 + i * cos_a) // TILE_SIZE)
            y = int((y1 - i * sin_a) // TILE_SIZE)
            if field.field[y][x] == 1:
                return True
        return False


class Sprite:
    def __init__(self, digit_on_map, type):
        self.digit_in_map = digit_on_map
        self.type = type

    def draw_circles(self, sc, field, player, ray_caster):
        to_draw = []
        for x in range(field.size_x):
            for y in range(field.size_y):
                if field.field[y][x] == 0 or field.field[y][x] == 2:
                    sprite_x = x * TILE_SIZE + TILE_SIZE / 2
                    sprite_y = y * TILE_SIZE + TILE_SIZE / 2
                    if dist_between_point(sprite_x, sprite_y, player.x, player.y) <= 800:
                        dist = ((player.x - (x * TILE_SIZE + TILE_SIZE / 2)) ** 2 + (player.y - (y * TILE_SIZE + TILE_SIZE / 2)) ** 2) ** 0.5
                        angle_p = player.angle % 360
                        dx, dy = x * TILE_SIZE + TILE_SIZE / 2 - player.x, player.y - y * TILE_SIZE - TILE_SIZE / 2

                        theta = degrees(atan2(dy, dx))
                        gamma = theta - angle_p
                        if dx > 0 and 180 <= angle_p <= 360 or dx < 0 and dy < 0:
                            gamma += 360

                        angle_delta = FOV / RAYS_AMOUNT
                        delta_rays = int(gamma / angle_delta)
                        center_ray = RAYS_AMOUNT // 2 - 1
                        current_ray = center_ray + delta_rays
                        dist *= cos(radians(FOV / 2 - current_ray * angle_delta))

                        if 0 <= current_ray <= RAYS_AMOUNT - 1:
                            angle_in_screen_tan = (WALL_HEIGHT / 2) / dist
                            fragment_height = angle_in_screen_tan * DISTANCE_TO_SCREEN * 2
                            shift = fragment_height / 2 * 1.4

                            add_y = sin(time_moving / 5) * 30
                            sprite_pos_on_screen = (WIDTH - current_ray * (WIDTH // RAYS_AMOUNT), HEIGHT / 2 - fragment_height / 2 + shift + add_y)
                            c = min(int(255 / dist * 50), 255)
                            if 0 <= sprite_pos_on_screen[0] < WIDTH and 0 <= sprite_pos_on_screen[1] < HEIGHT:
                                if field.field[y][x] == 0:
                                    color = (c, c, 0)
                                    to_draw.append(('circle', dist, color, sprite_pos_on_screen, fragment_height / 10))
                                elif field.field[y][x] == 2:
                                    color = (c, 0, 0)
                                    to_draw.append(('circle', dist, color, sprite_pos_on_screen, fragment_height / 7))

        return to_draw

    def draw_npc(self, sc, field, player, ray_caster, NPC_s):
        to_draw = []
        for npc in NPC_s:
            dist = ((player.x - npc.x) ** 2 + (player.y - npc.y) ** 2) ** 0.5
            angle_p = player.angle % 360
            dx, dy = npc.x - player.x, player.y - npc.y

            theta = degrees(atan2(dy, dx))
            gamma = theta - angle_p
            if dx > 0 and 180 <= angle_p <= 360 or dx < 0 and dy < 0:
                gamma += 360

            angle_delta = FOV / RAYS_AMOUNT
            delta_rays = int(gamma / angle_delta)
            center_ray = RAYS_AMOUNT // 2 - 1
            current_ray = center_ray + delta_rays
            dist *= cos(radians(FOV / 2 - current_ray * angle_delta))

            if 0 <= current_ray <= RAYS_AMOUNT - 1:
                angle_in_screen_tan = (WALL_HEIGHT / 2) / dist
                fragment_height = angle_in_screen_tan * DISTANCE_TO_SCREEN * 2
                shift = 0

                add_y = sin(time_moving / 5) * 30
                sprite_pos_on_screen = (WIDTH - current_ray * (WIDTH // RAYS_AMOUNT) - fragment_height / 2, HEIGHT / 2 - fragment_height / 2 + shift + add_y)

                if 0 <= sprite_pos_on_screen[0] < WIDTH and 0 <= sprite_pos_on_screen[1] < HEIGHT:
                    if not player.super_mode:
                        to_draw.append(('sprite', dist, npc.sprite, sprite_pos_on_screen, fragment_height))
                    else:
                        to_draw.append(('sprite', dist, npc.sprite_super, sprite_pos_on_screen, fragment_height))

        return to_draw

    def draw(self, sc, field, player, ray_caster, NPC_s):
        if self.type == 'circle':
            return self.draw_circles(sc, field, player, ray_caster)
        elif self.type == 'npc':
            return self.draw_npc(sc, field, player, ray_caster, NPC_s)


class App:
    def create_window(self):
        global WIDTH, HEIGHT
        self.sc = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.run = True
        self.beat_duration = 100
        self.beat_duration_counter = 0
        self.danger_volume = 0
        self.show_plus_10 = False
        self.show_plus_10_duration = 0

    def check_events(self):
        global pause, pause_duration_counter, master_volume, WIDTH, HEIGHT, floor
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if pause:
                    if WIDTH / 2 - 200 <= x <= WIDTH / 2 + 200 and HEIGHT / 2 - 120 <= y <= HEIGHT / 2 - 30:
                        pause = False
                        if game_mode == '3D':
                            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
                            pygame.mouse.set_visible(False)
                            pygame.event.set_grab(True)
                    elif WIDTH / 2 - 200 <= x <= WIDTH / 2 + 200 and HEIGHT / 2 + 20 <= y <= HEIGHT / 2 + 110:
                        self.run = False
                        for i in range(7):
                            pygame.mixer.Channel(i).stop()
                        return 'exit'
                    elif WIDTH / 2 - 96 <= x <= WIDTH / 2 + 96 and HEIGHT / 2 + 200 <= y <= HEIGHT / 2 + 242:
                        global SENSITIVITY
                        SENSITIVITY = (x - (WIDTH / 2 - 96)) / 192
                    elif WIDTH / 2 - 96 <= x <= WIDTH / 2 + 96 and HEIGHT / 2 + 290 <= y <= HEIGHT / 2 + 332:
                        master_volume = (x - (WIDTH / 2 - 96)) / 192
                        pygame.mixer.set_num_channels(8)
                        for i in range(7):
                            pygame.mixer.Channel(i).set_volume(master_volume)

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_ESCAPE] and pause_duration_counter >= 20:
            pause = not pause
            pause_duration_counter = 0
            if pause:
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
            else:
                if game_mode == '3D':
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))

    def update_window(self):
        global time, time_moving, pause_duration_counter
        pygame.display.flip()
        self.clock.tick(FPS)
        time += 1
        if moving:
            time_moving += 1
        self.beat_duration_counter += 1
        pygame.mixer.Channel(1).set_volume(self.danger_volume * master_volume)
        if self.beat_duration_counter >= self.beat_duration:
            if not pause:
                pygame.mixer.Channel(3).play(pygame.mixer.Sound('src/heart_beat.wav'))
            self.beat_duration_counter = 0

        pygame.mixer.Channel(2).set_volume(max(1 - self.danger_volume * 2, 0) * master_volume)

        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('src/danger_theme.mp3'))

        pause_duration_counter += 1

    def draw_sprites(self, sc, field, player, sprites, ray_caster, NPC_s):
        ans = []
        for sprite in sprites:
            ans += sprite.draw(self.sc, field, player, ray_caster, NPC_s)
        return ans

    def draw(self, to_draw):
        for el in to_draw:
            if el[0] == 'circle':
                pygame.draw.circle(self.sc, el[2], el[3], el[4])
            elif el[0] == 'rect':
                pygame.draw.rect(self.sc, el[2], el[3])
            elif el[0] == 'sprite':
                self.sc.blit(pygame.transform.scale(el[2], (el[4], el[4])), el[3])

    def draw_pause(self):
        x, y = pygame.mouse.get_pos()
        color_delta1 = 0
        color_delta2 = 0

        if WIDTH / 2 - 200 <= x <= WIDTH / 2 + 200 and HEIGHT / 2 - 120 <= y <= HEIGHT / 2 - 30:
            color_delta1 = 50
        elif WIDTH / 2 - 200 <= x <= WIDTH / 2 + 200 and HEIGHT / 2 + 20 <= y <= HEIGHT / 2 + 110:
            color_delta2 = 50

        pygame.draw.rect(self.sc, (180 - color_delta1, 0, 0), (WIDTH / 2 - 200, HEIGHT / 2 - 120, 400, 80), border_radius=10)
        print_text(self.sc, WIDTH / 2, HEIGHT / 2 - 110, 'Continue', 50, (255 - color_delta1, 255 - color_delta1, 255 - color_delta1), align='center', font='src/font3.ttf')

        pygame.draw.rect(self.sc, (180 - color_delta2, 0, 0), (WIDTH / 2 - 200, HEIGHT / 2 + 20, 400, 80), border_radius=10)
        print_text(self.sc, WIDTH / 2, HEIGHT / 2 + 30, 'Main menu', 50, (255 - color_delta2, 255 - color_delta2, 255 - color_delta2), align='center', font='src/font3.ttf')

        print_text(self.sc, WIDTH / 2, HEIGHT / 2 + 165, 'Sensitivity', 25, (255, 255, 255), align='center', font='src/font3.ttf')
        pygame.draw.rect(self.sc, (255, 255, 255), (WIDTH / 2 - 100, HEIGHT / 2 + 196, 200, 50), 2)
        pygame.draw.rect(self.sc, (255, 255, 255), (WIDTH / 2 - 96, HEIGHT / 2 + 200, 192 * SENSITIVITY, 42))

        print_text(self.sc, WIDTH / 2, HEIGHT / 2 + 255, 'Master Volume', 25, (255, 255, 255), align='center', font='src/font3.ttf')
        pygame.draw.rect(self.sc, (255, 255, 255), (WIDTH / 2 - 100, HEIGHT / 2 + 286, 200, 50), 2)
        pygame.draw.rect(self.sc, (0, 200, 0), (WIDTH / 2 - 96, HEIGHT / 2 + 290, 192 * master_volume, 42))

    def main(self):
        global pause, score
        pause = False
        if game_mode == '3D':
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)

        field = Field()

        start_x = 9 * TILE_SIZE + TILE_SIZE // 2
        start_y = 13 * TILE_SIZE + TILE_SIZE // 2
        player = Player(start_x, start_y)

        ray_caster = RayCaster()
        NPC_s = [NPC(850, 950, pygame.image.load('src/ghosts/ghost1.png'), pygame.image.load('src/ghosts/ghost1_super.png'), 'red'),
                 NPC(900, 950, pygame.image.load('src/ghosts/ghost2.png'), pygame.image.load('src/ghosts/ghost2_super.png'), 'blue'),
                 NPC(950, 950, pygame.image.load('src/ghosts/ghost3.png'), pygame.image.load('src/ghosts/ghost3_super.png'), 'yellow'),
                 NPC(1000, 950, pygame.image.load('src/ghosts/ghost4.png'), pygame.image.load('src/ghosts/ghost4_super.png'), 'pink')]
        minimap_frames = [
            pygame.transform.scale(pygame.image.load('src/pacman/frame1.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame2.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame3.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame4.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame5.png'),  (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame4.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame3.png'), (20, 20)),
            pygame.transform.scale(pygame.image.load('src/pacman/frame2.png'), (20, 20)),
        ]

        sprites = [Sprite(0, 'circle'), Sprite(None, 'npc')]
        background_sounds = [
            pygame.mixer.Sound('src/background_audio/1.oga'),
            pygame.mixer.Sound('src/background_audio/2.oga'),
            pygame.mixer.Sound('src/background_audio/3.oga'),
            pygame.mixer.Sound('src/background_audio/4.oga'),
            pygame.mixer.Sound('src/background_audio/5.oga'),
            pygame.mixer.Sound('src/background_audio/6.oga'),
            pygame.mixer.Sound('src/background_audio/7.oga'),
            pygame.mixer.Sound('src/background_audio/8.oga'),
            pygame.mixer.Sound('src/background_audio/9.ogg')
        ]
        pygame.mixer.Channel(0).set_volume(0.05 * master_volume)
        pygame.mixer.Channel(1).play(pygame.mixer.Sound('src/danger_theme.mp3'))
        pygame.mixer.Channel(1).set_volume(0)
        pygame.mixer.Channel(4).set_volume(0.1 * master_volume)
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('src/pacman_sound.mp3'))
        pygame.mixer.Channel(5).set_volume(1 * master_volume)
        pygame.mixer.Channel(5).play(pygame.mixer.Sound('src/opening.mp3'))
        pygame.mixer.Channel(6).set_volume(0.2 * master_volume)
        global score
        while self.run:
            res = self.check_events()
            if res == 'exit':
                return res
            if player.score >= points:
                for i in range(7):
                    pygame.mixer.Channel(i).stop()

                score += player.score + player.score_super
                return 'win'
            if not pause:
                player.check_movements(field)

            self.sc.fill((0, 0, 0))
            if game_mode == '3D':
                to_draw = []
                to_draw += ray_caster.draw(player, field, self.sc)
                to_draw += self.draw_sprites(self.sc, field, player, sprites, ray_caster, NPC_s)
                to_draw = sorted(to_draw, key=lambda x: x[1], reverse=True)
                self.draw(to_draw)
                field.draw_minimap(self.sc, player, minimap_frames, NPC_s)
            else:
                field.draw_classic(self.sc, player, minimap_frames, NPC_s)

            print_text(self.sc, WIDTH / 2, 10, f'{player.score}', 70, (255, 255, 0), align='center', font='src/font2.ttf')
            print_text(self.sc, WIDTH - 10, 10, str(int(self.clock.get_fps())), 50, (255, 0, 0), align='right')
            if self.show_plus_10:
                self.show_plus_10_duration += 1
                print_text(self.sc, WIDTH / 2, HEIGHT / 4, '+10', 30, (180, 180, 180), align='center', font='src/font4.ttf')
                if self.show_plus_10_duration >= FPS * 3:
                    self.show_plus_10 = False
                    self.show_plus_10_duration = 0
            if time <= FPS * 5:
                print_text(self.sc, WIDTH / 2, HEIGHT / 2 - 100, f'Level {level}', 100, (255, 0, 0), align='center', font='src/font2.ttf')
                print_text(self.sc, WIDTH / 2, HEIGHT / 2, f'Collect {points} points', 100, (180, 180, 180), align='center', font='src/font2.ttf')

            hunt = False
            for npc in NPC_s:
                if dist_between_point(player.x, player.y, npc.x, npc.y) <= 70:
                    if not player.super_mode:
                        self.run = False
                        for i in range(7):
                            pygame.mixer.Channel(i).stop()

                        score += player.score + player.score_super
                        return ('lose', npc.color)
                    else:
                        pygame.mixer.Channel(6).play(pygame.mixer.Sound('src/catch.wav'))
                        if not npc.run_away:
                            player.score_super += 10
                            self.show_plus_10 = True
                        npc.run_away = True
                        npc.speed = 4
                elif npc.hunt:
                    hunt = True
                    npc.speed = 3 + level / 3
                else:
                    npc.speed = 2
                if not pause:
                    npc.move(self.sc, field, player, ray_caster)
                if player.super_mode and game_mode == '3D':
                    pygame.draw.circle(self.sc, (255, 0, 0), (npc.x / 5, npc.y / 5), 10)

            if hunt:
                self.danger_volume = max(self.danger_volume, 0.02)
                self.danger_volume *= 1.07
            else:
                self.danger_volume = min(self.danger_volume, 1)
                self.danger_volume /= 1.07

            dist = None
            for npc in NPC_s:
                if dist is not None:
                    dist = min(dist, dist_between_point(player.x, player.y, npc.x, npc.y))
                else:
                    dist = dist_between_point(player.x, player.y, npc.x, npc.y)
            self.beat_duration = max(dist / 12, 20)

            if random.randint(1, 300) == 1 and not pygame.mixer.Channel(2).get_busy():
                pygame.mixer.Channel(2).play(random.choice(background_sounds))
            if moving:
                pygame.mixer.Channel(4).unpause()
            else:
                pygame.mixer.Channel(4).pause()
            if not pygame.mixer.Channel(4).get_busy():
                pygame.mixer.Channel(4).play(pygame.mixer.Sound('src/pacman_sound.mp3'))

            if pause:
                self.draw_pause()
            player.super_mode_duration += 1
            super_duration_limit = FPS * 5 if difficulty == 'Hard' else (FPS * 15 if difficulty == 'Easy' else FPS * 10)
            if player.super_mode_duration >= super_duration_limit:
                player.super_mode = False
            self.update_window()


def draw_buttons_main(sc, color1, color2):
    print_text(sc1, WIDTH * 0.70, HEIGHT * 0.1, 'Menu', 80, (255, 255, 255), font='src/font1.ttf')

    print_text(sc1, WIDTH * 0.70, HEIGHT * 0.1 + 110, 'Start', 60, color1, font='src/font2.ttf')
    print_text(sc1, WIDTH * 0.70 + 130, HEIGHT * 0.1 + 125, f'Level {level}', 40, (180, 180, 180), font='src/font2.ttf')

    print_text(sc1, WIDTH * 0.70, HEIGHT * 0.1 + 180, f'Mode: {game_mode}', 50, (200, 200, 50), font='src/font2.ttf')

    diff_color = (100, 255, 100) if difficulty == 'Easy' else ((255, 255, 100) if difficulty == 'Normal' else (255, 100, 100))
    print_text(sc1, WIDTH * 0.70, HEIGHT * 0.1 + 250, f'Diff: {difficulty}', 50, diff_color, font='src/font2.ttf')

    print_text(sc1, WIDTH * 0.70, HEIGHT * 0.1 + 320, 'Quit', 60, color2, font='src/font2.ttf')


def draw_main_menu():
    global game_mode, difficulty
    bg = pygame.transform.scale(pygame.image.load('src/main_menu_bg.png'), (WIDTH, HEIGHT))
    manual = pygame.transform.scale(pygame.image.load('src/manual.png'), (HEIGHT * 0.4 * 0.73, HEIGHT * 0.4))
    run = True
    pygame.mixer.Channel(0).play(pygame.mixer.Sound('src/background_music.mp3'))
    pygame.mixer.Channel(0).set_volume(0.2 * master_volume)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH * 0.70 <= x <= WIDTH * 0.70 + 120 and HEIGHT * 0.1 + 110 <= y <= HEIGHT * 0.1 + 160:
                    run = False
                    pygame.mixer.Channel(0).stop()
                elif WIDTH * 0.70 <= x <= WIDTH * 0.70 + 250 and HEIGHT * 0.1 + 180 <= y <= HEIGHT * 0.1 + 230:
                    game_mode = 'Classic' if game_mode == '3D' else '3D'
                elif WIDTH * 0.70 <= x <= WIDTH * 0.70 + 250 and HEIGHT * 0.1 + 250 <= y <= HEIGHT * 0.1 + 300:
                    if difficulty == 'Easy':
                        difficulty = 'Normal'
                    elif difficulty == 'Normal':
                        difficulty = 'Hard'
                    else:
                        difficulty = 'Easy'
                elif WIDTH * 0.70 <= x <= WIDTH * 0.70 + 100 and HEIGHT * 0.1 + 320 <= y <= HEIGHT * 0.1 + 370:
                    exit()

        sc1.blit(bg, (0, 0))

        print_text(sc1, WIDTH * 0.15, HEIGHT * 0.1, 'PacMan', 100, (190, 190, 50), font='src/font4.ttf')
        print_text(sc1, WIDTH * 0.15 + 310, HEIGHT * 0.1, '.exe', 100, (190, 0, 0), font='src/font4.ttf')
        print_text(sc1, WIDTH * 0.25, HEIGHT - 200, 'Collect points in this maze', 30, (150, 150, 150), align='center', font='src/font2.ttf')
        print_text(sc1, WIDTH * 0.25, HEIGHT - 150, 'Switch between 3D and Classic mode from the menu!', 30, (150, 150, 150), align='center', font='src/font2.ttf')

        color1 = (255, 0, 0)
        color2 = (255, 0, 0)
        x, y = pygame.mouse.get_pos()
        if WIDTH * 0.70 <= x <= WIDTH * 0.70 + 120 and HEIGHT * 0.1 + 110 <= y <= HEIGHT * 0.1 + 160:
            color1 = (180, 0, 0)
        if WIDTH * 0.70 <= x <= WIDTH * 0.70 + 100 and HEIGHT * 0.1 + 320 <= y <= HEIGHT * 0.1 + 370:
            color2 = (180, 0, 0)

        draw_buttons_main(sc1, color1, color2)
        sc1.blit(manual, (WIDTH - manual.get_width() - 10, HEIGHT - manual.get_height() - 10))
        pygame.display.flip()
        clock1.tick(FPS)


def draw_screamer(color):
    pygame.mixer.Channel(0).set_volume(0.4 * master_volume)
    pygame.mixer.Channel(0).play(pygame.mixer.Sound('src/screamer.mp3'))
    delta_y = 200

    if color == 'red':
        image = pygame.image.load('src/ghosts/ghost1.png')
    elif color == 'blue':
        image = pygame.image.load('src/ghosts/ghost2.png')
    elif color == 'yellow':
        image = pygame.image.load('src/ghosts/ghost3.png')
    else:
        image = pygame.image.load('src/ghosts/ghost4.png')
    image = pygame.transform.scale(image, (HEIGHT, HEIGHT))
    bg = pygame.transform.scale(pygame.image.load('src/screamer_bg.png'), (WIDTH, HEIGHT))
    size = HEIGHT
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        sc1.blit(bg, (0, 0))
        sc1.blit(image, (WIDTH // 2 - image.get_width() // 2 + random.randint(-50, 50) * (delta_y / 200), delta_y - 200))
        image = pygame.transform.scale(image, (size, size))
        delta_y *= 0.95
        size += 10 * (delta_y / 200)
        if delta_y <= 1:
            run = False
        pygame.display.flip()
        clock1.tick(FPS)


def draw_lose_screen():
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x >= WIDTH / 2 - 150 and x <= WIDTH / 2 + 150 and y >= HEIGHT - 200 and y <= HEIGHT - 100:
                    run = False

        sc1.fill((0, 0, 0))

        print_text(sc1, WIDTH / 2, HEIGHT * 0.1, 'Game Over', 100, (180, 0, 0), align='center', font='src/font3.ttf')
        print_text(sc1, WIDTH / 2, HEIGHT * 0.5, 'Score ' + str(score), 100, (200, 0, 0), align='center', font='src/font2.ttf')
        print_text(sc1, WIDTH / 2, HEIGHT * 0.4, f'Reached level {level}', 100, (200, 0, 0), align='center', font='src/font2.ttf')

        x, y = pygame.mouse.get_pos()
        delta_color = 0
        if x >= WIDTH / 2 - 150 and x <= WIDTH / 2 + 150 and y >= HEIGHT - 200 and y <= HEIGHT - 100:
            delta_color = 50
        print_text(sc1, WIDTH / 2, HEIGHT - 200, 'Continue', 100, (180 - delta_color, 180 - delta_color, 180 - delta_color), align='center', font='src/font3.ttf')

        pygame.display.flip()
        clock1.tick(FPS)


def draw_win_screen():
    run = True
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x >= WIDTH / 2 - 150 and x <= WIDTH / 2 + 150 and y >= HEIGHT * 0.85 and y <= HEIGHT * 0.85 + 100:
                    run = False

        sc1.fill((0, 0, 0))

        print_text(sc1, WIDTH / 2, HEIGHT * 0.1, f'Level {level - 1} complete', 100, (200, 200, 200), align='center', font='src/font3.ttf')
        print_text(sc1, WIDTH / 2 - 200, HEIGHT / 2 - 50, 'Time:', 100, (200, 0, 0), align='left', font='src/font4.ttf')
        surf = print_text(sc1, WIDTH / 2 + 20, HEIGHT / 2 - 50, str(time // FPS // 60), 100, (180, 180, 180), align='left', font='src/font4.ttf')
        print_text(sc1, WIDTH / 2 + 20 + surf.get_width() + 10, HEIGHT / 2 - 50, 'm', 100, (200, 0, 0), align='left', font='src/font4.ttf')
        surf1 = print_text(sc1, WIDTH / 2 + 120 + surf.get_width(), HEIGHT / 2 - 50, str((time // FPS) % 60), 100, (180, 180, 180), align='left', font='src/font4.ttf')
        print_text(sc1, WIDTH / 2 + 140 + surf.get_width() + surf1.get_width(), HEIGHT / 2 - 50, 's', 100, (200, 0, 0), align='left', font='src/font4.ttf')

        print_text(sc1, WIDTH / 2, HEIGHT / 2 + 150, f'score {score}', 100, (200, 0, 0), align='center', font='src/font2.ttf')

        x, y = pygame.mouse.get_pos()
        delta_color = 0
        if x >= WIDTH / 2 - 150 and x <= WIDTH / 2 + 150 and y >= HEIGHT * 0.85 and y <= HEIGHT * 0.85 + 100:
            delta_color = 50
        print_text(sc1, WIDTH / 2, HEIGHT * 0.85, 'Continue', 100, (180 - delta_color, 180 - delta_color, 180 - delta_color), align='center', font='src/font3.ttf')

        pygame.display.flip()
        clock1.tick(FPS)


app = App()
sc1 = pygame.display.set_mode((WIDTH, HEIGHT))
clock1 = pygame.time.Clock()
result = None

while True:
    pygame.mixer.init()
    if result is None or result == 'exit':
        draw_main_menu()
        time = 0
    elif type(result) == tuple:
        draw_screamer(result[1])
        draw_lose_screen()
        level = 1
        score = 0
        draw_main_menu()
    else:
        level += 1
        draw_win_screen()
        time = 0
        super_points = max(1, super_points - 1)
        points1 = 174 - super_points
        points = int(100 + min((level - 1) / 10, 1) * (points1 - 100))

    app.create_window()
    result = app.main()
