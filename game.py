"""Relic Rush, a small top-down roguelike built with Pygame Zero."""

import math
import random

import pgzrun
from pygame import Rect
from pgzero.builtins import Actor, keyboard, music, sounds
from pgzero.game import exit as quit_game

TILE = 48
HUD_HEIGHT = 48
FRAME_COUNT = 4
IDLE_FRAME_TIME = 0.22
WALK_FRAME_TIME = 0.11
COLLISION_DISTANCE = 28

# Columns 0-14, rows 0-10.
# P start, C coin, S slime, B bat, R relic, E exit.
# Doors on rows 3, 5, and 8 are safe places to wait outside each guard's room.
LEVEL = (
    "###############",
    "#P......C.....#",
    "#.............#",
    "#####.#########",
    "#S............#",
    "###########.###",
    "#.............#",
    "#............B#",
    "#####.#########",
    "#R....C....E..#",
    "###############",
)

SLIME_ROOM = (1, 13, 4, 4)
BAT_ROOM = (1, 13, 6, 7)

WIDTH = len(LEVEL[0]) * TILE
HEIGHT = len(LEVEL) * TILE + HUD_HEIGHT
TITLE = "Relic Rush"


def smoothstep(amount):
    amount = min(1.0, max(0.0, amount))
    return amount * amount * (3.0 - 2.0 * amount)


def cell_center(cell_x, cell_y):
    return cell_x * TILE + TILE // 2, cell_y * TILE + TILE // 2


def is_blocked(cell_x, cell_y):
    if cell_y < 0 or cell_y >= len(LEVEL):
        return True
    if cell_x < 0 or cell_x >= len(LEVEL[0]):
        return True
    return LEVEL[cell_y][cell_x] == "#"


def find_cells(symbol):
    found = []
    for row_index, row in enumerate(LEVEL):
        for column, char in enumerate(row):
            if char == symbol:
                found.append((column, row_index))
    return found


def find_cell(symbol):
    matches = find_cells(symbol)
    if len(matches) != 1:
        raise ValueError(f"Expected one {symbol} on the map.")
    return matches[0]


def walkable_row(row, min_x, max_x):
    return [
        (column, row)
        for column in range(min_x, max_x + 1)
        if not is_blocked(column, row)
    ]


def build_ping_pong(min_x, max_x, row):
    cells = walkable_row(row, min_x, max_x)
    return cells + list(reversed(cells[1:-1]))


def build_room_loop(min_x, max_x, min_y, max_y):
    top = walkable_row(min_y, min_x, max_x)
    bottom = list(reversed(walkable_row(max_y, min_x, max_x)))
    return top + bottom


def read_direction():
    dx = 0
    dy = 0
    if keyboard.left or keyboard.a:
        dx -= 1
    if keyboard.right or keyboard.d:
        dx += 1
    if keyboard.up or keyboard.w:
        dy -= 1
    if keyboard.down or keyboard.s:
        dy += 1
    if dx and dy:
        dy = 0
    return dx, dy


def play_effect(name):
    if world.sound_enabled:
        getattr(sounds, name).play()


class SpriteAnimator:
    """Plays an idle cycle or a walk cycle from named sprite frames."""

    def __init__(self, kind):
        self.kind = kind
        self.facing = "down"
        self.frame_index = 0
        self.elapsed = 0.0
        self.moving = False

    def face_toward(self, dx, dy):
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

    def update(self, dt, moving):
        if moving != self.moving:
            self.moving = moving
            self.frame_index = 0
            self.elapsed = 0.0
        interval = WALK_FRAME_TIME if moving else IDLE_FRAME_TIME
        self.elapsed += dt
        while self.elapsed >= interval:
            self.elapsed -= interval
            self.frame_index = (self.frame_index + 1) % FRAME_COUNT

    def image_name(self):
        state = "walk" if self.moving else "idle"
        return f"{self.kind}_{state}_{self.facing}_{self.frame_index}"


class Character:
    """Moves one grid cell at a time, with a smooth in-between animation."""

    def __init__(self, cell, kind, move_duration):
        self.cell_x, self.cell_y = cell
        self.target_x = self.cell_x
        self.target_y = self.cell_y
        self.move_duration = move_duration
        self.progress = 1.0
        self.moving = False
        self.pixel_x, self.pixel_y = cell_center(self.cell_x, self.cell_y)
        self.origin_x = self.pixel_x
        self.origin_y = self.pixel_y
        self.animator = SpriteAnimator(kind)
        self.actor = Actor(self.animator.image_name(), pos=(self.pixel_x, self.pixel_y))

    def begin_move(self, cell_x, cell_y):
        if is_blocked(cell_x, cell_y):
            return False
        if (cell_x, cell_y) == (self.cell_x, self.cell_y):
            return False
        self.target_x = cell_x
        self.target_y = cell_y
        self.origin_x = self.pixel_x
        self.origin_y = self.pixel_y
        self.progress = 0.0
        self.moving = True
        self.animator.face_toward(cell_x - self.cell_x, cell_y - self.cell_y)
        return True

    def update(self, dt):
        arrived = False
        if self.moving:
            self.progress += dt / self.move_duration
            if self.progress >= 1.0:
                self.progress = 1.0
                self.moving = False
                self.cell_x = self.target_x
                self.cell_y = self.target_y
                self.pixel_x, self.pixel_y = cell_center(self.cell_x, self.cell_y)
                arrived = True
            else:
                eased = smoothstep(self.progress)
                end_x, end_y = cell_center(self.target_x, self.target_y)
                self.pixel_x = self.origin_x + (end_x - self.origin_x) * eased
                self.pixel_y = self.origin_y + (end_y - self.origin_y) * eased
        self.animator.update(dt, self.moving)
        self.actor.image = self.animator.image_name()
        self.actor.pos = (self.pixel_x, self.pixel_y)
        return arrived

    def distance_to(self, other):
        return math.hypot(self.pixel_x - other.pixel_x, self.pixel_y - other.pixel_y)


class Player(Character):
    """The hero. Arrow keys or WASD request the next tile."""

    def __init__(self, cell):
        super().__init__(cell, "hero", 0.15)

    def update(self, dt):
        if not self.moving:
            dx, dy = read_direction()
            if (dx or dy) and self.begin_move(self.cell_x + dx, self.cell_y + dy):
                play_effect("step")
        return super().update(dt)


class Enemy(Character):
    """A guard that patrols a path and never leaves its own room."""

    def __init__(self, cell, kind, path, area, move_duration, pause_range):
        super().__init__(cell, kind, move_duration)
        self.path = list(path)
        self.area = area
        self.pause_range = pause_range
        self.pause_timer = random.uniform(*pause_range)
        self.path_index = (self.path.index(cell) + 1) % len(self.path)
        self.area_min_x = min(x for x, _y in self.path)
        self.area_max_x = max(x for x, _y in self.path)
        next_x, next_y = self.path[self.path_index]
        self.animator.face_toward(next_x - self.cell_x, next_y - self.cell_y)
        self._check_path()

    def _check_path(self):
        min_x, max_x, min_y, max_y = self.area
        for cell_x, cell_y in self.path:
            if not (min_x <= cell_x <= max_x and min_y <= cell_y <= max_y):
                raise ValueError(f"{self.animator.kind} patrol leaves its room.")
            if is_blocked(cell_x, cell_y):
                raise ValueError(f"{self.animator.kind} patrol hits a wall.")

    def _step_along_path(self):
        next_x, next_y = self.path[self.path_index]
        if self.begin_move(next_x, next_y):
            self.path_index = (self.path_index + 1) % len(self.path)

    def _at_horizontal_edge(self):
        return self.cell_x in (self.area_min_x, self.area_max_x)

    def update(self, dt):
        if not self.moving:
            if self.pause_timer > 0:
                self.pause_timer -= dt
            if self.pause_timer <= 0:
                self._step_along_path()
        arrived = super().update(dt)
        if arrived and self._at_horizontal_edge():
            self.pause_timer = random.uniform(*self.pause_range)
        return arrived


class MenuPreview:
    """Shows idle and walk cycles on the main menu."""

    def __init__(self, kind, pos, phase):
        self.animator = SpriteAnimator(kind)
        self.actor = Actor(self.animator.image_name(), pos=pos)
        self.timer = phase

    def update(self, dt):
        self.timer += dt
        self.animator.facing = ("down", "right", "up", "left")[int(self.timer / 1.5) % 4]
        moving = int(self.timer / 1.5) % 2 == 1
        self.animator.update(dt, moving)
        self.actor.image = self.animator.image_name()


class MenuButton:
    """A clickable rectangle with a label."""

    def __init__(self, rect, label, action):
        self.rect = rect
        self.label = label
        self.action = action

    def draw(self, mouse_position):
        hovered = self.rect.collidepoint(mouse_position)
        fill = (72, 134, 214) if hovered else (40, 84, 156)
        screen.draw.filled_rect(self.rect, fill)
        screen.draw.rect(self.rect, (214, 228, 255))
        screen.draw.text(
            self.label,
            center=self.rect.center,
            fontsize=30,
            color="white",
        )


class Game:
    """Menu, dungeon, pickups, and the win/lose rules."""

    def __init__(self):
        self.state = "menu"
        self.sound_enabled = True
        self.audio_started = False
        self.mouse_position = (0, 0)
        self.elapsed = 0.0
        self.hint = ""
        self.player = None
        self.enemies = []
        self.coins = set()
        self.coins_collected = 0
        self.total_coins = len(find_cells("C"))
        self.relic_collected = False
        self.relic_cell = find_cell("R")
        self.exit_cell = find_cell("E")
        self.slime_area = set()
        self.bat_area = set()
        self.previews = [
            MenuPreview("hero", (180, 500), random.uniform(0, 1)),
            MenuPreview("slime", (360, 500), random.uniform(1, 2)),
            MenuPreview("bat", (540, 500), random.uniform(2, 3)),
        ]

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            music.set_volume(0.35)
            music.play("theme")
        else:
            music.stop()

    def go_menu(self):
        self.state = "menu"
        self.hint = ""

    def start(self):
        slime_path = build_ping_pong(*SLIME_ROOM[:3])
        bat_path = build_room_loop(*BAT_ROOM)
        if set(slime_path) & set(bat_path):
            raise ValueError("Enemy rooms overlap.")
        self.slime_area = set(slime_path)
        self.bat_area = set(bat_path)
        self.player = Player(find_cell("P"))
        self.enemies = [
            Enemy(find_cell("S"), "slime", slime_path, SLIME_ROOM, 0.34, (0.7, 1.15)),
            Enemy(find_cell("B"), "bat", bat_path, BAT_ROOM, 0.22, (0.35, 0.65)),
        ]
        self.coins = set(find_cells("C"))
        self.coins_collected = 0
        self.relic_collected = False
        self.hint = ""
        self.elapsed = 0.0
        self.state = "playing"

    def buttons(self):
        if self.state == "menu":
            if self.sound_enabled:
                sound_label = "Müziği ve Sesleri Kapat"
            else:
                sound_label = "Müziği ve Sesleri Aç"
            return [
                MenuButton(Rect(160, 168, 400, 50), "Oyunu Başlat", self.start),
                MenuButton(Rect(160, 232, 400, 50), sound_label, self.toggle_sound),
                MenuButton(Rect(160, 296, 400, 50), "Çıkış", quit_game),
            ]
        if self.state in ("won", "lost"):
            return [
                MenuButton(Rect(220, 300, 280, 48), "Tekrar Oyna", self.start),
                MenuButton(Rect(220, 362, 280, 48), "Ana Menü", self.go_menu),
            ]
        return []

    def update(self, dt):
        self.elapsed += dt
        if not self.audio_started:
            self.audio_started = True
            if self.sound_enabled:
                music.set_volume(0.35)
                music.play("theme")
        if self.state == "menu":
            for preview in self.previews:
                preview.update(dt)
            return
        if self.state != "playing":
            return
        self.player.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)
        if self._player_was_caught():
            self.state = "lost"
            play_effect("hit")
            return
        self._collect_items()
        self._check_exit()

    def _player_was_caught(self):
        return any(
            self.player.distance_to(enemy) < COLLISION_DISTANCE
            for enemy in self.enemies
        )

    def _collect_items(self):
        if self.player.moving:
            return
        cell = (self.player.cell_x, self.player.cell_y)
        if cell in self.coins:
            self.coins.remove(cell)
            self.coins_collected += 1
            play_effect("coin")
        if cell == self.relic_cell and not self.relic_collected:
            self.relic_collected = True
            play_effect("relic")

    def _check_exit(self):
        self.hint = ""
        if self.player.moving:
            return
        if (self.player.cell_x, self.player.cell_y) != self.exit_cell:
            return
        if self.relic_collected:
            self.state = "won"
            play_effect("win")
        else:
            self.hint = "Kapı kilitli. Önce yadigârı al."

    def floor_name(self, cell_x, cell_y, char):
        if char == "#":
            return "wall"
        variant = (cell_x + cell_y) % 2
        if (cell_x, cell_y) in self.slime_area:
            return f"floor_slime_{variant}"
        if (cell_x, cell_y) in self.bat_area:
            return f"floor_bat_{variant}"
        return f"floor_{variant}"

    def draw(self):
        if self.state == "menu":
            self._draw_menu()
        elif self.state in ("won", "lost"):
            self._draw_world()
            self._draw_end_panel()
        else:
            self._draw_world()

    def _draw_menu(self):
        screen.fill((16, 20, 32))
        screen.draw.rect(Rect(16, 16, WIDTH - 32, HEIGHT - 32), (48, 60, 92))
        screen.draw.text(
            "RELIC RUSH",
            center=(WIDTH // 2, 72),
            fontsize=64,
            color=(255, 210, 96),
        )
        screen.draw.text(
            "Üstten bakışlı roguelike",
            center=(WIDTH // 2, 124),
            fontsize=26,
            color=(180, 196, 220),
        )
        for button in self.buttons():
            button.draw(self.mouse_position)
        screen.draw.text(
            "Ok tuşları veya WASD bir kare ilerletir.",
            center=(WIDTH // 2, 390),
            fontsize=22,
            color=(176, 190, 214),
        )
        screen.draw.text(
            "Yadigârı alıp çıkışa ulaş. Muhafıza değmek yenilgidir.",
            center=(WIDTH // 2, 418),
            fontsize=20,
            color=(176, 190, 214),
        )
        for preview, label in zip(self.previews, ("Kahraman", "Slime", "Yarasa")):
            preview.actor.draw()
            screen.draw.text(
                label,
                center=(preview.actor.x, preview.actor.y + 42),
                fontsize=22,
                color=(210, 218, 232),
            )

    def _draw_world(self):
        coin_frame = int(self.elapsed * 6) % FRAME_COUNT
        coin_bob = int(math.sin(self.elapsed * 5) * 3)
        relic_bob = int(math.sin(self.elapsed * 3) * 2)
        for row_index, row in enumerate(LEVEL):
            for column, char in enumerate(row):
                screen.blit(
                    self.floor_name(column, row_index, char),
                    (column * TILE, row_index * TILE),
                )
        for cell_x, cell_y in self.coins:
            screen.blit(
                f"coin_{coin_frame}",
                (cell_x * TILE, cell_y * TILE + coin_bob),
            )
        if not self.relic_collected:
            screen.blit(
                "relic",
                (self.relic_cell[0] * TILE, self.relic_cell[1] * TILE + relic_bob),
            )
        exit_image = "exit_open" if self.relic_collected else "exit_closed"
        screen.blit(
            exit_image,
            (self.exit_cell[0] * TILE, self.exit_cell[1] * TILE),
        )
        figures = self.enemies + [self.player]
        for figure in sorted(figures, key=lambda item: item.pixel_y):
            figure.actor.draw()
        self._draw_hud()

    def _draw_hud(self):
        hud = Rect(0, HEIGHT - HUD_HEIGHT, WIDTH, HUD_HEIGHT)
        screen.draw.filled_rect(hud, (16, 18, 28))
        if self.hint:
            message = self.hint
            color = (255, 206, 110)
        else:
            relic = "Var" if self.relic_collected else "Yok"
            message = (
                f"Yadigâr: {relic}    Altın: {self.coins_collected}/{self.total_coins}"
                "    Muhafızlardan kaç"
            )
            color = (236, 228, 206)
        screen.draw.text(
            message,
            midleft=(16, HEIGHT - HUD_HEIGHT // 2),
            fontsize=22,
            color=color,
        )

    def _draw_end_panel(self):
        panel = Rect(150, 130, 420, 300)
        won = self.state == "won"
        color = (128, 214, 140) if won else (232, 96, 96)
        screen.draw.filled_rect(panel, (14, 16, 26))
        screen.draw.rect(panel, color)
        screen.draw.text(
            "Kazandın" if won else "Kaybettin",
            center=(WIDTH // 2, 190),
            fontsize=52,
            color=color,
        )
        detail = "Yadigârla kaçtın." if won else "Bir muhafız seni yakaladı."
        screen.draw.text(detail, center=(WIDTH // 2, 248), fontsize=26, color="white")
        for button in self.buttons():
            button.draw(self.mouse_position)


world = Game()


def update(dt):
    world.update(dt)


def draw():
    world.draw()


def on_mouse_move(pos):
    world.mouse_position = pos


def on_mouse_down(pos):
    for button in world.buttons():
        if button.rect.collidepoint(pos):
            play_effect("click")
            button.action()
            return


pgzrun.go()
