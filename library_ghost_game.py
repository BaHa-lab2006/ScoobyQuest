# ==================== LIBRARY_GHOST_GAME.PY ====================
"""
Игра "Дело о Призраке Библиотеки" для детей 6–7 лет.
Реализация по полному сценарию.
Модуль для встраивания в основное приложение.
Не запускает собственный главный цикл, не вызывает pygame.init()/sys.exit().
"""

import pygame
import pyodbc
import json
import os
import random
import logging
import math
from typing import Dict, List, Optional, Any, Tuple, Callable

logger = logging.getLogger(__name__)

# ---------- КОНФИГУРАЦИЯ ----------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'DARK_BLUE': (25, 25, 112),
    'BROWN': (139, 69, 19),
    'GOLD': (255, 215, 0),
    'GREEN': (0, 255, 0),
    'RED': (255, 0, 0),
    'GRAY': (128, 128, 128),
    'BLUE': (25,25, 250),
    'LIGHT_BLUE': (173, 216, 230),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0),
    'LIGHT_GREEN': (144, 238, 144),
    'DARK_GRAY': (64, 64, 64),
    'YELLOW': (255, 255, 0),
    'PINK': (255, 192, 203),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "assets", "game3")
IMAGES_PATH = os.path.join(ASSETS_PATH, "images")
SOUNDS_PATH = os.path.join(ASSETS_PATH, "sounds")
FONTS_PATH = os.path.join(ASSETS_PATH, "fonts")


# ---------- РАБОТА С БД (сохранение прогресса) ----------
class Database:
    def __init__(self, config: Dict):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:
        try:
            conn_str = (
                f"DRIVER={self.config['driver']};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']}"
            )
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def init_tables(self):
        # Упростим таблицы под нужды игры (можно оставить существующие)
        pass

    def get_child_progress(self, child_id: int, quest_id: int = 1) -> Dict:
        # Для простоты будем хранить прогресс в JSON файле, если БД нет
        # Но для совместимости оставим заглушку, возвращающую пустой прогресс
        # Реальная реализация может использовать БД, как в исходном коде
        return {
            'completed_locations': [],
            'collected_letters': '',
            'current_location': 1,
            'score': 0,
            'stars_earned': 0,
            'is_completed': False
        }

    def save_progress(self, child_id: int, quest_id: int, progress: Dict):
        pass

    def get_location(self, quest_id: int, loc_num: int) -> Optional[Dict]:
        # Имитация данных локаций (в реальности берутся из БД)
        locations = {
            1: {'id': 1, 'name': 'Читальный зал', 'background': 'reading_hall.png', 'desc': '', 'npc_name': 'Библиотекарь', 'npc_dialogue': 'Помоги расставить книги по порядку!', 'letter': 'В'},
            2: {'id': 2, 'name': 'Детский абонемент', 'background': 'kids_section.png', 'desc': '', 'npc_name': 'Скуби и Шэгги', 'npc_dialogue': 'Найди пару букв и составь число!', 'letter': 'О'},
            3: {'id': 3, 'name': 'Книгохранилище', 'background': 'book_storage.png', 'desc': '', 'npc_name': 'Фред', 'npc_dialogue': 'Поставь правильное время и пройди лабиринт!', 'letter': 'Р'},
            4: {'id': 4, 'name': 'Кабинет библиотекаря', 'background': 'office.png', 'desc': '', 'npc_name': 'Велма', 'npc_dialogue': 'Собери пазл и найди причину!', 'letter': 'О'},
            5: {'id': 5, 'name': 'Подвал', 'background': 'basement.png', 'desc': '', 'npc_name': 'Скуби и Шэгги', 'npc_dialogue': 'Расшифруй слово и посчитай!', 'letter': 'Н'},
            6: {'id': 6, 'name': 'Чердак', 'background': 'attic.png', 'desc': '', 'npc_name': 'Вся команда', 'npc_dialogue': 'Вот и наш призрак!', 'letter': 'А'},
        }
        return locations.get(loc_num)

    def get_tasks(self, location_id: int) -> List[Dict]:
        # В новой версии задания жёстко заданы в коде, а не в БД
        # Этот метод возвращает пустой список, т.к. задания будут создаваться в LocationScreen
        return []

    def add_achievement(self, child_id: int, ach_name: str):
        pass

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# ---------- КЭШ РЕСУРСОВ ----------
class AssetCache:
    def __init__(self):
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

    def load_font(self, name: str, size: int, fallback: str = 'arial') -> pygame.font.Font:
        try:
            path = os.path.join(FONTS_PATH, name)
            return pygame.font.Font(path, size)
        except Exception:
            logger.warning(f"Шрифт {name} не найден, использую {fallback}")
            return pygame.font.SysFont(fallback, size)

    def load_image(self, key: str, subpath: str, size: Tuple[int, int] = None) -> pygame.Surface:
        try:
            path = os.path.join(IMAGES_PATH, subpath)
            img = pygame.image.load(path)
            if size:
                img = pygame.transform.scale(img, size)
            self.images[key] = img
            return img
        except Exception:
            logger.warning(f"Изображение {subpath} не загружено")
            surf = pygame.Surface(size if size else (100, 100))
            surf.fill(COLORS['PURPLE'])
            return surf

    def load_sound(self, key: str, subpath: str) -> Optional[pygame.mixer.Sound]:
        try:
            path = os.path.join(SOUNDS_PATH, subpath)
            sound = pygame.mixer.Sound(path)
            self.sounds[key] = sound
            return sound
        except Exception:
            logger.warning(f"Звук {subpath} не загружен")
            return None


# ---------- UI ЭЛЕМЕНТЫ ----------
class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 color: Tuple, hover_color: Tuple, callback: Callable = None,
                 border_color: Tuple = COLORS['WHITE'], border_width: int = 3):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.border_color = border_color
        self.border_width = border_width
        self.is_hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()

    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=12)
        text_surf = self.font.render(self.text, True, COLORS['WHITE'])
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class Label:
    def __init__(self, pos: Tuple[int, int], text: str, font: pygame.font.Font, color: Tuple, center: bool = True):
        self.pos = pos
        self.text = text
        self.font = font
        self.color = color
        self.center = center
        self.surf = self.font.render(text, True, color)

    def set_text(self, text: str):
        self.text = text
        self.surf = self.font.render(text, True, self.color)

    def draw(self, surface: pygame.Surface):
        if self.center:
            rect = self.surf.get_rect(center=self.pos)
            surface.blit(self.surf, rect)
        else:
            surface.blit(self.surf, self.pos)


class DialogBubble:
    def __init__(self, rect: pygame.Rect, text: str, speaker: str = "", font_small: pygame.font.Font = None):
        self.rect = rect
        self.text = text
        self.speaker = speaker
        self.font_small = font_small

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, COLORS['WHITE'], self.rect, border_radius=20)
        pygame.draw.rect(surface, COLORS['BLACK'], self.rect, 3, border_radius=20)
        if self.speaker and self.font_small:
            sp_surf = self.font_small.render(self.speaker + ":", True, COLORS['PURPLE'])
            surface.blit(sp_surf, (self.rect.x + 15, self.rect.y + 10))
            text_y = self.rect.y + 45
        else:
            text_y = self.rect.y + 20
        # Простой перенос слов
        words = self.text.split(' ')
        lines = []
        line = ""
        for wd in words:
            test_line = line + wd + " "
            if self.font_small and self.font_small.size(test_line)[0] < self.rect.width - 30:
                line = test_line
            else:
                lines.append(line)
                line = wd + " "
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            if self.font_small:
                txt = self.font_small.render(ln, True, COLORS['BLACK'])
                surface.blit(txt, (self.rect.x + 15, text_y + i * 30))


class Draggable:
    def __init__(self, rect: pygame.Rect, image: pygame.Surface, data: Any):
        self.rect = rect
        self.image = image
        self.data = data
        self.dragging = False
        self.drag_offset = (0, 0)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (self.rect.x - event.pos[0], self.rect.y - event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.drag_offset[0]
                self.rect.y = event.pos[1] + self.drag_offset[1]

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


# ---------- БАЗОВЫЙ КЛАСС МИНИ-ИГРЫ ----------
class BaseMinigame:
    def __init__(self, task_data: Dict, assets: AssetCache, on_complete: Callable):
        self.task_data = task_data
        self.assets = assets
        self.on_complete = on_complete  # вызывается с bool (успех/провал)
        self.finished = False
        self.ui_elements: List = []
        self.message_label = None
        self.message_timer = 0

    def handle_event(self, event: pygame.event.Event):
        for el in self.ui_elements:
            if hasattr(el, 'handle_event'):
                el.handle_event(event)

    def update(self, dt: float):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_label = None

    def draw(self, surface: pygame.Surface):
        for el in self.ui_elements:
            if hasattr(el, 'draw'):
                el.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)

    def show_message(self, text: str, color=COLORS['RED'], duration=2.0):
        self.message_label = Label((SCREEN_WIDTH//2, 100), text, self.assets.fonts.get('medium'), color)
        self.message_timer = duration

    def complete(self, success: bool):
        self.on_complete(success)


# ---------- РЕАЛИЗАЦИИ МИНИ-ИГР ПО СЦЕНАРИЮ ----------
# 1. ЧИТАЛЬНЫЙ ЗАЛ
class SortBooksMinigame(BaseMinigame):
    """Перетаскивание книг 3,1,2 в правильном порядке"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.slots = [None, None, None]  # позиции слева направо
        self.books = []  # список Draggable
        # Книги с цифрами
        book_images = {}
        for num in [1,2,3]:
            surf = pygame.Surface((80,100))
            surf.fill(COLORS['ORANGE'])
            text = assets.fonts.get('medium').render(str(num), True, COLORS['BLACK'])
            surf.blit(text, text.get_rect(center=(40,50)))
            book_images[num] = surf
        # Перемешанные книги: 3,1,2
        positions = [(300,400), (450,400), (600,400)]
        for i, num in enumerate([3,1,2]):
            rect = pygame.Rect(positions[i][0], positions[i][1], 80, 100)
            draggable = Draggable(rect, book_images[num], num)
            self.books.append(draggable)
        self.ui_elements = self.books
        # Проверочная кнопка
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 600, 120, 50), "Проверить",
                                assets.fonts.get('small'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements.append(self.check_btn)

    def check(self):
        # Проверяем, что в слотах лежат книги 1,2,3 по порядку
        correct = [1,2,3]
        if self.slots == correct:
            self.complete(True)
        else:
            self.show_message("Порядок должен быть 1, 2, 3! Попробуй ещё раз.")

    def handle_event(self, event):
        super().handle_event(event)
        # Обработка отпускания книг над слотами
        if event.type == pygame.MOUSEBUTTONUP:
            for i, book in enumerate(self.books):
                if book.dragging:
                    book.dragging = False
                    # Проверить попадание в слоты
                    slot_rects = [
                        pygame.Rect(200, 250, 100, 120),
                        pygame.Rect(350, 250, 100, 120),
                        pygame.Rect(500, 250, 100, 120)
                    ]
                    placed = False
                    for idx, slot_rect in enumerate(slot_rects):
                        if book.rect.colliderect(slot_rect):
                            # Положить книгу в слот
                            book.rect.center = slot_rect.center
                            self.slots[idx] = book.data
                            placed = True
                            break
                    if not placed:
                        # Вернуть в исходное положение (сохраним исходные координаты)
                        # Упрощённо: не перемещаем обратно, просто оставляем где отпустили
                        # Но для удобства вернём на место
                        orig_positions = [(300,400), (450,400), (600,400)]
                        for j, b in enumerate(self.books):
                            if b == book:
                                book.rect.topleft = orig_positions[j]
                                break
                    # Обновим слоты: очистим те, где книги больше нет
                    for idx, slot_val in enumerate(self.slots):
                        if slot_val == book.data and not any(b.data == slot_val and b.rect.colliderect(slot_rects[idx]) for b in self.books):
                            self.slots[idx] = None
                    break

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        # Нарисовать полку и слоты
        for i, pos in enumerate([(200,250), (350,250), (500,250)]):
            rect = pygame.Rect(pos[0], pos[1], 100, 120)
            pygame.draw.rect(surface, COLORS['BROWN'], rect, 3)
            if self.slots[i] is not None:
                num = self.slots[i]
                surf = pygame.Surface((80,100))
                surf.fill(COLORS['ORANGE'])
                text = self.assets.fonts.get('medium').render(str(num), True, COLORS['BLACK'])
                surf.blit(text, text.get_rect(center=(40,50)))
                surface.blit(surf, rect)
        # Нарисовать книги
        for book in self.books:
            book.draw(surface)
        # Текст задания
        q_text = self.assets.fonts.get('medium').render("Расставь книги по порядку: 1, 2, 3", True, COLORS['GOLD'])
        surface.blit(q_text, (SCREEN_WIDTH//2 - q_text.get_width()//2, 50))
        self.check_btn.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)


class LogicRowMinigame(BaseMinigame):
    """Логический ряд: красная, синяя, красная, ?"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.options = ["🔴 КНИГА", "🔵 КНИГА", "🟢 ТЕТРАДЬ"]
        self.correct_index = 1
        self.buttons = []
        for i, opt in enumerate(self.options):
            btn = Button(pygame.Rect(300, 300 + i*80, 400, 60), opt,
                         assets.fonts.get('medium'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if idx == self.correct_index:
            self.complete(True)
        else:
            self.show_message("Посмотри внимательно: цвета чередуются. Красный, синий, красный... какой следующий?")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.assets.fonts.get('medium').render("Какой предмет следующий?", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        # Показать ряд
        items = ["🔴 КНИГА", "🔵 КНИГА", "🔴 КНИГА", "?"]
        x_start = 150
        for i, it in enumerate(items):
            txt = self.assets.fonts.get('small').render(it, True, COLORS['WHITE'])
            surface.blit(txt, (x_start + i*150, 200))
        super().draw(surface)


# 2. ДЕТСКИЙ АБОНЕМЕНТ
class NumberCompositionMinigame(BaseMinigame):
    """Состав числа 7 - выбрать пару картинок, дающих в сумме 7"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.pairs = [
            ("3 яблока + 4 яблока", 7, True),
            ("5 звёзд + 2 звезды", 7, True),
            ("6 мячей + 1 мяч", 7, True),
            ("2 яблока + 3 яблока", 5, False),
            ("4 звезды + 4 звезды", 8, False)
        ]
        self.buttons = []
        for i, (text, total, correct) in enumerate(self.pairs):
            color = COLORS['LIGHT_BLUE']
            btn = Button(pygame.Rect(200, 200 + i*70, 600, 50), text,
                         assets.fonts.get('small'), color, COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if self.pairs[idx][2]:
            self.complete(True)
        else:
            self.show_message("Семь — это три и четыре. Или пять и два. Попробуй ещё!")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.assets.fonts.get('medium').render("Выбери пару, которая в сумме даёт 7", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        big7 = self.assets.fonts.get('large').render("7", True, COLORS['YELLOW'])
        surface.blit(big7, (SCREEN_WIDTH//2 - big7.get_width()//2, 120))
        super().draw(surface)


class MemoryLettersMinigame(BaseMinigame):
    """Найди пару букв: карточки А,А,Б,В"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.cards = [('А', False), ('А', False), ('Б', False), ('В', False)]
        random.shuffle(self.cards)
        self.selected = None
        self.waiting = False
        self.wait_timer = 0
        self.buttons = []
        for i in range(4):
            rect = pygame.Rect(200 + (i%2)*300, 300 + (i//2)*200, 150, 150)
            btn = Button(rect, "", assets.fonts.get('large'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.reveal(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def reveal(self, idx):
        if self.waiting or self.cards[idx][1]:
            return
        # Переворачиваем карточку
        self.cards[idx] = (self.cards[idx][0], True)
        if self.selected is None:
            self.selected = idx
        else:
            # проверяем пару
            if self.cards[self.selected][0] == self.cards[idx][0]:
                # успех
                self.cards[self.selected] = (self.cards[self.selected][0], True)
                self.cards[idx] = (self.cards[idx][0], True)
                self.selected = None
                # проверить, все ли открыты
                if all(flipped for _, flipped in self.cards):
                    self.complete(True)
            else:
                # не совпали, ждём и закрываем
                self.waiting = True
                self.wait_timer = 1.0
                self.pending_idx = idx

    def update(self, dt):
        super().update(dt)
        if self.waiting:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                # закрыть обе карточки
                self.cards[self.selected] = (self.cards[self.selected][0], False)
                self.cards[self.pending_idx] = (self.cards[self.pending_idx][0], False)
                self.selected = None
                self.waiting = False

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.assets.fonts.get('medium').render("Найди пару одинаковых букв", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, btn in enumerate(self.buttons):
            if self.cards[i][1]:
                # показать букву
                letter = self.cards[i][0]
                text_surf = self.assets.fonts.get('large').render(letter, True, COLORS['BLACK'])
                btn.color = COLORS['WHITE']
                btn.draw(surface)
                surface.blit(text_surf, text_surf.get_rect(center=btn.rect.center))
            else:
                btn.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)


# 3. КНИГОХРАНИЛИЩЕ
class ClockMinigame(BaseMinigame):
    """Часы: перетащить часовую стрелку на 6"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.hour = 3
        self.dragging = False
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 600, 120, 50), "Проверить",
                                assets.fonts.get('small'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = [self.check_btn]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверить, попали ли в стрелку
            center = (SCREEN_WIDTH//2, 300)
            angle = 360 - (self.hour % 12) * 30
            rad = math.radians(angle)
            end = (center[0] + 80 * math.cos(rad), center[1] - 80 * math.sin(rad))
            # Простая проверка попадания в линию
            if pygame.Rect(end[0]-10, end[1]-10, 20, 20).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Вычислить новый час по углу
            center = (SCREEN_WIDTH//2, 300)
            dx = event.pos[0] - center[0]
            dy = event.pos[1] - center[1]
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
            self.complete(True)
        else:
            self.show_message("Нужно поставить стрелку на 6 часов. Маленькая стрелка внизу, большая наверху.")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        # Рисуем часы
        center = (SCREEN_WIDTH//2, 300)
        pygame.draw.circle(surface, COLORS['WHITE'], center, 150, 5)
        # Рисуем деления
        for i in range(1, 13):
            angle = math.radians(90 - i*30)
            x1 = center[0] + 130 * math.cos(angle)
            y1 = center[1] - 130 * math.sin(angle)
            x2 = center[0] + 145 * math.cos(angle)
            y2 = center[1] - 145 * math.sin(angle)
            pygame.draw.line(surface, COLORS['BLACK'], (x1,y1), (x2,y2), 3)
            num = self.assets.fonts.get('small').render(str(i), True, COLORS['BLACK'])
            x_text = center[0] + 115 * math.cos(angle) - num.get_width()//2
            y_text = center[1] - 115 * math.sin(angle) - num.get_height()//2
            surface.blit(num, (x_text, y_text))
        # Часовая стрелка
        angle = math.radians(90 - self.hour*30)
        end = (center[0] + 80 * math.cos(angle), center[1] - 80 * math.sin(angle))
        pygame.draw.line(surface, COLORS['BLACK'], center, end, 8)
        # Минутная стрелка (всегда на 12)
        end_min = (center[0], center[1] - 110)
        pygame.draw.line(surface, COLORS['BLACK'], center, end_min, 4)
        self.check_btn.draw(surface)
        title = self.assets.fonts.get('medium').render("Поставь время 6 часов", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        if self.message_label:
            self.message_label.draw(surface)


class MazeMinigame(BaseMinigame):
    """Лабиринт 4x4, передвинуть стеллаж к выходу"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.grid = [[0]*4 for _ in range(4)]  # 0 - пусто, 1 - стена
        # Стены (простой лабиринт)
        # Определим стены между клетками (список препятствий)
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
        self.pos = (0,0)
        self.target = (3,3)
        self.buttons = []
        btn_up = Button(pygame.Rect(SCREEN_WIDTH//2-30, 500, 60, 50), "↑", assets.fonts.get('large'), COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(0,-1))
        btn_down = Button(pygame.Rect(SCREEN_WIDTH//2-30, 600, 60, 50), "↓", assets.fonts.get('large'), COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(0,1))
        btn_left = Button(pygame.Rect(SCREEN_WIDTH//2-90, 550, 60, 50), "←", assets.fonts.get('large'), COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(-1,0))
        btn_right = Button(pygame.Rect(SCREEN_WIDTH//2+30, 550, 60, 50), "→", assets.fonts.get('large'), COLORS['LIGHT_BLUE'], COLORS['GREEN'], callback=lambda: self.move(1,0))
        self.buttons = [btn_up, btn_down, btn_left, btn_right]
        self.ui_elements = self.buttons

    def move(self, dx, dy):
        nx, ny = self.pos[0]+dx, self.pos[1]+dy
        if nx < 0 or nx >= 4 or ny < 0 or ny >= 4:
            self.show_message("Там стена!")
            return
        # Проверка стены между текущей и соседней клеткой
        if dx == 1 and self.walls[self.pos].get('right', False):
            self.show_message("Там стена!")
            return
        if dx == -1 and self.walls[(nx, ny)].get('right', False):
            self.show_message("Там стена!")
            return
        if dy == 1 and self.walls[self.pos].get('down', False):
            self.show_message("Там стена!")
            return
        if dy == -1 and self.walls[(nx, ny)].get('down', False):
            self.show_message("Там стена!")
            return
        self.pos = (nx, ny)
        if self.pos == self.target:
            self.complete(True)

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
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
                # Рисуем стены
                if self.walls[(x,y)].get('right', False):
                    pygame.draw.line(surface, COLORS['RED'], (rect.right, rect.top), (rect.right, rect.bottom), 3)
                if self.walls[(x,y)].get('down', False):
                    pygame.draw.line(surface, COLORS['RED'], (rect.left, rect.bottom), (rect.right, rect.bottom), 3)
        title = self.assets.fonts.get('medium').render("Проведи стеллаж к выходу (золотая клетка)", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for btn in self.buttons:
            btn.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)


# 4. КАБИНЕТ БИБЛИОТЕКАРЯ
class PuzzleMinigame(BaseMinigame):
    """Пазл следа лапы из 4 частей"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        # Создаём изображение пазла (заглушка)
        full_image = pygame.Surface((200,200))
        full_image.fill(COLORS['GRAY'])
        # Рисуем след лапы
        pygame.draw.circle(full_image, COLORS['BLACK'], (100,100), 40)
        pygame.draw.circle(full_image, COLORS['BLACK'], (70,70), 15)
        pygame.draw.circle(full_image, COLORS['BLACK'], (130,70), 15)
        pygame.draw.circle(full_image, COLORS['BLACK'], (70,130), 15)
        pygame.draw.circle(full_image, COLORS['BLACK'], (130,130), 15)
        # Разрезаем на 4 части
        self.pieces = []
        for i in range(2):
            for j in range(2):
                rect = pygame.Rect(i*100, j*100, 100, 100)
                piece = full_image.subsurface(rect).copy()
                self.pieces.append(piece)
        random.shuffle(self.pieces)
        self.slots = [None]*4
        self.draggables = []
        for idx, piece in enumerate(self.pieces):
            rect = pygame.Rect(600 + (idx%2)*100, 300 + (idx//2)*100, 100, 100)
            d = Draggable(rect, piece, idx)
            self.draggables.append(d)
        self.ui_elements = self.draggables
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 600, 120, 50), "Проверить",
                                assets.fonts.get('small'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements.append(self.check_btn)

    def check(self):
        if all(s is not None for s in self.slots) and len(set(self.slots))==4:
            self.complete(True)
        else:
            self.show_message("Собери все части в рамку!")

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONUP:
            for d in self.draggables:
                if d.dragging:
                    d.dragging = False
                    # Попадание в слоты
                    slot_rects = [pygame.Rect(200, 250, 100, 100), pygame.Rect(320, 250, 100, 100),
                                   pygame.Rect(200, 370, 100, 100), pygame.Rect(320, 370, 100, 100)]
                    placed = False
                    for idx, slot in enumerate(slot_rects):
                        if d.rect.colliderect(slot):
                            d.rect.center = slot.center
                            self.slots[idx] = d.data
                            placed = True
                            break
                    if not placed:
                        # вернуть в исходное
                        orig = [(600,300), (700,300), (600,400), (700,400)]
                        for i, dd in enumerate(self.draggables):
                            if dd == d:
                                d.rect.topleft = orig[i]
                                break
                    # очистить слоты, где больше нет части
                    for idx, val in enumerate(self.slots):
                        if val is not None and not any(d.data == val and d.rect.colliderect(slot_rects[idx]) for d in self.draggables):
                            self.slots[idx] = None
                    break

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        # Рамка для сборки
        for i, rect in enumerate([(200,250), (320,250), (200,370), (320,370)]):
            pygame.draw.rect(surface, COLORS['WHITE'], (*rect,100,100), 3)
            if self.slots[i] is not None:
                # отобразить часть
                piece = self.pieces[self.slots[i]]
                surface.blit(piece, rect)
        for d in self.draggables:
            d.draw(surface)
        title = self.assets.fonts.get('medium').render("Собери след лапы", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.check_btn.draw(surface)


class CauseEffectMinigame(BaseMinigame):
    """Причина-следствие: выбрать лужу"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.options = ["Лужа на полу", "Горящая лампа", "Закрытая книга"]
        self.correct = 0
        self.buttons = []
        for i, opt in enumerate(self.options):
            btn = Button(pygame.Rect(300, 300 + i*80, 400, 60), opt,
                         assets.fonts.get('medium'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.check(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def check(self, idx):
        if idx == self.correct:
            self.complete(True)
        else:
            self.show_message("Если окно открыто и идёт дождь — что случится с полом?")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.assets.fonts.get('medium').render("Выбери правильное следствие", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        # Изображение причины: открытое окно, дождь
        cause_text = self.assets.fonts.get('small').render("Открытое окно идёт дождь", True, COLORS['WHITE'])
        surface.blit(cause_text, (SCREEN_WIDTH//2 - cause_text.get_width()//2, 150))
        super().draw(surface)


# 5. ПОДВАЛ
class RebusMinigame(BaseMinigame):
    """Ребус: картинки -> буквы, слово КРОНА"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.pictures = [("🧢", "К"), ("🐟", "Р"), ("🦢", "О"), ("🐓", "Н"), ("🍉", "А")]
        self.user_letters = ["", "", "", "", ""]
        self.current_slot = 0
        self.keyboard_buttons = []
        letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        x_start = 200
        for i, ch in enumerate(letters):
            btn = Button(pygame.Rect(x_start + (i%10)*60, 500 + (i//10)*60, 50, 50), ch,
                         assets.fonts.get('small'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda c=ch: self.add_letter(c))
            self.keyboard_buttons.append(btn)
        self.check_btn = Button(pygame.Rect(SCREEN_WIDTH//2-60, 650, 120, 50), "Проверить",
                                assets.fonts.get('small'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                callback=self.check)
        self.ui_elements = self.keyboard_buttons + [self.check_btn]

    def add_letter(self, ch):
        if self.current_slot < 5:
            self.user_letters[self.current_slot] = ch
            self.current_slot += 1

    def check(self):
        word = "".join(self.user_letters)
        if word == "КРОНА":
            self.complete(True)
        else:
            self.show_message("Первая буква — как в слове 'кепка'. Вторая — как в 'рыба'... Попробуй ещё!")

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.unicode.isalpha():
            self.add_letter(event.unicode.upper())

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        for i, (pic, correct) in enumerate(self.pictures):
            x = 150 + i*130
            # Картинка
            pic_surf = self.assets.fonts.get('large').render(pic, True, COLORS['WHITE'])
            surface.blit(pic_surf, (x, 150))
            # Слот для буквы
            rect = pygame.Rect(x+20, 250, 60, 60)
            pygame.draw.rect(surface, COLORS['WHITE'], rect)
            pygame.draw.rect(surface, COLORS['BLACK'], rect, 2)
            if self.user_letters[i]:
                letter_surf = self.assets.fonts.get('large').render(self.user_letters[i], True, COLORS['BLACK'])
                surface.blit(letter_surf, letter_surf.get_rect(center=rect.center))
        title = self.assets.fonts.get('medium').render("Напиши слово по картинкам", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for btn in self.keyboard_buttons:
            btn.draw(surface)
        self.check_btn.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)


class EvenNumbersMinigame(BaseMinigame):
    """Нажми на все чётные числа от 1 до 20"""
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.clicked = [False]*21
        self.buttons = []
        for i in range(1, 21):
            x = 100 + ((i-1)%5)*120
            y = 200 + ((i-1)//5)*80
            btn = Button(pygame.Rect(x, y, 80, 60), str(i),
                         assets.fonts.get('medium'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda n=i: self.click_number(n))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def click_number(self, n):
        if n % 2 == 0 and not self.clicked[n]:
            self.clicked[n] = True
            if all(self.clicked[i] for i in range(2,21,2)):
                self.complete(True)
        elif n % 2 != 0:
            self.show_message("Чётные — те, что делятся на два. Два, четыре, шесть... А это нечётное!")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.assets.fonts.get('medium').render("Нажми на все чётные числа от 1 до 20", True, COLORS['GOLD'])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, btn in enumerate(self.buttons):
            if self.clicked[i+1]:
                btn.color = COLORS['GREEN']
            btn.draw(surface)
        if self.message_label:
            self.message_label.draw(surface)


# 6. ЧЕРДАК (финал) - викторина
class FinalQuizMinigame(BaseMinigame):
    def __init__(self, task_data, assets, on_complete):
        super().__init__(task_data, assets, on_complete)
        self.questions = [
            ("Кто оставил чернильные следы?", ["Библиотекарь", "Ворона", "Собака"], 1),
            ("Почему ворона залетела в библиотеку?", ["Хотела украсть книги", "Окно было разбито", "Ей было скучно"], 1),
            ("Что нужно сделать, чтобы ворона больше не залетала?", ["Поймать её", "Поставить сетку на окно и повесить скворечник", "Закрыть библиотеку"], 1)
        ]
        self.current_q = 0
        self.buttons = []
        self.next_btn = None
        self.setup_question()

    def setup_question(self):
        self.buttons = []
        q_text, options, _ = self.questions[self.current_q]
        # Показываем вопрос и варианты
        for i, opt in enumerate(options):
            btn = Button(pygame.Rect(300, 300 + i*80, 400, 60), opt,
                         self.assets.fonts.get('medium'), COLORS['LIGHT_BLUE'], COLORS['GREEN'],
                         callback=lambda i=i: self.answer(i))
            self.buttons.append(btn)
        self.ui_elements = self.buttons

    def answer(self, idx):
        _, _, correct = self.questions[self.current_q]
        if idx == correct:
            self.current_q += 1
            if self.current_q >= len(self.questions):
                self.complete(True)
            else:
                self.setup_question()
        else:
            self.show_message("Подумай, как решить проблему, чтобы всем было хорошо — и птице, и книгам.")

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        if self.current_q < len(self.questions):
            q_text, _, _ = self.questions[self.current_q]
            q_surf = self.assets.fonts.get('medium').render(q_text, True, COLORS['GOLD'])
            surface.blit(q_surf, (SCREEN_WIDTH//2 - q_surf.get_width()//2, 150))
        super().draw(surface)


# ---------- ЭКРАНЫ ----------
class Screen:
    def __init__(self, game: 'LibraryGame'):
        self.game = game

    def handle_event(self, event: pygame.event.Event): pass
    def update(self, dt: float): pass
    def draw(self, surface: pygame.Surface): pass


class LoadingScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.timer = 2.0

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.game.set_state('PROLOG')

    def draw(self, surface):
        surface.fill(COLORS['DARK_BLUE'])
        title = self.game.assets.fonts.get('title').render("Дело о Призраке Библиотеки", True, COLORS['GOLD'])
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
        load = self.game.assets.fonts.get('small').render("Загрузка...", True, COLORS['WHITE'])
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
        self.font = game.assets.fonts.get('small')
        self.next_btn = Button(pygame.Rect(SCREEN_WIDTH-150, SCREEN_HEIGHT-70, 100, 40), "Далее",
                               self.font, COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                               callback=self.next_step)
        self.start_btn = None

    def next_step(self):
        self.step += 1
        if self.step >= len(self.dialogs):
            # Показать кнопку "Начать расследование"
            self.start_btn = Button(pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT-100, 240, 60), "Начать расследование",
                                    self.game.assets.fonts.get('medium'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                    callback=lambda: self.game.set_state('MAP'))
            self.next_btn.enabled = False

    def handle_event(self, event):
        self.next_btn.handle_event(event)
        if self.start_btn:
            self.start_btn.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.images.get('prolog_bg.png')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['DARK_BLUE'])
        if self.step < len(self.dialogs):
            speaker, text = self.dialogs[self.step]
            bubble = DialogBubble(pygame.Rect(100, SCREEN_HEIGHT-180, SCREEN_WIDTH-200, 120), text, speaker, self.font)
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
                               game.assets.fonts.get('small'), COLORS['RED'], COLORS['ORANGE'],
                               callback=self.game.exit_game)

    def update_buttons(self):
        self.buttons = []
        for num, name, x, y, letter in self.locations:
            available = (num == 1) or (num-1 in self.game.completed_locations)
            completed = num in self.game.completed_locations
            color = COLORS['GREEN'] if completed else (COLORS['LIGHT_BLUE'] if available else COLORS['GRAY'])
            btn = Button(pygame.Rect(x, y, 180, 100), name, self.game.assets.fonts.get('small'),
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
        bg = self.game.assets.images.get('map_bg.jpg')
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['BROWN'])
        title = self.game.assets.fonts.get('title').render("Карта библиотеки", True, COLORS['GOLD'])
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 50)))
        letters_str = ' '.join(list(self.game.collected_letters.ljust(6, '_')))
        lett_surf = self.game.assets.fonts.get('medium').render(f"Буквы: {letters_str}", True, COLORS['WHITE'])
        surface.blit(lett_surf, (150, 110))
        score_surf = self.game.assets.fonts.get('medium').render(f"Очки: {self.game.score}", True, COLORS['GOLD'])
        surface.blit(score_surf, (SCREEN_WIDTH-100, 110))
        for btn in self.buttons:
            btn.draw(surface)
        self.home_btn.draw(surface)


class LocationScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.tasks = []  # список заданий в этой локации
        self.task_buttons = []
        self.loc = None
        self.completed_tasks = []  # id выполненных заданий (внутренние)
        self.back_btn = Button(pygame.Rect(50, SCREEN_HEIGHT-60, 120, 40), "На карту",
                               game.assets.fonts.get('small'), COLORS['GRAY'], COLORS['LIGHT_BLUE'],
                               callback=self.exit_location)

    def on_enter(self):
        self.loc = self.game.db.get_location(self.game.quest_id, self.game.current_location_num)
        if not self.loc:
            self.game.set_state('MAP')
            return
        # Определяем задания для локации
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
                {'id': 'puzzle', 'name': 'Пазл записи', 'minigame_class': PuzzleMinigame},
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
        # Загружаем сохранённые выполненные задания
        self.completed_tasks = self.game.location_tasks_completed.get(self.game.current_location_num, [])
        self.update_task_buttons()
        self.dialog_bubble = DialogBubble(pygame.Rect(50, SCREEN_HEIGHT-160, SCREEN_WIDTH-100, 100),
                                          self.loc['npc_dialogue'], self.loc['npc_name'],
                                          self.game.assets.fonts.get('small'))

    def update_task_buttons(self):
        self.task_buttons = []
        for t in self.tasks:
            completed = t['id'] in self.completed_tasks
            color = COLORS['GREEN'] if completed else COLORS['LIGHT_BLUE']
            btn = Button(pygame.Rect(200, 180 + len(self.task_buttons)*70, 600, 50),
                         f"Задание: {t['name']}",
                         self.game.assets.fonts.get('small'), color, COLORS['LIGHT_GREEN'] if not completed else color,
                         callback=lambda task=t: self.start_task(task) if not completed else None)
            btn.enabled = not completed
            self.task_buttons.append(btn)

    def start_task(self, task):
        self.game.set_state('TASK', task=task, location_num=self.game.current_location_num)

    def exit_location(self):
        # Проверяем, все ли задания выполнены, чтобы выдать букву
        all_completed = all(t['id'] in self.completed_tasks for t in self.tasks)
        if all_completed and self.game.current_location_num not in self.game.completed_locations:
            # Выдаём букву
            letter = self.loc['letter']
            if letter not in self.game.collected_letters:
                self.game.collected_letters += letter
            self.game.completed_locations.append(self.game.current_location_num)
            self.game.save_progress()
        self.game.set_state('MAP')

    def handle_event(self, event):
        for btn in self.task_buttons:
            btn.handle_event(event)
        self.back_btn.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.images.get(self.loc['background']) if self.loc else None
        if bg:
            surface.blit(bg, (0,0))
        else:
            surface.fill(COLORS['DARK_BLUE'])
        if self.loc:
            name_surf = self.game.assets.fonts.get('title').render(self.loc['name'], True, COLORS['GOLD'])
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
        self.minigame = task['minigame_class'](task, game.assets, self._on_task_complete)
        self.back_btn = Button(pygame.Rect(50, SCREEN_HEIGHT-60, 100, 40), "Назад",
                               game.assets.fonts.get('small'), COLORS['GRAY'], COLORS['LIGHT_BLUE'],
                               callback=lambda: game.set_state('LOCATION'))

    def _on_task_complete(self, success):
        if success:
            self.game.score += 10  # очки за задание
            # Сохраняем выполненное задание для текущей локации
            if self.location_num not in self.game.location_tasks_completed:
                self.game.location_tasks_completed[self.location_num] = []
            if self.task['id'] not in self.game.location_tasks_completed[self.location_num]:
                self.game.location_tasks_completed[self.location_num].append(self.task['id'])
            self.game.save_progress()
            self.game.set_state('LOCATION')
        else:
            # Можно показать сообщение, но остаться в мини-игре
            self.minigame.show_message("Попробуй ещё раз!", COLORS['RED'])

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.minigame.handle_event(event)

    def update(self, dt):
        self.minigame.update(dt)

    def draw(self, surface):
        self.minigame.draw(surface)
        self.back_btn.draw(surface)


class WinScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = game.assets.fonts.get('title')
        self.font_large = game.assets.fonts.get('large')
        self.btn_reward = Button(pygame.Rect(SCREEN_WIDTH//2-200, 500, 180, 60), "Забрать награду",
                                 game.assets.fonts.get('medium'), COLORS['GREEN'], COLORS['LIGHT_GREEN'],
                                 callback=self.game.finish_game)
        self.btn_replay = Button(pygame.Rect(SCREEN_WIDTH//2+20, 500, 180, 60), "Играть ещё раз",
                                 game.assets.fonts.get('medium'), COLORS['BLUE'], COLORS['LIGHT_BLUE'],
                                 callback=self.game.reset_game)

    def handle_event(self, event):
        self.btn_reward.handle_event(event)
        self.btn_replay.handle_event(event)

    def draw(self, surface):
        bg = self.game.assets.images.get('win_bg.jpg')
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

        self.db = Database(db_config)
        self.db.connect()
        self.quest_id = 1

        self.assets = AssetCache()
        self._load_fonts()
        self._load_images()
        self._load_sounds()

        # Прогресс
        progress = self.db.get_child_progress(self.child_id, self.quest_id)
        self.completed_locations = progress['completed_locations']
        self.collected_letters = progress['collected_letters']
        self.current_location_num = progress['current_location']
        self.score = progress['score']
        self.stars = progress['stars_earned']
        self.location_tasks_completed = {}  # локально, можно сохранять в БД при желании

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

    def _load_fonts(self):
        self.assets.fonts['title'] = self.assets.load_font("Chewy-Regular.ttf", 64)
        self.assets.fonts['large'] = self.assets.load_font("ComicNeue-Bold.ttf", 48)
        self.assets.fonts['medium'] = self.assets.load_font("ComicNeue-Bold.ttf", 36)
        self.assets.fonts['small'] = self.assets.load_font("ComicNeue-Regular.ttf", 24)

    def _load_images(self):
        bg_names = ['prolog_bg.png', 'map_bg.png', 'reading_hall.png', 'kids_section.png',
                    'book_storage.png', 'office.png', 'basement.png', 'attic.png', 'win_bg.png']
        for name in bg_names:
            self.assets.load_image(name, f"backgrounds/{name}", (SCREEN_WIDTH, SCREEN_HEIGHT))

    def _load_sounds(self):
        self.assets.load_sound('bg_music', "music/background_music.mp3")
        if 'bg_music' in self.assets.sounds:
            try:
                pygame.mixer.music.load(os.path.join(SOUNDS_PATH, "music/background_music.mp3"))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except:
                pass

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

    def save_progress(self):
        progress = {
            'completed_locations': self.completed_locations,
            'collected_letters': self.collected_letters,
            'current_location': self.current_location_num,
            'score': self.score,
            'stars_earned': self.stars,
            'is_completed': (self.state_name == 'WIN'),
        }
        self.db.save_progress(self.child_id, self.quest_id, progress)

    def exit_game(self):
        self.save_progress()
        self.running = False
        self.db.close()
        self.on_exit()

    def finish_game(self):
        self.stars = 1
        self.save_progress()
        self.db.add_achievement(self.child_id, "Детектив библиотеки")
        self.running = False
        self.db.close()
        self.on_finish()

    def reset_game(self):
        self.completed_locations = []
        self.collected_letters = ""
        self.current_location_num = 1
        self.score = 0
        self.stars = 0
        self.location_tasks_completed = {}
        self.save_progress()
        self.set_state('PROLOG')


# ---------- ФУНКЦИЯ ДЛЯ ИНТЕГРАЦИИ ----------
def create_library_game(surface: pygame.Surface, db_config: Dict, child_id: int, username: str,
                        on_exit: Callable = None, on_finish: Callable = None) -> LibraryGame:
    return LibraryGame(surface, db_config, child_id, username, on_exit, on_finish)