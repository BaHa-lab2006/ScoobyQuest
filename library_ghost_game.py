# ==================== LIBRARY_GHOST_GAME.PY ====================
"""
Игра "Дело о Призраке Библиотеки" для детей 6–7 лет.
Полная версия, использующая ассеты из assets/game3/.
"""

import pygame
import json
import os
import random
import math
from typing import Dict, List, Optional, Any, Tuple, Callable

# ---------- КОНФИГУРАЦИЯ ----------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'DARK_BLUE': (25, 25, 112),
    'GOLD': (255, 215, 0),
    'GREEN': (0, 255, 0),
    'RED': (255, 0, 0),
    'GRAY': (128, 128, 128),
    'BLUE': (30, 144, 255),
    'LIGHT_BLUE': (173, 216, 230),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0),
    'YELLOW': (255, 255, 0),
    'BROWN': (139, 69, 19),
    'DARK_GRAY': (64, 64, 64),
    'LIGHT_GREEN': (144, 238, 144),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "assets", "game3")
IMAGES_PATH = os.path.join(ASSETS_PATH, "images")
SOUNDS_PATH = os.path.join(ASSETS_PATH, "sounds")
FONTS_PATH = os.path.join(ASSETS_PATH, "fonts")

# Дополнительные пути
BACKGROUNDS_PATH = os.path.join(IMAGES_PATH, "backgrounds")
CHARACTERS_PATH = os.path.join(IMAGES_PATH, "characters")
ITEMS_PATH = os.path.join(IMAGES_PATH, "items")
MINIGAMES_PATH = os.path.join(IMAGES_PATH, "minigames")
UI_PATH = os.path.join(IMAGES_PATH, "ui")
MUSIC_PATH = os.path.join(SOUNDS_PATH, "music")
SFX_PATH = os.path.join(SOUNDS_PATH, "sfx")
VOICE_PATH = os.path.join(SOUNDS_PATH, "voice")

PROGRESS_FILE = "library_progress.json"

def render_with_outline(text, font, color, outline_color, outline_width=2):
    """Рисует текст с обводкой (тенью)"""
    base = font.render(text, True, color)
    outline = font.render(text, True, outline_color)
    # Создаём поверхность с учётом обводки
    w, h = base.get_width() + outline_width*2, base.get_height() + outline_width*2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Рисуем обводку со смещениями
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                surf.blit(outline, (dx+outline_width, dy+outline_width))
    surf.blit(base, (outline_width, outline_width))
    return surf

# ---------- МЕНЕДЖЕР РЕСУРСОВ ----------
class AssetCache:
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._load_fonts()
        self._load_images()
        self._load_sounds()

    def _load_fonts(self):
        self.fonts['title'] = pygame.font.Font(None, 64)
        self.fonts['large'] = pygame.font.Font(None, 48)
        self.fonts['medium'] = pygame.font.Font(None, 36)
        self.fonts['small'] = pygame.font.Font(None, 24)
        try:
            font_path = os.path.join(FONTS_PATH, "Chewy-Regular.ttf")
            if os.path.exists(font_path):
                self.fonts['title'] = pygame.font.Font(font_path, 64)
                self.fonts['large'] = pygame.font.Font(font_path, 48)
                self.fonts['medium'] = pygame.font.Font(font_path, 36)
                self.fonts['small'] = pygame.font.Font(font_path, 24)
        except:
            pass

    def _load_images(self):
        # Фоны
        self._load_image('prolog_bg', os.path.join(BACKGROUNDS_PATH, 'prolog_bg.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('map_bg', os.path.join(BACKGROUNDS_PATH, 'map_bg.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('reading_hall_bg', os.path.join(BACKGROUNDS_PATH, 'reading_hall.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('kids_section_bg', os.path.join(BACKGROUNDS_PATH, 'kids_section.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('book_storage_bg', os.path.join(BACKGROUNDS_PATH, 'book_storage.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('office_bg', os.path.join(BACKGROUNDS_PATH, 'office.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('basement_bg', os.path.join(BACKGROUNDS_PATH, 'basement.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('attic_bg', os.path.join(BACKGROUNDS_PATH, 'attic.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._load_image('win_bg', os.path.join(BACKGROUNDS_PATH, 'win_bg.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Персонажи
        self._load_image('daphne_normal', os.path.join(CHARACTERS_PATH, 'daphne_normal.png'), (200, 250))
        self._load_image('fred_normal', os.path.join(CHARACTERS_PATH, 'fred_normal.png'), (200, 250))
        self._load_image('fred_pointing', os.path.join(CHARACTERS_PATH, 'fred_pointing.png'), (200, 250))
        self._load_image('librarian_normal', os.path.join(CHARACTERS_PATH, 'librarian_normal.png'), (200, 250))
        self._load_image('librarian_worried', os.path.join(CHARACTERS_PATH, 'librarian_worried (1).png'), (200, 250))
        self._load_image('raven_normal', os.path.join(CHARACTERS_PATH, 'raven_normal.png'), (150, 150))
        self._load_image('raven_flying', os.path.join(CHARACTERS_PATH, 'raven_flying.png'), (150, 150))
        self._load_image('shaggy_scooby_normal', os.path.join(CHARACTERS_PATH, 'shaggy_scooby_normal.png'), (250, 250))
        self._load_image('shaggy_scooby_scared', os.path.join(CHARACTERS_PATH, 'shaggy_scooby_scared4.png'), (250, 250))
        self._load_image('velma_normal', os.path.join(CHARACTERS_PATH, 'velma_normal.png'), (200, 250))
        self._load_image('velma_thinking', os.path.join(CHARACTERS_PATH, 'velma_thinking.png'), (200, 250))
        # Предметы для мини-игр
        self._load_image('book_1', os.path.join(ITEMS_PATH, 'books', 'book_1.png'), (80, 100))
        self._load_image('book_2', os.path.join(ITEMS_PATH, 'books', 'book_2.png'), (80, 100))
        self._load_image('book_3', os.path.join(ITEMS_PATH, 'books', 'book_3.png'), (80, 100))
        self._load_image('book_blue', os.path.join(ITEMS_PATH, 'books', 'book_blue.png'), (80, 100))
        self._load_image('book_red', os.path.join(ITEMS_PATH, 'books', 'book_red.png'), (80, 100))
        self._load_image('book_green', os.path.join(ITEMS_PATH, 'books', 'book_green.png'), (80, 100))
        self._load_image('apple', os.path.join(ITEMS_PATH, 'math', 'apple.png'), (60, 60))
        self._load_image('ball', os.path.join(ITEMS_PATH, 'math', 'ball.png'), (60, 60))
        self._load_image('star', os.path.join(ITEMS_PATH, 'math', 'star.png'), (60, 60))
        self._load_image('cookie', os.path.join(ITEMS_PATH, 'math', 'cookie.png'), (60, 60))
        self._load_image('number_7', os.path.join(ITEMS_PATH, 'math', 'number_7.png'), (100, 100))
        self._load_image('lamp', os.path.join(ITEMS_PATH, 'cause_effect', 'lamp.png'), (100, 100))
        self._load_image('puddle', os.path.join(ITEMS_PATH, 'cause_effect', 'puddle.jpg'), (100, 100))
        self._load_image('open_window', os.path.join(ITEMS_PATH, 'cause_effect', 'open_window.png'), (150, 150))
        self._load_image('rain', os.path.join(ITEMS_PATH, 'cause_effect', 'rain.png'), (200, 150))
        self._load_image('clock_face', os.path.join(ITEMS_PATH, 'clock', 'clock_face.png'), (300, 300))
        self._load_image('clock_hour_hand', os.path.join(ITEMS_PATH, 'clock', 'clock_hour_hand.png'), (120, 120))
        self._load_image('clock_min_hand', os.path.join(ITEMS_PATH, 'clock', 'clock_min_hand.png'), (150, 150))
        self._load_image('puzzle_piece_1', os.path.join(ITEMS_PATH, 'puzzle', 'puzzle_piece_1.png'), (100, 100))
        self._load_image('puzzle_piece_2', os.path.join(ITEMS_PATH, 'puzzle', 'puzzle_piece_2.png'), (100, 100))
        self._load_image('puzzle_piece_3', os.path.join(ITEMS_PATH, 'puzzle', 'puzzle_piece_3.png'), (100, 100))
        self._load_image('puzzle_piece_4', os.path.join(ITEMS_PATH, 'puzzle', 'puzzle_piece_4.png'), (100, 100))
        self._load_image('paw_print', os.path.join(ITEMS_PATH, 'puzzle', 'paw_print_puzzle.jpg'), (400, 400))
        self._load_image('bookshelf_maze', os.path.join(ITEMS_PATH, 'maze', 'bookshelf.png'), (70, 70))
        self._load_image('exit_door', os.path.join(ITEMS_PATH, 'maze', 'exit_door.png'), (70, 70))
        self._load_image('cap', os.path.join(ITEMS_PATH, 'rebus', 'cap-bg.png'), (100, 100))
        self._load_image('fish', os.path.join(ITEMS_PATH, 'rebus', 'fish.png'), (100, 100))
        self._load_image('swan', os.path.join(ITEMS_PATH, 'rebus', 'swan.png'), (100, 100))
        self._load_image('rooster', os.path.join(ITEMS_PATH, 'rebus', 'rooster.png'), (100, 100))
        self._load_image('watermelon', os.path.join(ITEMS_PATH, 'rebus', 'watermelon.png'), (100, 100))
        # UI
        self._load_image('door', os.path.join(UI_PATH, 'door.png'), (80, 120))
        self._load_image('home_button', os.path.join(UI_PATH, 'home.png'), (50, 50))
        self._load_image('button_normal', os.path.join(UI_PATH, 'button_normal.png'), (200, 60))
        self._load_image('button_hover', os.path.join(UI_PATH, 'button_hover.png'), (200, 60))
        self._load_image('letter_slot', os.path.join(UI_PATH, 'letter_slot.png'), (60, 60))

    def _load_image(self, key, path, size=None):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            self.images[key] = img
        except Exception as e:
            print(f"Ошибка загрузки {path}: {e}")
            surf = pygame.Surface(size if size else (100, 100))
            surf.fill(COLORS['PURPLE'])
            self.images[key] = surf

    def _load_sounds(self):
        self._load_sound('bg_music', os.path.join(MUSIC_PATH, 'background_music.mp3'))
        self._load_sound('suspense', os.path.join(MUSIC_PATH, 'suspense_music.mp3'))
        self._load_sound('victory', os.path.join(MUSIC_PATH, 'victory_music.mp3'))
        self._load_sound('click', os.path.join(SFX_PATH, 'click.wav'))
        self._load_sound('success', os.path.join(SFX_PATH, 'success.mp3'))
        self._load_sound('fail', os.path.join(SFX_PATH, 'fail.wav'))
        self._load_sound('book_move', os.path.join(SFX_PATH, 'book_move.wav'))
        self._load_sound('bookshelf_move', os.path.join(SFX_PATH, 'bookshelf_move.wav'))
        self._load_sound('clock_chime', os.path.join(SFX_PATH, 'clock_chime.wav'))
        self._load_sound('clock_tick', os.path.join(SFX_PATH, 'clock_tick.wav'))
        self._load_sound('puzzle_place', os.path.join(SFX_PATH, 'puzzle_place.flac'))
        self._load_sound('puzzle_complete', os.path.join(SFX_PATH, 'puzzle_complete.wav'))
        self._load_sound('raven_caw', os.path.join(SFX_PATH, 'raven_caw.aiff'))
        self._load_sound('star_earn', os.path.join(SFX_PATH, 'star_earn.wav'))
        self._load_sound('window_net', os.path.join(SFX_PATH, 'window_net.wav'))
        self._load_sound('letter_collect', os.path.join(SFX_PATH, 'letter_collect.ogg'))
        self._load_sound('map_open', os.path.join(SFX_PATH, 'map_open.wav'))
        self._load_sound('transition', os.path.join(SFX_PATH, 'transition.wav'))
        # Голоса
        voice_files = [
            'daphne_congrats', 'daphne_intro_1', 'fred_clock_success', 'fred_final', 'fred_intro_1',
            'fred_maze_success', 'librarian_final', 'librarian_intro_1', 'librarian_success_1',
            'librarian_task_1', 'scooby_basement_1', 'scooby_count_hint', 'scooby_intro_1',
            'scooby_letter', 'scooby_math_hint', 'scooby_memory_success', 'scooby_rebus_success',
            'shaggy_basement_1', 'shaggy_count_success', 'shaggy_intro_1', 'shaggy_math_success',
            'shaggy_rebus_hint', 'velma_cause_success', 'velma_intro_1', 'velma_office_1',
            'velma_puzzle_success', 'velma_reveal'
        ]
        for vf in voice_files:
            path = os.path.join(VOICE_PATH, vf + '.wav')
            self._load_sound(vf, path)

    def _load_sound(self, key, path):
        try:
            self.sounds[key] = pygame.mixer.Sound(path)
        except:
            self.sounds[key] = None

    def get_image(self, key):
        return self.images.get(key)

    def get_sound(self, key):
        return self.sounds.get(key)

    def play_sound(self, key, volume=0.7):
        snd = self.get_sound(key)
        if snd:
            snd.set_volume(volume)
            snd.play()

    def play_voice(self, key, volume=0.8):
        self.play_sound(key, volume)

    def play_music(self, key, loop=-1, volume=0.4):
        if key == 'bg_music':
            try:
                pygame.mixer.music.load(os.path.join(MUSIC_PATH, 'background_music.mp3'))
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loop)
            except:
                pass
        else:
            snd = self.get_sound(key)
            if snd:
                snd.play(loop)

    def stop_music(self):
        pygame.mixer.music.stop()


# ---------- UI ЭЛЕМЕНТЫ ----------
class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 normal_color=(100, 100, 200), hover_color=(150, 150, 255), callback=None,
                 image_normal=None, image_hover=None):
        self.rect = rect
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.callback = callback
        self.image_normal = image_normal
        self.image_hover = image_hover
        self.is_hovered = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()

    def draw(self, surface):
        if self.image_normal and self.is_hovered and self.image_hover:
            surface.blit(self.image_hover, self.rect)
        elif self.image_normal:
            surface.blit(self.image_normal, self.rect)
        else:
            color = self.hover_color if self.is_hovered else self.normal_color
            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            pygame.draw.rect(surface, COLORS['WHITE'], self.rect, 2, border_radius=12)
        if self.text:
            text_surf = self.font.render(self.text, True, COLORS['WHITE'])
            surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class Label:
    def __init__(self, pos, text, font, color, center=True):
        self.pos = pos
        self.text = text
        self.font = font
        self.color = color
        self.center = center
        self._update_surface()

    def _update_surface(self):
        self.surface = self.font.render(self.text, True, self.color)

    def set_text(self, text):
        self.text = text
        self._update_surface()

    def draw(self, surface):
        if self.center:
            rect = self.surface.get_rect(center=self.pos)
            surface.blit(self.surface, rect)
        else:
            surface.blit(self.surface, self.pos)


class DialogBubble:
    def __init__(self, rect, text, speaker, font, assets):
        self.rect = rect
        self.text = text
        self.speaker = speaker
        self.font = font
        self.assets = assets
        self._lines = self._wrap_text()

    def _wrap_text(self):
        words = self.text.split(' ')
        lines = []
        current = ''
        max_width = self.rect.width - 40
        for w in words:
            test = current + w + ' '
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = w + ' '
        if current:
            lines.append(current)
        return lines

    def draw(self, surface):
        pygame.draw.rect(surface, COLORS['WHITE'], self.rect, border_radius=20)
        pygame.draw.rect(surface, COLORS['BLACK'], self.rect, 3, border_radius=20)
        name_surf = self.font.render(self.speaker + ':', True, COLORS['PURPLE'])
        surface.blit(name_surf, (self.rect.x + 15, self.rect.y + 10))
        y = self.rect.y + 50
        for line in self._lines:
            line_surf = self.font.render(line, True, COLORS['BLACK'])
            surface.blit(line_surf, (self.rect.x + 15, y))
            y += 30


# ---------- МИНИ-ИГРЫ (полная реализация по сценарию) ----------
# Базовый класс
class BaseMinigame:
    def __init__(self, assets: AssetCache, on_complete: Callable[[bool], None]):
        self.assets = assets
        self.on_complete = on_complete
        self.finished = False
        self.ui_elements = []
        self.message_label = None
        self.message_timer = 0

    def handle_event(self, event):
        for el in self.ui_elements:
            if hasattr(el, 'handle_event'):
                el.handle_event(event)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_label = None

    def draw(self, surface):
        for el in self.ui_elements:
            if hasattr(el, 'draw'):
                el.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)

    def show_message(self, text, color=COLORS['RED'], duration=2.0):
        self.message_label = Label((SCREEN_WIDTH//2, 100), text, self.assets.fonts['medium'], color)
        self.message_timer = duration

    def complete(self, success: bool):
        if not self.finished:
            self.finished = True
            self.on_complete(success)


# 1.1 Расставь книги
class SortBooksMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.slots = [None, None, None]  # позиции 0,1,2
        self.books = []
        # Книги с цифрами 3,1,2 (перепутаны)
        positions = [(300, 500), (450, 500), (600, 500)]
        numbers = [3,1,2]
        for i, num in enumerate(numbers):
            img = assets.get_image(f'book_{num}')
            if img is None:
                img = pygame.Surface((80,100))
                img.fill(COLORS['ORANGE'])
            rect = pygame.Rect(positions[i][0], positions[i][1], 80, 100)
            self.books.append({'img': img, 'rect': rect, 'num': num, 'dragging': False, 'drag_offset': (0,0)})
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = self.books + [self.check_btn]
        self.slot_rects = [
            pygame.Rect(250, 300, 100, 120),
            pygame.Rect(420, 300, 100, 120),
            pygame.Rect(590, 300, 100, 120)
        ]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.books:
                if b['rect'].collidepoint(event.pos):
                    b['dragging'] = True
                    b['drag_offset'] = (b['rect'].x - event.pos[0], b['rect'].y - event.pos[1])
                    self.assets.play_sound('click')
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self.books:
                if b['dragging']:
                    b['dragging'] = False
                    # Проверить попадание в слот
                    placed = False
                    for idx, slot_rect in enumerate(self.slot_rects):
                        if b['rect'].colliderect(slot_rect):
                            # Положить в слот
                            b['rect'].center = slot_rect.center
                            self.slots[idx] = b['num']
                            placed = True
                            break
                    if not placed:
                        # Вернуть в исходное
                        orig_pos = [(300,500),(450,500),(600,500)][self.books.index(b)]
                        b['rect'].topleft = orig_pos
                    # Обновить слоты: удалить если книга ушла
                    for idx, val in enumerate(self.slots):
                        if val == b['num'] and not any(b2['num'] == val and b2['rect'].colliderect(self.slot_rects[idx]) for b2 in self.books):
                            self.slots[idx] = None
        elif event.type == pygame.MOUSEMOTION:
            for b in self.books:
                if b['dragging']:
                    b['rect'].x = event.pos[0] + b['drag_offset'][0]
                    b['rect'].y = event.pos[1] + b['drag_offset'][1]

    def check(self):
        if self.slots == [1,2,3]:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Нет, начни с единицы!", COLORS['RED'])

    def draw(self, surface):
        # Рисуем полку с местами
        for i, rect in enumerate(self.slot_rects):
            pygame.draw.rect(surface, COLORS['BROWN'], rect, 3)
            if self.slots[i] is not None:
                num = self.slots[i]
                img = self.assets.get_image(f'book_{num}')
                if img:
                    surface.blit(img, rect)
        # Рисуем книги снизу
        for b in self.books:
            surface.blit(b['img'], b['rect'])
        title = self.assets.fonts['medium'].render("Расставь книги по порядку: 1, 2, 3", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.check_btn.draw(surface)
        super().draw(surface)


# 1.2 Логический ряд
class LogicRowMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.options = ["🔴 КНИГА", "🔵 КНИГА", "🟢 ТЕТРАДЬ"]
        self.correct_idx = 1
        self.buttons = []
        for i, opt in enumerate(self.options):
            btn = Button(pygame.Rect(300, 400 + i*70, 400, 60), opt,
                         assets.fonts['medium'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if idx == self.correct_idx:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Посмотри внимательно: цвета чередуются. Красный, синий, красный… какой следующий?")

    def draw(self, surface):
        title = self.assets.fonts['medium'].render("Какой предмет следующий?", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        items = ["🔴 КНИГА", "🔵 КНИГА", "🔴 КНИГА", "?"]
        x_start = 200
        for i, it in enumerate(items):
            txt = self.assets.fonts['small'].render(it, True, COLORS['WHITE'])
            surface.blit(txt, (x_start + i*150, 250))
        super().draw(surface)


# 2.1 Состав числа
class NumberCompositionMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.pairs = [
            ("3 яблока + 4 яблока", 7, True),
            ("5 звёзд + 2 звезды", 7, True),
            ("6 мячей + 1 мяч", 7, True),
            ("2 яблока + 3 яблока", 5, False),
            ("4 звезды + 4 звезды", 8, False)
        ]
        self.buttons = []
        for i, (text, total, correct) in enumerate(self.pairs):
            btn = Button(pygame.Rect(200, 250 + i*60, 600, 50), text,
                         assets.fonts['small'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if self.pairs[idx][2]:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Семь — это три и четыре. Или пять и два. Попробуй ещё!")

    def draw(self, surface):
        title = self.assets.fonts['medium'].render("Выбери пару, которая в сумме даёт 7", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        big7 = self.assets.fonts['large'].render("7", True, COLORS['YELLOW'])
        surface.blit(big7, (SCREEN_WIDTH//2 - big7.get_width()//2, 120))
        super().draw(surface)


# 2.2 Найди пару букв
class MemoryLettersMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.cards = [('А', False), ('А', False), ('Б', False), ('В', False)]
        random.shuffle(self.cards)
        self.selected = None
        self.waiting = False
        self.wait_timer = 0
        self.buttons = []
        for i in range(4):
            rect = pygame.Rect(200 + (i%2)*300, 300 + (i//2)*200, 150, 150)
            btn = Button(rect, "", assets.fonts['large'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.reveal(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def reveal(self, idx):
        if self.waiting or self.cards[idx][1]:
            return
        self.cards[idx] = (self.cards[idx][0], True)
        self.assets.play_sound('click')
        if self.selected is None:
            self.selected = idx
        else:
            if self.cards[self.selected][0] == self.cards[idx][0]:
                self.cards[self.selected] = (self.cards[self.selected][0], True)
                self.cards[idx] = (self.cards[idx][0], True)
                self.selected = None
                if all(flipped for _, flipped in self.cards):
                    self.assets.play_sound('success')
                    self.complete(True)
            else:
                self.waiting = True
                self.wait_timer = 1.0
                self.pending_idx = idx

    def update(self, dt):
        super().update(dt)
        if self.waiting:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.cards[self.selected] = (self.cards[self.selected][0], False)
                self.cards[self.pending_idx] = (self.cards[self.pending_idx][0], False)
                self.selected = None
                self.waiting = False

    def draw(self, surface):
        title = self.assets.fonts['medium'].render("Найди пару одинаковых букв", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, btn in enumerate(self.buttons):
            if self.cards[i][1]:
                letter = self.cards[i][0]
                text_surf = self.assets.fonts['large'].render(letter, True, COLORS['BLACK'])
                btn.color = COLORS['WHITE']
                btn.draw(surface)
                surface.blit(text_surf, text_surf.get_rect(center=btn.rect.center))
            else:
                btn.draw(surface)
        super().draw(surface)


# 3.1 Часы
class ClockMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.hour = 3
        self.dragging = False
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = [self.check_btn]
        self.center = (SCREEN_WIDTH//2, 300)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверить попадание в часовую стрелку
            angle = math.radians(90 - self.hour*30)
            end = (self.center[0] + 80 * math.cos(angle), self.center[1] - 80 * math.sin(angle))
            if pygame.Rect(end[0]-15, end[1]-15, 30, 30).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            angle = math.degrees(math.atan2(-dy, dx))
            if angle < 0:
                angle += 360
            hour = round(angle / 30) % 12
            if hour == 0:
                hour = 12
            self.hour = hour
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def check(self):
        if self.hour == 6:
            self.assets.play_sound('clock_chime')
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Не торопись. Шесть часов — это когда маленькая стрелка внизу, а большая наверху.")

    def draw(self, surface):
        # Циферблат
        pygame.draw.circle(surface, COLORS['WHITE'], self.center, 150, 5)
        for i in range(1, 13):
            angle = math.radians(90 - i*30)
            x1 = self.center[0] + 130 * math.cos(angle)
            y1 = self.center[1] - 130 * math.sin(angle)
            x2 = self.center[0] + 145 * math.cos(angle)
            y2 = self.center[1] - 145 * math.sin(angle)
            pygame.draw.line(surface, COLORS['BLACK'], (x1,y1), (x2,y2), 3)
            num = self.assets.fonts['small'].render(str(i), True, COLORS['BLACK'])
            x_text = self.center[0] + 115 * math.cos(angle) - num.get_width()//2
            y_text = self.center[1] - 115 * math.sin(angle) - num.get_height()//2
            surface.blit(num, (x_text, y_text))
        # Часовая стрелка
        angle = math.radians(90 - self.hour*30)
        end = (self.center[0] + 80 * math.cos(angle), self.center[1] - 80 * math.sin(angle))
        pygame.draw.line(surface, COLORS['BLACK'], self.center, end, 8)
        # Минутная на 12
        end_min = (self.center[0], self.center[1] - 110)
        pygame.draw.line(surface, COLORS['BLACK'], self.center, end_min, 4)
        self.check_btn.draw(surface)
        title = self.assets.fonts['medium'].render("Поставь время 6 часов", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        super().draw(surface)


# 3.2 Лабиринт (передвинь стеллаж)
class MazeMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.pos = (0,0)
        self.target = (3,3)
        # Стены: для каждой клетки направления
        self.walls = {
            (0,0): {'right': False, 'down': True},
            (1,0): {'left': False, 'right': False, 'down': True},
            (2,0): {'left': False, 'right': True, 'down': False},
            (3,0): {'left': True, 'down': True},
            (0,1): {'right': False, 'up': True, 'down': True},
            (1,1): {'left': False, 'right': True, 'up': True, 'down': False},
            (2,1): {'left': True, 'right': False, 'up': False, 'down': True},
            (3,1): {'left': False, 'up': True, 'down': False},
            (0,2): {'right': True, 'up': True, 'down': False},
            (1,2): {'left': True, 'right': False, 'up': False, 'down': True},
            (2,2): {'left': False, 'right': False, 'up': True, 'down': False},
            (3,2): {'left': False, 'up': False, 'down': True},
            (0,3): {'right': True, 'up': False},
            (1,3): {'left': True, 'right': False, 'up': True},
            (2,3): {'left': False, 'right': False, 'up': False},
            (3,3): {'left': False, 'up': True},
        }
        self.buttons = []
        btn_up = Button(pygame.Rect(SCREEN_WIDTH//2-30, 550, 60, 50), "↑", assets.fonts['large'],
                        COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(0,-1))
        btn_down = Button(pygame.Rect(SCREEN_WIDTH//2-30, 650, 60, 50), "↓", assets.fonts['large'],
                          COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(0,1))
        btn_left = Button(pygame.Rect(SCREEN_WIDTH//2-90, 600, 60, 50), "←", assets.fonts['large'],
                          COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(-1,0))
        btn_right = Button(pygame.Rect(SCREEN_WIDTH//2+30, 600, 60, 50), "→", assets.fonts['large'],
                           COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(1,0))
        self.buttons = [btn_up, btn_down, btn_left, btn_right]
        self.ui_elements = self.buttons

    def move(self, dx, dy):
        nx, ny = self.pos[0]+dx, self.pos[1]+dy
        if nx < 0 or nx >= 4 or ny < 0 or ny >= 4:
            self.show_message("Там стена!")
            self.assets.play_sound('fail')
            return
        # Проверка стены
        if dx == 1 and self.walls[self.pos].get('right', False):
            self.show_message("Там стена!")
            self.assets.play_sound('fail')
            return
        if dx == -1 and self.walls[(nx, ny)].get('right', False):
            self.show_message("Там стена!")
            self.assets.play_sound('fail')
            return
        if dy == 1 and self.walls[self.pos].get('down', False):
            self.show_message("Там стена!")
            self.assets.play_sound('fail')
            return
        if dy == -1 and self.walls[(nx, ny)].get('down', False):
            self.show_message("Там стена!")
            self.assets.play_sound('fail')
            return
        self.pos = (nx, ny)
        self.assets.play_sound('bookshelf_move')
        if self.pos == self.target:
            self.assets.play_sound('success')
            self.complete(True)

    def draw(self, surface):
        cell_size = 80
        offset_x = (SCREEN_WIDTH - 4*cell_size)//2
        offset_y = 150
        for y in range(4):
            for x in range(4):
                rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size, cell_size-2, cell_size-2)
                if (x,y) == self.pos:
                    color = COLORS['GREEN']
                elif (x,y) == self.target:
                    color = COLORS['GOLD']
                else:
                    color = COLORS['LIGHT_BLUE']
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, COLORS['BLACK'], rect, 2)
                # Стены
                if self.walls[(x,y)].get('right', False):
                    pygame.draw.line(surface, COLORS['RED'], (rect.right, rect.top), (rect.right, rect.bottom), 3)
                if self.walls[(x,y)].get('down', False):
                    pygame.draw.line(surface, COLORS['RED'], (rect.left, rect.bottom), (rect.right, rect.bottom), 3)
        title = self.assets.fonts['medium'].render("Проведи стеллаж к выходу (золотая клетка)", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for btn in self.buttons:
            btn.draw(surface)
        super().draw(surface)


# 4.1 Пазл (след лапы)
class PuzzleMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        # 4 части пазла
        self.pieces = []
        self.slots = [None, None, None, None]
        # Картинка целиком (для отображения)
        self.full_image = assets.get_image('paw_print')
        if self.full_image:
            self.full_image = pygame.transform.scale(self.full_image, (400,400))
        # Создаём кусочки из полной картинки (если есть) иначе заглушки
        piece_rects = [(0,0,200,200), (200,0,200,200), (0,200,200,200), (200,200,200,200)]
        for i, rect in enumerate(piece_rects):
            if self.full_image:
                piece = self.full_image.subsurface(pygame.Rect(rect))
            else:
                piece = pygame.Surface((200,200))
                piece.fill(COLORS['GRAY'])
            self.pieces.append(piece)
        random.shuffle(self.pieces)
        # Позиции кусочков справа
        self.piece_rects = []
        start_x = 750
        start_y = 200
        for i in range(4):
            rect = pygame.Rect(start_x, start_y + i*110, 100, 100)
            self.piece_rects.append({'img': pygame.transform.scale(self.pieces[i], (100,100)), 'rect': rect, 'idx': i, 'dragging': False, 'drag_offset': (0,0)})
        self.slot_rects = [
            pygame.Rect(200, 200, 100, 100),
            pygame.Rect(320, 200, 100, 100),
            pygame.Rect(200, 320, 100, 100),
            pygame.Rect(320, 320, 100, 100)
        ]
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = self.piece_rects + [self.check_btn]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for p in self.piece_rects:
                if p['rect'].collidepoint(event.pos):
                    p['dragging'] = True
                    p['drag_offset'] = (p['rect'].x - event.pos[0], p['rect'].y - event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            for p in self.piece_rects:
                if p['dragging']:
                    p['dragging'] = False
                    placed = False
                    for idx, slot_rect in enumerate(self.slot_rects):
                        if p['rect'].colliderect(slot_rect):
                            p['rect'].center = slot_rect.center
                            self.slots[idx] = p['idx']
                            placed = True
                            break
                    if not placed:
                        # Вернуть в исходное
                        orig_x = 750 + (p['idx']%2)*110
                        orig_y = 200 + (p['idx']//2)*110
                        p['rect'].topleft = (orig_x, orig_y)
                    # Очистить слоты
                    for idx, val in enumerate(self.slots):
                        if val == p['idx'] and not any(p2['idx'] == val and p2['rect'].colliderect(self.slot_rects[idx]) for p2 in self.piece_rects):
                            self.slots[idx] = None
        elif event.type == pygame.MOUSEMOTION:
            for p in self.piece_rects:
                if p['dragging']:
                    p['rect'].x = event.pos[0] + p['drag_offset'][0]
                    p['rect'].y = event.pos[1] + p['drag_offset'][1]

    def check(self):
        if all(s is not None for s in self.slots):
            self.assets.play_sound('puzzle_complete')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Собери все части в рамку!")

    def draw(self, surface):
        # Рамка
        for rect in self.slot_rects:
            pygame.draw.rect(surface, COLORS['WHITE'], rect, 3)
            if self.slots[ self.slot_rects.index(rect) ] is not None:
                idx = self.slots[ self.slot_rects.index(rect) ]
                surface.blit(pygame.transform.scale(self.pieces[idx], (100,100)), rect)
        for p in self.piece_rects:
            surface.blit(p['img'], p['rect'])
        title = self.assets.fonts['medium'].render("Собери след лапы", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.check_btn.draw(surface)
        super().draw(surface)


# 4.2 Причина-Следствие
class CauseEffectMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.options = ["Лужа на полу", "Горящая лампа", "Закрытая книга"]
        self.correct = 0
        self.buttons = []
        for i, opt in enumerate(self.options):
            btn = Button(pygame.Rect(300, 400 + i*70, 400, 60), opt,
                         assets.fonts['medium'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if idx == self.correct:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Если окно открыто и идёт дождь — что случится с полом?")

    def draw(self, surface):
        title = self.assets.fonts['medium'].render("Выбери правильное следствие", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        # Изображение причины
        cause_text = self.assets.fonts['small'].render("Открытое окно идёт дождь", True, COLORS['WHITE'])
        surface.blit(cause_text, (SCREEN_WIDTH//2 - cause_text.get_width()//2, 150))
        super().draw(surface)


# 5.1 Ребус
class RebusMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.pictures = [("cap", "К"), ("fish", "Р"), ("swan", "О"), ("rooster", "Н"), ("watermelon", "А")]
        self.user_letters = ["", "", "", "", ""]
        self.current_slot = 0
        self.keyboard_buttons = []
        letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        x_start = 150
        for i, ch in enumerate(letters):
            btn = Button(pygame.Rect(x_start + (i%10)*60, 500 + (i//10)*60, 50, 50), ch,
                         assets.fonts['small'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda c=ch: self.add_letter(c))
            self.keyboard_buttons.append(btn)
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = self.keyboard_buttons + [self.check_btn]

    def add_letter(self, ch):
        if self.current_slot < 5:
            self.user_letters[self.current_slot] = ch
            self.current_slot += 1
            self.assets.play_sound('click')

    def check(self):
        word = "".join(self.user_letters)
        if word == "КРОНА":
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Первая буква — как в слове 'кепка'. Вторая — как в 'рыба'... Попробуй ещё!")

    def draw(self, surface):
        for i, (pic_key, correct) in enumerate(self.pictures):
            x = 150 + i*130
            img = self.assets.get_image(pic_key)
            if img:
                surface.blit(img, (x, 150))
            else:
                txt = self.assets.fonts['large'].render(pic_key[0].upper(), True, COLORS['WHITE'])
                surface.blit(txt, (x+30, 180))
            # Слот для буквы
            rect = pygame.Rect(x+30, 280, 60, 60)
            pygame.draw.rect(surface, COLORS['WHITE'], rect)
            pygame.draw.rect(surface, COLORS['BLACK'], rect, 2)
            if self.user_letters[i]:
                letter_surf = self.assets.fonts['large'].render(self.user_letters[i], True, COLORS['BLACK'])
                surface.blit(letter_surf, letter_surf.get_rect(center=rect.center))
        title = self.assets.fonts['medium'].render("Напиши слово по картинкам", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for btn in self.keyboard_buttons:
            btn.draw(surface)
        self.check_btn.draw(surface)
        super().draw(surface)


# 5.2 Счёт до 20 (чётные)
class EvenNumbersMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.clicked = [False]*21
        self.buttons = []
        for i in range(1, 21):
            x = 100 + ((i-1)%5)*120
            y = 200 + ((i-1)//5)*80
            btn = Button(pygame.Rect(x, y, 80, 60), str(i),
                         assets.fonts['medium'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda n=i: self.click_number(n))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def click_number(self, n):
        if n % 2 == 0 and not self.clicked[n]:
            self.clicked[n] = True
            self.assets.play_sound('click')
            if all(self.clicked[i] for i in range(2,21,2)):
                self.assets.play_sound('success')
                self.complete(True)
        elif n % 2 != 0:
            self.assets.play_sound('fail')
            self.show_message("Чётные — те, что делятся на два. Два, четыре, шесть… А это нечётное!")

    def draw(self, surface):
        title = self.assets.fonts['medium'].render("Нажми на все чётные числа от 1 до 20", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, btn in enumerate(self.buttons):
            if self.clicked[i+1]:
                btn.normal_color = COLORS['GREEN']
            btn.draw(surface)
        super().draw(surface)


# 6. Финальная викторина
class FinalQuizMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.questions = [
            ("Кто оставил чернильные следы?", ["Библиотекарь", "Ворона", "Собака"], 1),
            ("Почему ворона залетела в библиотеку?", ["Хотела украсть книги", "Окно было разбито", "Ей было скучно"], 1),
            ("Что нужно сделать, чтобы ворона больше не залетала?", ["Поймать её", "Поставить сетку на окно и повесить скворечник", "Закрыть библиотеку"], 1)
        ]
        self.current_q = 0
        self.buttons = []
        self.setup_question()

    def setup_question(self):
        self.buttons = []
        q_text, options, _ = self.questions[self.current_q]
        for i, opt in enumerate(options):
            btn = Button(pygame.Rect(300, 350 + i*70, 400, 60), opt,
                         self.assets.fonts['medium'], COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.answer(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def answer(self, idx):
        _, _, correct = self.questions[self.current_q]
        if idx == correct:
            self.assets.play_sound('click')
            self.current_q += 1
            if self.current_q >= len(self.questions):
                self.assets.play_sound('success')
                self.complete(True)
            else:
                self.setup_question()
        else:
            self.assets.play_sound('fail')
            self.show_message("Подумай, как решить проблему, чтобы всем было хорошо — и птице, и книгам.")

    def draw(self, surface):
        if self.current_q < len(self.questions):
            q_text, _, _ = self.questions[self.current_q]
            q_surf = self.assets.fonts['medium'].render(q_text, True, COLORS['GOLD'])
            surface.blit(q_surf, (SCREEN_WIDTH//2 - q_surf.get_width()//2, 200))
        super().draw(surface)


# ---------- ОСНОВНЫЕ ЭКРАНЫ ----------
class Screen:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass


class LoadingScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.timer = 2.0

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.game.set_state('PROLOG')

    def draw(self, surface):
        bg = self.game.assets.get_image('prolog_bg')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['DARK_BLUE'])
        title = self.game.assets.fonts['title'].render("Дело о Призраке Библиотеки", True, COLORS['GOLD'])
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
        load = self.game.assets.fonts['small'].render("Загрузка...", True, COLORS['WHITE'])
        surface.blit(load, load.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))


class PrologScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.dialogs = [
            ("Дафна", "Тишина библиотеки нарушена… Книги летают по ночам сами по себе!"),
            ("Библиотекарь", "Это Призрак Знаний! Он переставляет стеллажи и пишет знаки на стенах. Помогите нам, пожалуйста!"),
            ("Велма", "Знаки на полу похожи на отпечатки… но не человеческие. Если пройдём все комнаты и решим загадки — узнаем правду.")
        ]
        self.step = 0
        self.font = game.assets.fonts['small']
        self.next_btn = Button(pygame.Rect(SCREEN_WIDTH-150, SCREEN_HEIGHT-70, 100, 40), "Далее",
                               self.font, COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                               callback=self.next_step)
        self.start_btn = None

    def next_step(self):
        self.step += 1
        self.game.assets.play_sound('click')
        if self.step >= len(self.dialogs):
            self.start_btn = Button(pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT-100, 240, 60), "Начать расследование",
                                    self.game.assets.fonts['medium'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                    callback=lambda: self.game.set_state('MAP'))
            self.next_btn.enabled = False

    def handle_event(self, event):
        self.next_btn.handle_event(event)
        if self.start_btn:
            self.start_btn.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.get_image('prolog_bg')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['DARK_BLUE'])
        if self.step < len(self.dialogs):
            speaker, text = self.dialogs[self.step]
            bubble = DialogBubble(pygame.Rect(100, SCREEN_HEIGHT-180, SCREEN_WIDTH-200, 120), text, speaker, self.font, self.game.assets)
            bubble.draw(surface)
            self.next_btn.draw(surface)
        else:
            if self.start_btn:
                self.start_btn.draw(surface)


class MapScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.locations = [
            (1, "Читальный зал", 200, 250, 'В'),
            (2, "Детский абонемент", 650, 250, 'О'),
            (3, "Книгохранилище", 200, 450, 'Р'),
            (4, "Кабинет", 650, 450, 'О'),
            (5, "Подвал", 200, 650, 'Н'),
            (6, "Чердак", 650, 650, 'А')
        ]
        self.buttons = []
        self.update_buttons()
        self.home_btn = Button(pygame.Rect(30, SCREEN_HEIGHT-60, 100, 40), "Домой",
                               game.assets.fonts['small'], COLORS['RED'], COLORS['ORANGE'],
                               callback=self.game.exit_game)

    def update_buttons(self):
        self.buttons = []
        for num, name, x, y, letter in self.locations:
            available = (num == 1) or (num-1 in self.game.completed_locations)
            completed = num in self.game.completed_locations
            if completed:
                color = COLORS['GREEN']
            elif available:
                color = COLORS['LIGHT_BLUE']
            else:
                color = COLORS['GRAY']
            btn = Button(pygame.Rect(x, y, 180, 100), name, self.game.assets.fonts['small'],
                         color, color, callback=lambda n=num: self.go_to_location(n))
            btn.enabled = available and not completed
            self.buttons.append(btn)

    def go_to_location(self, loc_num):
        self.game.current_location_num = loc_num
        self.game.set_state('LOCATION')

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
        self.home_btn.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.get_image('map_bg')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['BROWN'])
        title = render_with_outline("Карта библиотеки", self.game.assets.fonts['title'], COLORS['GOLD'], COLORS['BLACK'], 2)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 50)))
        letters_str = ' '.join(list(self.game.collected_letters.ljust(6, '_')))
        lett_surf = render_with_outline(f"Буквы: {letters_str}", self.game.assets.fonts['medium'], COLORS['WHITE'], COLORS['BLACK'], 2)
        surface.blit(lett_surf, (150, 110))
        for btn in self.buttons:
            btn.draw(surface)
        self.home_btn.draw(surface)


class LocationScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.tasks = []
        self.task_buttons = []
        self.loc = None
        self.completed_tasks = []
        self.back_btn = Button(pygame.Rect(50, SCREEN_HEIGHT-60, 120, 40), "На карту",
                               game.assets.fonts['small'], COLORS['GRAY'], COLORS['LIGHT_BLUE'],
                               callback=self.exit_location)

    def on_enter(self):
        self.loc = self.game.get_location_data(self.game.current_location_num)
        if not self.loc:
            self.game.set_state('MAP')
            return
        # Задания для каждой локации
        if self.game.current_location_num == 1:
            self.tasks = [
                {'id': 'sort', 'name': 'Расставь книги', 'minigame_class': SortBooksMinigame},
                {'id': 'logic', 'name': 'Логический ряд', 'minigame_class': LogicRowMinigame}
            ]
        elif self.game.current_location_num == 2:
            self.tasks = [
                {'id': 'number', 'name': 'Состав числа 7', 'minigame_class': NumberCompositionMinigame},
                {'id': 'memory', 'name': 'Найди пару букв', 'minigame_class': MemoryLettersMinigame}
            ]
        elif self.game.current_location_num == 3:
            self.tasks = [
                {'id': 'clock', 'name': 'Часы', 'minigame_class': ClockMinigame},
                {'id': 'maze', 'name': 'Передвинь стеллаж', 'minigame_class': MazeMinigame}
            ]
        elif self.game.current_location_num == 4:
            self.tasks = [
                {'id': 'puzzle', 'name': 'Пазл следа', 'minigame_class': PuzzleMinigame},
                {'id': 'cause', 'name': 'Причина-Следствие', 'minigame_class': CauseEffectMinigame}
            ]
        elif self.game.current_location_num == 5:
            self.tasks = [
                {'id': 'rebus', 'name': 'Расшифруй слово', 'minigame_class': RebusMinigame},
                {'id': 'even', 'name': 'Счёт до 20 (чётные)', 'minigame_class': EvenNumbersMinigame}
            ]
        elif self.game.current_location_num == 6:
            self.tasks = [
                {'id': 'final', 'name': 'Раскрыть дело!', 'minigame_class': FinalQuizMinigame}
            ]
        self.completed_tasks = self.game.location_tasks_completed.get(self.game.current_location_num, [])
        self.update_task_buttons()
        # Диалог при входе
        dialog_text = self.loc.get('npc_dialogue', "Помоги мне!")
        speaker = self.loc.get('npc_name', "Библиотекарь")
        self.dialog_bubble = DialogBubble(pygame.Rect(50, SCREEN_HEIGHT-160, SCREEN_WIDTH-100, 100),
                                          dialog_text, speaker, self.game.assets.fonts['small'], self.game.assets)

    def update_task_buttons(self):
        self.task_buttons = []
        for t in self.tasks:
            completed = t['id'] in self.completed_tasks
            color = COLORS['GREEN'] if completed else COLORS['LIGHT_BLUE']
            btn = Button(pygame.Rect(200, 200 + len(self.task_buttons)*70, 600, 50),
                         f"Задание: {t['name']}",
                         self.game.assets.fonts['small'], color, COLORS['LIGHT_GREEN'] if not completed else color,
                         callback=lambda task=t: self.start_task(task) if not completed else None)
            btn.enabled = not completed
            self.task_buttons.append(btn)

    def start_task(self, task):
        self.game.set_state('TASK', task=task, location_num=self.game.current_location_num)

    def exit_location(self):
        all_completed = all(t['id'] in self.completed_tasks for t in self.tasks)
        if all_completed and self.game.current_location_num not in self.game.completed_locations:
            letter = self.loc.get('letter', '')
            if letter:
                self.game.collected_letters += letter
                self.game.assets.play_sound('letter_collect')
            self.game.completed_locations.append(self.game.current_location_num)
            self.game.save_progress()
        self.game.set_state('MAP')

    def handle_event(self, event):
        for btn in self.task_buttons:
            btn.handle_event(event)
        self.back_btn.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.get_image(self.loc['background']) if self.loc else None
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['DARK_BLUE'])
        if self.loc:
            name_surf = self.game.assets.fonts['title'].render(self.loc['name'], True, COLORS['GOLD'])
            surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH//2, 40)))
        self.dialog_bubble.draw(surface)
        for btn in self.task_buttons:
            btn.draw(surface)
        self.back_btn.draw(surface)


class TaskScreen(Screen):
    def __init__(self, game, task, location_num):
        super().__init__(game)
        self.task = task
        self.location_num = location_num
        self.minigame = task['minigame_class'](game.assets, self._on_task_complete)
        self.back_btn = Button(pygame.Rect(50, SCREEN_HEIGHT-60, 100, 40), "Назад",
                               game.assets.fonts['small'], COLORS['GRAY'], COLORS['LIGHT_BLUE'],
                               callback=lambda: game.set_state('LOCATION'))

    def _on_task_complete(self, success):
        if success:
            # Сохраняем выполнение задания
            if self.location_num not in self.game.location_tasks_completed:
                self.game.location_tasks_completed[self.location_num] = []
            if self.task['id'] not in self.game.location_tasks_completed[self.location_num]:
                self.game.location_tasks_completed[self.location_num].append(self.task['id'])
            self.game.save_progress()
            self.game.set_state('LOCATION')
        else:
            self.minigame.show_message("Попробуй ещё раз!", COLORS['RED'])

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.minigame.handle_event(event)

    def update(self, dt):
        self.minigame.update(dt)

    def draw(self, surface):
        # Рисуем фон локации
        loc = self.game.get_location_data(self.location_num)
        if loc:
            bg_key = loc.get('background')
            bg = self.game.assets.get_image(bg_key)
            if bg:
                surface.blit(bg, (0, 0))
        # Затемнение
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 180))  # полупрозрачный чёрный
        surface.blit(dark, (0, 0))
        # Отрисовка мини-игры
        self.minigame.draw(surface)
        self.back_btn.draw(surface)


class WinScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = game.assets.fonts['title']
        self.font_large = game.assets.fonts['large']
        self.btn_reward = Button(pygame.Rect(SCREEN_WIDTH//2-200, 500, 180, 60), "Забрать награду",
                                 game.assets.fonts['medium'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                 callback=self.game.finish_game)
        self.btn_replay = Button(pygame.Rect(SCREEN_WIDTH//2+20, 500, 180, 60), "Играть ещё раз",
                                 game.assets.fonts['medium'], COLORS['BLUE'], COLORS['LIGHT_BLUE'],
                                 callback=self.game.reset_game)

    def handle_event(self, event):
        self.btn_reward.handle_event(event)
        self.btn_replay.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.get_image('win_bg')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['GOLD'])
        title = self.font_title.render("ПОЗДРАВЛЯЮ!", True, COLORS['PURPLE'])
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))
        line2 = self.font_large.render("Ты раскрыл дело о Призраке Библиотеки!", True, COLORS['DARK_BLUE'])
        surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH//2, 200)))
        word = self.font_large.render(f"Собранное слово: {self.game.collected_letters}", True, COLORS['RED'])
        surface.blit(word, word.get_rect(center=(SCREEN_WIDTH//2, 280)))
        stars = "⭐" * self.game.stars
        star_surf = self.font_title.render(stars, True, COLORS['GOLD'])
        surface.blit(star_surf, star_surf.get_rect(center=(SCREEN_WIDTH//2, 360)))
        self.btn_reward.draw(surface)
        self.btn_replay.draw(surface)


# ---------- ГЛАВНЫЙ КЛАСС ИГРЫ ----------
class LibraryGame:
    def __init__(self, surface: pygame.Surface, db_config: Dict, child_id: int, username: str,
                 on_exit: Callable = None, on_finish: Callable = None):
        self.surface = surface
        self.child_id = child_id
        self.username = username
        self.on_exit = on_exit or (lambda: None)
        self.on_finish = on_finish or (lambda: None)

        self.assets = AssetCache()
        self.assets.play_music('bg_music', loop=-1)

        # Прогресс
        self.load_progress()
        self.state_name = 'LOADING'
        self.current_screen = None
        self.running = True

        self.screens = {
            'LOADING': LoadingScreen(self),
            'PROLOG': PrologScreen(self),
            'MAP': MapScreen(self),
            'LOCATION': LocationScreen(self),
            'WIN': WinScreen(self),
        }
        self.set_state('LOADING')

    def get_location_data(self, loc_num):
        locations = {
            1: {'name': 'Читальный зал', 'background': 'reading_hall_bg', 'npc_name': 'Библиотекарь', 'npc_dialogue': 'Ох, эти книги совсем расшалились! Помоги расставить их по порядку, и я покажу тебе странные знаки.', 'letter': 'В'},
            2: {'name': 'Детский абонемент', 'background': 'kids_section_bg', 'npc_name': 'Шэгги', 'npc_dialogue': 'Мы тут нашли какие-то странные следы… Но сначала — задания!', 'letter': 'О'},
            3: {'name': 'Книгохранилище', 'background': 'book_storage_bg', 'npc_name': 'Фред', 'npc_dialogue': 'Чтобы поймать призрака, нужно знать время и уметь двигать стеллажи. Готов?', 'letter': 'Р'},
            4: {'name': 'Кабинет библиотекаря', 'background': 'office_bg', 'npc_name': 'Велма', 'npc_dialogue': 'Я нашла странные записи и разлитые чернила. Давай разбираться по порядку.', 'letter': 'О'},
            5: {'name': 'Подвал', 'background': 'basement_bg', 'npc_name': 'Скуби', 'npc_dialogue': 'С-с-страшно, но мы храбрые! Там на стене какие-то символы. Может, шифр?', 'letter': 'Н'},
            6: {'name': 'Чердак', 'background': 'attic_bg', 'npc_name': 'Велма', 'npc_dialogue': 'Смотрите! Следы ведут к окну. А на стене — символы… такие же, как внизу.', 'letter': 'А'}
        }
        return locations.get(loc_num)

    def load_progress(self):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                self.completed_locations = data.get('completed_locations', [])
                self.collected_letters = data.get('collected_letters', '')
                self.location_tasks_completed = data.get('location_tasks_completed', {})
                self.stars = data.get('stars', 0)
        except:
            self.completed_locations = []
            self.collected_letters = ''
            self.location_tasks_completed = {}
            self.stars = 0

    def save_progress(self):
        data = {
            'completed_locations': self.completed_locations,
            'collected_letters': self.collected_letters,
            'location_tasks_completed': self.location_tasks_completed,
            'stars': self.stars,
        }
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f)

    def set_state(self, state: str, **kwargs):
        self.state_name = state
        if state == 'TASK':
            task = kwargs.get('task')
            loc_num = kwargs.get('location_num')
            self.current_screen = TaskScreen(self, task, loc_num)
        else:
            screen = self.screens[state]
            if state == 'LOCATION':
                screen.on_enter()
            self.current_screen = screen

    def handle_event(self, event: pygame.event.Event):
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt: float):
        if self.current_screen:
            self.current_screen.update(dt)

    def draw(self):
        if self.current_screen:
            self.current_screen.draw(self.surface)

    def exit_game(self):
        self.save_progress()
        self.running = False
        self.on_exit()

    def finish_game(self):
        self.stars = 1
        self.save_progress()
        self.running = False
        self.on_finish()

    def reset_game(self):
        self.completed_locations = []
        self.collected_letters = ''
        self.location_tasks_completed = {}
        self.stars = 0
        self.save_progress()
        self.set_state('PROLOG')


# ---------- ФУНКЦИЯ ДЛЯ ИНТЕГРАЦИИ ----------
def create_library_game(surface: pygame.Surface, db_config: Dict, child_id: int, username: str,
                        on_exit: Callable = None, on_finish: Callable = None) -> LibraryGame:
    return LibraryGame(surface, db_config, child_id, username, on_exit, on_finish)