# ==================== LIBRARY_GHOST_GAME.PY ====================
"""
Игра "Дело о Призраке Библиотеки" для детей 6–7 лет.
Полная версия, использующая ассеты из assets/game3/.
"""

import pygame
import os
import random
import math
from typing import Dict, List, Optional, Any, Tuple, Callable
from database import db_manager

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
        self._load_image('closed_book', os.path.join(ITEMS_PATH, 'cause_effect', 'closed_book.png'), (200, 150))
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
        self._load_image('wall_horizontal', os.path.join(ITEMS_PATH, 'maze', 'wall_horizontal.jpg'), (80, 20))
        self._load_image('wall_vertical', os.path.join(ITEMS_PATH, 'maze', 'wall_vertical.png'), (20, 80))
        self._load_image('cap', os.path.join(ITEMS_PATH, 'rebus', 'cap-bg.png'), (100, 100))
        self._load_image('fish', os.path.join(ITEMS_PATH, 'rebus', 'fish.png'), (100, 100))
        self._load_image('window', os.path.join(ITEMS_PATH, 'rebus', 'window.png'), (100, 100))
        self._load_image('nose', os.path.join(ITEMS_PATH, 'rebus', 'nose.png'), (100, 100))
        self._load_image('watermelon', os.path.join(ITEMS_PATH, 'rebus', 'watermelon.png'), (100, 100))
        self._load_image('number_1', os.path.join(ITEMS_PATH, 'numbers', 'number_1.png'), (100, 100))
        self._load_image('number_2', os.path.join(ITEMS_PATH, 'numbers', 'number_2.png'), (100, 100))
        self._load_image('number_3', os.path.join(ITEMS_PATH, 'numbers', 'number_3.png'), (100, 100))
        self._load_image('number_4', os.path.join(ITEMS_PATH, 'numbers', 'number_4.png'), (100, 100))
        self._load_image('number_5', os.path.join(ITEMS_PATH, 'numbers', 'number_5.png'), (100, 100))
        self._load_image('number_6', os.path.join(ITEMS_PATH, 'numbers', 'number_6.png'), (100, 100))
        self._load_image('number_7', os.path.join(ITEMS_PATH, 'numbers', 'number_7.png'), (100, 100))
        self._load_image('number_8', os.path.join(ITEMS_PATH, 'numbers', 'number_8.png'), (100, 100))
        self._load_image('number_9', os.path.join(ITEMS_PATH, 'numbers', 'number_9.png'), (100, 100))
        self._load_image('number_10', os.path.join(ITEMS_PATH, 'numbers', 'number_10.png'), (100, 100))
        self._load_image('number_11', os.path.join(ITEMS_PATH, 'numbers', 'number_11.png'), (100, 100))
        self._load_image('number_12', os.path.join(ITEMS_PATH, 'numbers', 'number_12.png'), (100, 100))
        self._load_image('number_13', os.path.join(ITEMS_PATH, 'numbers', 'number_13.png'), (100, 100))
        self._load_image('number_14', os.path.join(ITEMS_PATH, 'numbers', 'number_14.png'), (100, 100))
        self._load_image('number_15', os.path.join(ITEMS_PATH, 'numbers', 'number_15.png'), (100, 100))
        self._load_image('number_16', os.path.join(ITEMS_PATH, 'numbers', 'number_16.png'), (100, 100))
        self._load_image('number_17', os.path.join(ITEMS_PATH, 'numbers', 'number_17.png'), (100, 100))
        self._load_image('number_18', os.path.join(ITEMS_PATH, 'numbers', 'number_18.png'), (100, 100))
        self._load_image('number_19', os.path.join(ITEMS_PATH, 'numbers', 'number_19.png'), (100, 100))
        self._load_image('number_20', os.path.join(ITEMS_PATH, 'numbers', 'number_20.png'), (100, 100))
        self._load_image('star', os.path.join(ITEMS_PATH, 'star.png'), (200, 200))
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
        # Слоты хранят ссылки на книги (None или объект книги)
        self.slots = [None, None, None]
        self.books = []
        # Исходные позиции для книг внизу
        positions = [(300, 500), (450, 500), (600, 500)]
        numbers = [3, 1, 2]
        for i, num in enumerate(numbers):
            img = assets.get_image(f'book_{num}')
            if img is None:
                img = pygame.Surface((80, 100))
                img.fill(COLORS['ORANGE'])
            rect = pygame.Rect(positions[i][0], positions[i][1], 80, 100)
            self.books.append({
                'img': img,
                'rect': rect,
                'num': num,
                'start_pos': positions[i],
                'dragging': False,
                'drag_offset': (0, 0),
                'slot_idx': None  # индекс слота, если книга в слоте
            })
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
                    # Если книга была в слоте, освобождаем слот
                    if b['slot_idx'] is not None:
                        self.slots[b['slot_idx']] = None
                        b['slot_idx'] = None
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self.books:
                if b['dragging']:
                    b['dragging'] = False
                    # Проверяем попадание в какой-либо слот
                    placed = False
                    for idx, slot_rect in enumerate(self.slot_rects):
                        if b['rect'].colliderect(slot_rect):
                            if self.slots[idx] is None:
                                # Слот свободен – ставим книгу
                                b['rect'].center = slot_rect.center
                                self.slots[idx] = b
                                b['slot_idx'] = idx
                                self.assets.play_sound('book_move')
                                placed = True
                                break
                    if not placed:
                        # Проверяем, не отпустили ли книгу в нижнюю область (возврат)
                        if b['rect'].y > 400:  # примерно область внизу
                            b['rect'].topleft = b['start_pos']
                            b['slot_idx'] = None
                        else:
                            # Иначе возвращаем на прежнее место (если была в слоте – вернём в слот, но слот уже пуст)
                            if b['slot_idx'] is not None:
                                b['rect'].center = self.slot_rects[b['slot_idx']].center
                            else:
                                b['rect'].topleft = b['start_pos']
                    # После каждого перемещения пересчитываем содержимое слотов
                    # (на случай, если книга вытащена, слот уже очищен)
                    break
        elif event.type == pygame.MOUSEMOTION:
            for b in self.books:
                if b['dragging']:
                    b['rect'].x = event.pos[0] + b['drag_offset'][0]
                    b['rect'].y = event.pos[1] + b['drag_offset'][1]

    def check(self):
        # Проверяем, что в слотах книги с номерами 1,2,3 по порядку
        if (self.slots[0] is not None and self.slots[0]['num'] == 1 and
            self.slots[1] is not None and self.slots[1]['num'] == 2 and
            self.slots[2] is not None and self.slots[2]['num'] == 3):
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Нет, начни с единицы!", COLORS['RED'])

    def draw(self, surface):
        # Рисуем пустые слоты
        for rect in self.slot_rects:
            pygame.draw.rect(surface, COLORS['BROWN'], rect, 3)
        # Рисуем книги (все)
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
        # Загружаем спрайты
        self.sprites = {
            'red_book': assets.get_image('book_red'),
            'blue_book': assets.get_image('book_blue'),
            'green_notebook': assets.get_image('book_green')
        }
        # Если нет зелёной книги, создадим зелёный прямоугольник
        if self.sprites['green_notebook'] is None:
            self.sprites['green_notebook'] = pygame.Surface((80, 100))
            self.sprites['green_notebook'].fill(COLORS['GREEN'])
        
        # Перетаскиваемые варианты (находятся снизу)
        self.options = [
            {'sprite': self.sprites['red_book'], 'rect': pygame.Rect(150, 500, 80, 100), 'type': 'red',
             'dragging': False, 'drag_offset': (0,0), 'placed': False},
            {'sprite': self.sprites['blue_book'], 'rect': pygame.Rect(350, 500, 80, 100), 'type': 'blue',
             'dragging': False, 'drag_offset': (0,0), 'placed': False},
            {'sprite': self.sprites['green_notebook'], 'rect': pygame.Rect(550, 500, 80, 100), 'type': 'green',
             'dragging': False, 'drag_offset': (0,0), 'placed': False}
        ]
        # Слот для варианта (пустое место в ряду)
        self.slot_rect = pygame.Rect(600, 250, 80, 100)
        self.placed_option = None  # какой вариант сейчас в слоте
        
        # Ряд с образцом: красная, синяя, красная
        self.row_sprites = [
            self.sprites['red_book'],
            self.sprites['blue_book'],
            self.sprites['red_book']
        ]
        self.row_positions = [(150, 250), (300, 250), (450, 250)]
        
        self.correct_type = 'blue'  # правильный вариант – синяя книга
        
        # Кнопка проверки
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = self.options + [self.check_btn]

    def handle_event(self, event):
        super().handle_event(event)  # для кнопки проверки
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for opt in self.options:
                if not opt['placed'] and opt['rect'].collidepoint(event.pos):
                    opt['dragging'] = True
                    opt['drag_offset'] = (opt['rect'].x - event.pos[0], opt['rect'].y - event.pos[1])
                    self.assets.play_sound('click')
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for opt in self.options:
                if opt['dragging']:
                    opt['dragging'] = False
                    # Проверяем, попал ли вариант в слот
                    if opt['rect'].colliderect(self.slot_rect) and self.placed_option is None:
                        # Помещаем в слот
                        opt['rect'].center = self.slot_rect.center
                        opt['placed'] = True
                        self.placed_option = opt
                        self.assets.play_sound('book_move')
                    else:
                        # Возвращаем на исходную позицию
                        self._reset_option_position(opt)
                    break
        elif event.type == pygame.MOUSEMOTION:
            for opt in self.options:
                if opt['dragging']:
                    opt['rect'].x = event.pos[0] + opt['drag_offset'][0]
                    opt['rect'].y = event.pos[1] + opt['drag_offset'][1]

    def _reset_option_position(self, opt):
        # Возвращает вариант на исходную позицию по его типу
        orig = {'red': (150, 500), 'blue': (350, 500), 'green': (550, 500)}
        opt['rect'].topleft = orig.get(opt['type'], (150, 500))
        opt['placed'] = False

    def check(self):
        if self.placed_option is None:
            self.show_message("Сначала положи вариант в пустое место!", COLORS['YELLOW'])
            self.assets.play_sound('fail')
            return
        if self.placed_option['type'] == self.correct_type:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Посмотри внимательно: цвета чередуются. Красный, синий, красный… какой следующий?")
            # Возвращаем неправильный вариант на место
            self._reset_option_position(self.placed_option)
            self.placed_option = None

    def draw(self, surface):
        # Рисуем ряд с образцом (первые три книги)
        for i, sprite in enumerate(self.row_sprites):
            if sprite:
                surface.blit(sprite, self.row_positions[i])
            else:
                pygame.draw.rect(surface, COLORS['GRAY'], pygame.Rect(self.row_positions[i][0], self.row_positions[i][1], 80, 100))
        # Рисуем пустой слот (вопросительный знак)
        pygame.draw.rect(surface, COLORS['WHITE'], self.slot_rect, 3)
        if self.placed_option is None:
            font = self.assets.fonts['large']
            q_mark = font.render("?", True, COLORS['WHITE'])
            surface.blit(q_mark, q_mark.get_rect(center=self.slot_rect.center))
        else:
            # Отрисовываем вариант, лежащий в слоте
            surface.blit(self.placed_option['sprite'], self.slot_rect)
        
        # Рисуем перетаскиваемые варианты (только неразмещённые)
        for opt in self.options:
            if not opt['placed']:
                surface.blit(opt['sprite'], opt['rect'])
        
        title = self.assets.fonts['medium'].render("Перетащи правильный предмет в пустое место", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.check_btn.draw(surface)
        super().draw(surface)


# 2.1 Состав числа
class NumberCompositionMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.types = ['apple', 'ball', 'cookie']
        self.sprites = {}
        for t in self.types:
            img = assets.get_image(t)
            if img is None:
                surf = pygame.Surface((25, 25), pygame.SRCALPHA)
                color = {'apple': (255, 0, 0), 'ball': (255, 165, 0), 'cookie': (139, 69, 19)}[t]
                pygame.draw.circle(surf, color, (12, 12), 12)
                img = surf
            self.sprites[t] = img

        self.seven_img = assets.get_image('number_7')
        if self.seven_img is None:
            self.seven_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            font = assets.fonts['large']
            seven_text = font.render("7", True, COLORS['GOLD'])
            self.seven_img.blit(seven_text, (5, 5))

        self.groups = {}
        self.combined_sevens = {}
        self.layout()
        self.dragging = None
        self.drag_offset = (0, 0)
        self.completed_types = set()
        self.message_label = None
        self.message_timer = 0

    def layout(self):
        type_positions = {
            'apple': 150,
            'ball': SCREEN_WIDTH // 2 - 55,
            'cookie': SCREEN_WIDTH - 260
        }
        y_start = 150
        y_step = 200
        for t in self.types:
            x = random.randint(1, 5)
            y = 7 - x
            if y == x:
                x = random.choice([1,2,3])
                y = 7 - x
            possible_z = [i for i in range(1,7) if i != x and i != y and (i + x) != 7 and (i + y) != 7]
            z = random.choice(possible_z) if possible_z else 3
            counts = [x, y, z]
            random.shuffle(counts)

            self.groups[t] = []
            for idx, cnt in enumerate(counts):
                rect = pygame.Rect(type_positions[t], y_start + idx * y_step, 110, 100)
                self.groups[t].append({
                    'count': cnt,
                    'rect': rect,
                    'original_pos': (rect.x, rect.y),
                    'active': True,
                    'locked': False,
                    'combined': False
                })

    def _draw_group(self, surface, sprite, count, rect, combined=False):
        w, h = 60, 60
        step_x = 35   # горизонтальный шаг
        step_y = 35   # вертикальный шаг

        rows = 0
        while (rows * (rows + 1)) // 2 < count:
            rows += 1

        # Ширина и высота всей пирамиды
        total_width = (rows - 1) * step_x + w
        total_height = (rows - 1) * step_y + h
        start_x = rect.centerx - total_width // 2
        start_y = rect.centery - total_height // 2

        drawn = 0
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for row in range(rows):
            items_in_row = row + 1
            if drawn + items_in_row > count:
                items_in_row = count - drawn
            row_width = (items_in_row - 1) * step_x + w
            row_start_x = rect.centerx - row_width // 2
            for col in range(items_in_row):
                x = row_start_x + col * step_x
                y = start_y + row * step_y
                surface.blit(sprite, (x, y))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + w)
                max_y = max(max_y, y + h)
                drawn += 1
                if drawn >= count:
                    break
            if drawn >= count:
                break

        if drawn > 0:
            box_rect = pygame.Rect(min_x - 5, min_y - 5, max_x - min_x + 10, max_y - min_y + 10)
            color = COLORS['GOLD'] if combined else COLORS['WHITE']
            pygame.draw.rect(surface, color, box_rect, 3)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for t in self.types:
                for idx, g in enumerate(self.groups[t]):
                    if g['active'] and not g['locked'] and g['rect'].collidepoint(event.pos):
                        self.dragging = (t, idx)
                        self.drag_offset = (g['rect'].x - event.pos[0], g['rect'].y - event.pos[1])
                        self.assets.play_sound('click')
                        break
                if self.dragging:
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                t, idx = self.dragging
                g = self.groups[t][idx]
                target = None
                for i, other in enumerate(self.groups[t]):
                    if i != idx and other['active'] and not other['locked'] and other['rect'].colliderect(g['rect']):
                        target = other
                        break
                if target and (g['count'] + target['count'] == 7):
                    self.assets.play_sound('success')
                    # Помечаем группы как заблокированные (нельзя перетаскивать)
                    for grp in self.groups[t]:
                        grp['locked'] = True
                        grp['combined'] = True
                    # Находим третью группу и делаем неактивной
                    for third in self.groups[t]:
                        if third != g and third != target:
                            third['active'] = False
                    # Вычисляем позицию для семёрки между центрами
                    center_x = (g['rect'].centerx + target['rect'].centerx) // 2
                    center_y = (g['rect'].centery + target['rect'].centery) // 2
                    self.combined_sevens[t] = (center_x, center_y)
                    self.completed_types.add(t)
                    if len(self.completed_types) == 3:
                        self.complete(True)
                else:
                    g['rect'].x, g['rect'].y = g['original_pos']
                    self.assets.play_sound('fail')
                    self.show_message("Сложи две группы одного предмета, чтобы получилось 7!", COLORS['RED'], 2)
                self.dragging = None
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                t, idx = self.dragging
                g = self.groups[t][idx]
                g['rect'].x = event.pos[0] + self.drag_offset[0]
                g['rect'].y = event.pos[1] + self.drag_offset[1]

    def draw(self, surface):
        for t in self.types:
            for g in self.groups[t]:
                if not g['active']:
                    continue
                self._draw_group(surface, self.sprites[t], g['count'], g['rect'], g['combined'])
        for t, pos in self.combined_sevens.items():
            if self.seven_img:
                rect = self.seven_img.get_rect(center=pos)
                surface.blit(self.seven_img, rect)
        super().draw(surface)


# 2.2 Найди пару букв
class MemoryLettersMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.cards = [
            {'letter': 'А', 'flipped': False, 'matched': False},
            {'letter': 'А', 'flipped': False, 'matched': False},
            {'letter': 'Б', 'flipped': False, 'matched': False},
            {'letter': 'В', 'flipped': False, 'matched': False}
        ]
        random.shuffle(self.cards)
        self.selected_index = None
        self.waiting = False
        self.wait_timer = 0
        self.pending_flip_back = []
        # Карточки без Button – просто прямоугольники
        self.card_rects = []
        card_width = 150
        card_height = 150
        spacing = 30
        start_x = (SCREEN_WIDTH - (card_width * 2 + spacing)) // 2
        start_y = (SCREEN_HEIGHT - (card_height * 2 + spacing)) // 2
        for i in range(4):
            col = i % 2
            row = i // 2
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing)
            self.card_rects.append(pygame.Rect(x, y, card_width, card_height))

    def handle_event(self, event):
        if self.waiting:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(pos):
                    self.reveal_card(idx)
                    break
        super().handle_event(event)  # если есть другие кнопки (например, "Назад")

    def reveal_card(self, idx):
        card = self.cards[idx]
        if card['flipped'] or card['matched']:
            return
        # Открываем
        card['flipped'] = True
        self.assets.play_sound('click')
        if self.selected_index is None:
            self.selected_index = idx
        else:
            first = self.cards[self.selected_index]
            second = card
            if first['letter'] == second['letter']:
                first['matched'] = True
                second['matched'] = True
                first['flipped'] = True
                second['flipped'] = True
                self.selected_index = None
                self.assets.play_sound('success')
                if all(c['matched'] or c['letter'] != 'А' for c in self.cards):
                    self.complete(True)
            else:
                self.waiting = True
                self.wait_timer = 750
                self.pending_flip_back = [self.selected_index, idx]
                self.selected_index = None

    def update(self, dt):
        if self.waiting:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                for idx in self.pending_flip_back:
                    if not self.cards[idx]['matched']:
                        self.cards[idx]['flipped'] = False
                self.pending_flip_back = []
                self.waiting = False
        super().update(dt)

    def draw(self, surface):
        # Рисуем карточки
        for i, rect in enumerate(self.card_rects):
            card = self.cards[i]
            # Рисуем фон карточки
            if card['flipped'] or card['matched']:
                color = COLORS['WHITE']
                pygame.draw.rect(surface, color, rect, border_radius=10)
                pygame.draw.rect(surface, COLORS['BLACK'], rect, 2, border_radius=10)
                # Рисуем букву
                letter_surf = self.assets.fonts['large'].render(card['letter'], True, COLORS['BLACK'])
                surface.blit(letter_surf, letter_surf.get_rect(center=rect.center))
            else:
                color = COLORS['LIGHT_BLUE']
                pygame.draw.rect(surface, color, rect, border_radius=10)
                pygame.draw.rect(surface, COLORS['BLACK'], rect, 2, border_radius=10)
                # Можно нарисовать вопросительный знак
                q_surf = self.assets.fonts['large'].render("?", True, COLORS['DARK_GRAY'])
                surface.blit(q_surf, q_surf.get_rect(center=rect.center))
        title = self.assets.fonts['medium'].render("Найди пару одинаковых букв (А и А)", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        super().draw(surface)


# 3.1 Часы
class ClockMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        self.radius = 150

        # Возможные целевые времена
        possible_times = [(h, m) for h in range(1, 13) for m in (0, 15, 30, 45)]
        self.target_time = random.choice(possible_times)
        # Начальное случайное, отличное от целевого
        start_options = [t for t in possible_times if t != self.target_time]
        self.start_time = random.choice(start_options)
        self.current_hour, self.current_min = self.start_time

        self.dragging = None  # 'hour' или 'minute'
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 100, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = [self.check_btn]

    def _angle_to_time(self, angle_deg, is_hour):
        """Преобразует угол (0° = вверх, по часовой стрелке) в часы (1-12) или минуты (0-59)."""
        if is_hour:
            # 1 час = 30 градусов
            hour = (angle_deg / 30) % 12
            return 12 if hour < 0.5 else int(round(hour))
        else:
            minute = (angle_deg / 6) % 60
            return int(round(minute))

    def _time_to_angle(self, hour, minute, is_hour):
        if is_hour:
            return (hour % 12) * 30
        else:
            return minute * 6

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Вычисляем позиции стрелок
            angle_h = self._time_to_angle(self.current_hour, self.current_min, True)
            rad_h = math.radians(90 - angle_h)
            end_h = (self.center[0] + 80 * math.cos(rad_h), self.center[1] - 80 * math.sin(rad_h))
            angle_m = self._time_to_angle(self.current_hour, self.current_min, False)
            rad_m = math.radians(90 - angle_m)
            end_m = (self.center[0] + 110 * math.cos(rad_m), self.center[1] - 110 * math.sin(rad_m))

            if pygame.Rect(end_h[0]-15, end_h[1]-15, 30, 30).collidepoint(event.pos):
                self.dragging = 'hour'
            elif pygame.Rect(end_m[0]-15, end_m[1]-15, 30, 30).collidepoint(event.pos):
                self.dragging = 'minute'

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            # Угол от вертикали (вверх = 0°) по часовой стрелке
            angle = math.degrees(math.atan2(dx, -dy))  # исправлено для правильного направления
            if angle < 0:
                angle += 360
            if self.dragging == 'hour':
                self.current_hour = self._angle_to_time(angle, True)
            elif self.dragging == 'minute':
                self.current_min = self._angle_to_time(angle, False)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = None

    def check(self):
        if (self.current_hour, self.current_min) == self.target_time:
            self.assets.play_sound('clock_chime')
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message(f"Нужно поставить {self.target_time[0]}:{self.target_time[1]:02d}", COLORS['RED'])

    def draw(self, surface):
        # Циферблат
        pygame.draw.circle(surface, COLORS['WHITE'], self.center, self.radius, 3)
        for i in range(1, 13):
            angle = math.radians(90 - i * 30)
            x1 = self.center[0] + (self.radius - 20) * math.cos(angle)
            y1 = self.center[1] - (self.radius - 20) * math.sin(angle)
            x2 = self.center[0] + (self.radius - 5) * math.cos(angle)
            y2 = self.center[1] - (self.radius - 5) * math.sin(angle)
            pygame.draw.line(surface, COLORS['WHITE'], (x1, y1), (x2, y2), 2)
            num = self.assets.fonts['small'].render(str(i), True, COLORS['WHITE'])
            x_text = self.center[0] + (self.radius - 35) * math.cos(angle) - num.get_width() // 2
            y_text = self.center[1] - (self.radius - 35) * math.sin(angle) - num.get_height() // 2
            surface.blit(num, (x_text, y_text))

        # Часовая стрелка (белая)
        angle_h = self._time_to_angle(self.current_hour, self.current_min, True)
        rad_h = math.radians(90 - angle_h)
        end_h = (self.center[0] + 80 * math.cos(rad_h), self.center[1] - 80 * math.sin(rad_h))
        pygame.draw.line(surface, COLORS['WHITE'], self.center, end_h, 6)

        # Минутная стрелка (белая)
        angle_m = self._time_to_angle(self.current_hour, self.current_min, False)
        rad_m = math.radians(90 - angle_m)
        end_m = (self.center[0] + 110 * math.cos(rad_m), self.center[1] - 110 * math.sin(rad_m))
        pygame.draw.line(surface, COLORS['WHITE'], self.center, end_m, 4)

        self.check_btn.draw(surface)
        title = self.assets.fonts['medium'].render(f"Поставь стрелки на {self.target_time[0]}:{self.target_time[1]:02d}", True, COLORS['WHITE'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        super().draw(surface)


# 3.2 Лабиринт (передвинь стеллаж)
class MazeMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.pos = (0, 0)
        self.target = (3, 3)
        # Стены (оставляем логику)
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
        # Загружаем спрайты стеллажа и выхода
        self.bookshelf_img = assets.get_image('bookshelf_maze')
        self.exit_img = assets.get_image('exit_door')
        if self.bookshelf_img is None:
            self.bookshelf_img = pygame.Surface((70, 70))
            self.bookshelf_img.fill(COLORS['GREEN'])
        if self.exit_img is None:
            self.exit_img = pygame.Surface((70, 70))
            self.exit_img.fill(COLORS['GOLD'])
        self.bookshelf_img = pygame.transform.scale(self.bookshelf_img, (70, 70))
        self.exit_img = pygame.transform.scale(self.exit_img, (70, 70))

        # Загружаем спрайты стен
        self.wall_h_img = assets.get_image('wall_horizontal')
        self.wall_v_img = assets.get_image('wall_vertical')
        if self.wall_h_img is None:
            self.wall_h_img = pygame.Surface((80, 20))
            self.wall_h_img.fill(COLORS['RED'])
        else:
            self.wall_h_img = pygame.transform.scale(self.wall_h_img, (80, 20))
        if self.wall_v_img is None:
            self.wall_v_img = pygame.Surface((20, 80))
            self.wall_v_img.fill(COLORS['RED'])
        else:
            self.wall_v_img = pygame.transform.scale(self.wall_v_img, (20, 80))

        # Убираем кнопки-стрелки, оставляем только перетаскивание (по желанию можно вернуть)
        self.dragging = False
        self.drag_offset = (0, 0)

        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts['small'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = [self.check_btn]

    def check(self):
        if self.pos == self.target:
            self.assets.play_sound('success')
            self.complete(True)
        else:
            self.assets.play_sound('fail')
            self.show_message("Стеллаж ещё не у выхода!", COLORS['RED'])

    def handle_event(self, event):
        super().handle_event(event)
        # Перетаскивание стеллажа
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell_size = 80
            offset_x = (SCREEN_WIDTH - 4*cell_size) // 2
            offset_y = 150
            rect = pygame.Rect(offset_x + self.pos[0]*cell_size, offset_y + self.pos[1]*cell_size, cell_size, cell_size)
            if rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (rect.x - event.pos[0], rect.y - event.pos[1])
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Перемещаем стеллаж (визуально), но реальное положение меняем только при отпускании
            pass
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            # Определяем, в какой клетке отпустили
            cell_size = 80
            offset_x = (SCREEN_WIDTH - 4*cell_size) // 2
            offset_y = 150
            mx, my = event.pos
            # Вычисляем координаты клетки
            grid_x = (mx - offset_x) // cell_size
            grid_y = (my - offset_y) // cell_size
            if 0 <= grid_x < 4 and 0 <= grid_y < 4:
                self.move_to(grid_x, grid_y)
            # else: остаётся на месте

    def move_to(self, nx, ny):
        # Проверка пути (по стенам) от текущей позиции до (nx, ny) - упростим: разрешаем только соседние клетки
        dx = nx - self.pos[0]
        dy = ny - self.pos[1]
        if abs(dx) + abs(dy) != 1:
            return
        if dx == 1 and self.walls[self.pos].get('right', False):
            self.show_message("Там стена!", COLORS['RED'])
            self.assets.play_sound('fail')
            return
        if dx == -1 and self.walls[(nx, ny)].get('right', False):
            self.show_message("Там стена!", COLORS['RED'])
            self.assets.play_sound('fail')
            return
        if dy == 1 and self.walls[self.pos].get('down', False):
            self.show_message("Там стена!", COLORS['RED'])
            self.assets.play_sound('fail')
            return
        if dy == -1 and self.walls[(nx, ny)].get('down', False):
            self.show_message("Там стена!", COLORS['RED'])
            self.assets.play_sound('fail')
            return
        self.pos = (nx, ny)
        self.assets.play_sound('bookshelf_move')

    def draw(self, surface):
        cell_size = 80
        offset_x = (SCREEN_WIDTH - 4*cell_size) // 2
        offset_y = 150

        for y in range(4):
            for x in range(4):
                rect = pygame.Rect(offset_x + x*cell_size, offset_y + y*cell_size, cell_size, cell_size)
                # Рамка клетки
                pygame.draw.rect(surface, COLORS['WHITE'], rect, 2)
                # Стены (спрайты)
                if self.walls[(x,y)].get('right', False):
                    # Вертикальная стена
                    wall_rect = pygame.Rect(rect.right - 10, rect.top, 20, cell_size)
                    surface.blit(self.wall_v_img, wall_rect)
                if self.walls[(x,y)].get('down', False):
                    # Горизонтальная стена
                    wall_rect = pygame.Rect(rect.left, rect.bottom - 10, cell_size, 20)
                    surface.blit(self.wall_h_img, wall_rect)

        # Стеллаж (можно перетаскивать)
        rect = pygame.Rect(offset_x + self.pos[0]*cell_size, offset_y + self.pos[1]*cell_size, cell_size, cell_size)
        img_rect = self.bookshelf_img.get_rect(center=rect.center)
        surface.blit(self.bookshelf_img, img_rect)

        # Выход
        target_rect = pygame.Rect(offset_x + self.target[0]*cell_size, offset_y + self.target[1]*cell_size, cell_size, cell_size)
        exit_rect = self.exit_img.get_rect(center=target_rect.center)
        surface.blit(self.exit_img, exit_rect)

        self.check_btn.draw(surface)

        title = self.assets.fonts['medium'].render("Перетащи стеллаж к выходу (золотая дверь)", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
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
        # Загружаем спрайты следствий
        self.puddle_img = assets.get_image('puddle')
        self.lamp_img = assets.get_image('lamp')
        self.closed_book_img = assets.get_image('closed_book')
        # Если нет – создаём заглушки
        if self.puddle_img is None:
            self.puddle_img = pygame.Surface((150, 150))
            self.puddle_img.fill(COLORS['BLUE'])
        if self.lamp_img is None:
            self.lamp_img = pygame.Surface((150, 150))
            self.lamp_img.fill(COLORS['YELLOW'])
        if self.closed_book_img is None:
            self.closed_book_img = pygame.Surface((150, 150))
            self.closed_book_img.fill(COLORS['GREEN'])
        # Масштабируем
        size = (150, 150)
        self.puddle_img = pygame.transform.scale(self.puddle_img, size)
        self.lamp_img = pygame.transform.scale(self.lamp_img, size)
        self.closed_book_img = pygame.transform.scale(self.closed_book_img, size)

        # Картинка причины (окно + дождь)
        self.cause_img = assets.get_image('open_window')
        if self.cause_img is None:
            self.cause_img = pygame.Surface((300, 200))
            self.cause_img.fill(COLORS['LIGHT_BLUE'])
        else:
            self.cause_img = pygame.transform.scale(self.cause_img, (300, 200))
        self.rain_img = assets.get_image('rain')
        if self.rain_img is None:
            self.rain_img = pygame.Surface((300, 200), pygame.SRCALPHA)
        else:
            self.rain_img = pygame.transform.scale(self.rain_img, (300, 200))

        # Позиции трёх вариантов
        self.option_rects = []
        start_x = SCREEN_WIDTH // 2 - 250
        y = 450
        self.option_rects.append(pygame.Rect(start_x, y, 150, 150))      # лужа
        self.option_rects.append(pygame.Rect(start_x + 180, y, 150, 150)) # лампа
        self.option_rects.append(pygame.Rect(start_x + 360, y, 150, 150)) # закрытая книга
        self.correct_index = 0  # лужа

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    if i == self.correct_index:
                        self.assets.play_sound('success')
                        self.complete(True)
                    else:
                        self.assets.play_sound('fail')
                        self.show_message("Если окно открыто и идёт дождь — что случится с полом?")

    def draw(self, surface):
        # Причина
        cause_x = SCREEN_WIDTH // 2 - 150
        surface.blit(self.cause_img, (cause_x, 150))
        if self.rain_img:
            surface.blit(self.rain_img, (cause_x, 150))
        # Варианты следствий
        surface.blit(self.puddle_img, self.option_rects[0])
        surface.blit(self.lamp_img, self.option_rects[1])
        surface.blit(self.closed_book_img, self.option_rects[2])
        # Подписи
        font = self.assets.fonts['small']
        labels = ["Лужа", "Лампа", "Закрытая книга"]
        for i, rect in enumerate(self.option_rects):
            label = font.render(labels[i], True, COLORS['WHITE'])
            surface.blit(label, label.get_rect(center=(rect.centerx, rect.bottom + 15)))
        title = self.assets.fonts['medium'].render("Выбери правильное следствие", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        super().draw(surface)

# 5.1 Ребус
class RebusMinigame(BaseMinigame):
    def __init__(self, assets, on_complete):
        super().__init__(assets, on_complete)
        self.pictures = [("cap", "К"), ("fish", "Р"), ("window", "О"), ("nose", "Н"), ("watermelon", "А")]
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
        self.clicked = [False] * 21  # индекс 1..20
        self.number_sprites = {}
        self.number_rects = []

        # Загружаем спрайты для цифр 1–20
        for i in range(1, 21):
            img = assets.get_image(f'number_{i}')
            if img is None:
                # Заглушка: рисуем цифру на поверхности
                img = pygame.Surface((60, 60), pygame.SRCALPHA)
                font = assets.fonts['medium']
                text = font.render(str(i), True, COLORS['WHITE'])
                img.blit(text, text.get_rect(center=(30, 30)))
                pygame.draw.rect(img, COLORS['WHITE'], img.get_rect(), 2)
            else:
                img = pygame.transform.scale(img, (60, 60))
            self.number_sprites[i] = img

        # Располагаем в сетке 5x4
        start_x = 150
        start_y = 200
        cols = 5
        spacing_x = 80
        spacing_y = 80
        for i in range(1, 21):
            row = (i - 1) // cols
            col = (i - 1) % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            rect = pygame.Rect(x, y, 60, 60)
            self.number_rects.append((i, rect))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for num, rect in self.number_rects:
                if rect.collidepoint(event.pos) and not self.clicked[num]:
                    if num % 2 == 0:
                        self.clicked[num] = True
                        self.assets.play_sound('click')
                        # Проверяем, все ли чётные нажаты
                        if all(self.clicked[i] for i in range(2, 21, 2)):
                            self.assets.play_sound('success')
                            self.complete(True)
                    else:
                        self.assets.play_sound('fail')
                        self.show_message(f"Число {num} нечётное! Нужны только чётные.", COLORS['RED'], 1.5)
                    break  # обработали один клик

    def draw(self, surface):
        # Фон уже нарисован в TaskScreen
        for num, rect in self.number_rects:
            sprite = self.number_sprites[num]
            surface.blit(sprite, rect)
            if self.clicked[num]:
                # Рисуем зелёную галочку или рамку поверх нажатых
                pygame.draw.rect(surface, COLORS['GREEN'], rect, 4)
        title = self.assets.fonts['medium'].render("Нажми на все чётные числа от 1 до 20", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
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
            if len(self.game.completed_locations) >= 6:
                self.game.set_state('WIN')
            elif self.game.completed_locations or self.game.collected_letters or self.game.location_tasks_completed:
                self.game.set_state('MAP')
            else:
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
        self.home_btn = Button(pygame.Rect(30, SCREEN_HEIGHT-60, 100, 40), "Домой",
                               game.assets.fonts['small'], COLORS['RED'], COLORS['ORANGE'],
                               callback=self.game.exit_game)
        self.last_completed = None

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
        if self.last_completed != self.game.completed_locations.copy():
            self.update_buttons()
            self.last_completed = self.game.completed_locations.copy()

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
        y = 200
        for t in self.tasks:
            completed = t['id'] in self.completed_tasks
            rect = pygame.Rect(200, y, 600, 50)
            
            # Создаём замыкание с фиксацией текущих значений
            def make_callback(task, is_completed):
                def callback():
                    if not is_completed:
                        self.start_task(task)
                return callback
            
            btn = Button(rect,
                        f"Задание: {t['name']}",
                        self.game.assets.fonts['small'],
                        COLORS['GREEN'] if completed else COLORS['LIGHT_BLUE'],
                        COLORS['LIGHT_GREEN'] if not completed else COLORS['GREEN'],
                        callback=make_callback(t, completed))
            btn.enabled = not completed
            self.task_buttons.append(btn)
            y += 70

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
            # Если это последняя локация (6), переходим на экран победы
            if self.game.current_location_num == 6:
                self.game.set_state('WIN')
                return
        self.game.save_progress()  # сохраняем даже если не всё выполнено
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
        self.btn_reward = Button(pygame.Rect(SCREEN_WIDTH//2-200, 500, 180, 60), "Выход",
                                 game.assets.fonts['medium'], COLORS['BLUE'], COLORS['LIGHT_BLUE'],
                                 callback=self.game.finish_game)
        self.btn_replay = Button(pygame.Rect(SCREEN_WIDTH//2+20, 500, 200, 60), "Играть ещё раз",
                                 game.assets.fonts['medium'], COLORS['GREEN'], COLORS['LIGHT_GREEN'],
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
        title = render_with_outline("ПОЗДРАВЛЯЮ!", self.font_title, COLORS['PURPLE'], COLORS['BLACK'], 2)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))
        line2 = render_with_outline("Ты раскрыл дело о Призраке Библиотеки!", self.font_large, COLORS['DARK_BLUE'], COLORS['BLACK'], 2)
        surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH//2, 200)))
        word = render_with_outline(f"Собранное слово: {self.game.collected_letters}", self.font_large, COLORS['RED'], COLORS['BLACK'], 2)
        surface.blit(word, word.get_rect(center=(SCREEN_WIDTH//2, 280)))
        star_img = self.game.assets.get_image('star')
        if star_img:
            star_rect = star_img.get_rect(center=(SCREEN_WIDTH//2, 400))
            surface.blit(star_img, star_rect)
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

        # Загружаем прогресс из БД
        progress = db_manager.load_library_progress(self.child_id)
        self.completed_locations = progress.get('completed_locations', [])
        self.collected_letters = progress.get('collected_letters', '')
        self.location_tasks_completed = progress.get('location_tasks', {})
        self.stars = progress.get('stars', 0)
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

    def save_progress(self):
        data = {
            'completed_locations': self.completed_locations,
            'collected_letters': self.collected_letters,
            'location_tasks_completed': self.location_tasks_completed,
            'stars': self.stars,
        }
        db_manager.save_library_progress(
            child_id=self.child_id,
            completed_locations=self.completed_locations,
            collected_letters=self.collected_letters,
            location_tasks=self.location_tasks_completed,
            stars=self.stars
        )

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