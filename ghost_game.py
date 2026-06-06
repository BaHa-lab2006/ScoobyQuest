"""
Игра 2: Тайна Призрака в Консервном Замке
Полная переработанная версия с неблокирующими сценами, кешированием ресурсов,
использованием жизней, адаптивным UI и конфигурацией БД из файла.
"""

import pygame
import sys
import os
import random
import json
import pyodbc
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from configparser import ConfigParser

# ----------------------------------------------------------------------
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ----------------------------------------------------------------------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Цвета
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GREEN': (100, 200, 100),
    'RED': (200, 100, 100),
    'BLUE': (100, 150, 255),
    'YELLOW': (255, 255, 150),
    'BROWN': (139, 69, 19),
    'GRAY': (128, 128, 128),
    'GOLD': (255, 215, 0),
    'DARK_BROWN': (101, 67, 33),
    'ORANGE': (255, 165, 0),
    'PURPLE': (147, 112, 219)
}

# Пути к ассетам
ASSETS_BASE = "assets/game2/"
IMAGES_PATH = os.path.join(ASSETS_BASE, "images/")
SOUNDS_PATH = os.path.join(ASSETS_BASE, "sounds/")
VOICES_PATH = os.path.join(ASSETS_BASE, "voices/")

BG_PATH = os.path.join(IMAGES_PATH, "backgrounds/")
CHAR_PATH = os.path.join(IMAGES_PATH, "characters/")
ITEMS_PATH = os.path.join(IMAGES_PATH, "items/")
UI_PATH = os.path.join(IMAGES_PATH, "ui/")
MINIGAMES_PATH = os.path.join(IMAGES_PATH, "minigames/")
MUSIC_PATH = os.path.join(SOUNDS_PATH, "music/")
SFX_PATH = os.path.join(SOUNDS_PATH, "sfx/")

# Размеры UI
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 70
PORTRAIT_SIZE = 180
DIALOG_WIDTH = SCREEN_WIDTH - 100
DIALOG_HEIGHT = 180
DEFAULT_LIVES = 3
MAX_STARS = 6

# ----------------------------------------------------------------------
# МЕНЕДЖЕР РЕСУРСОВ (кеширование)
# ----------------------------------------------------------------------
class AssetManager:
    """Загружает и кеширует все ресурсы, чтобы не делать это многократно."""
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {
            'name': pygame.font.Font(None, 32),
            'text': pygame.font.Font(None, 28),
            'button': pygame.font.Font(None, 36),
            'big': pygame.font.Font(None, 48),
            'huge': pygame.font.Font(None, 72),
            'small': pygame.font.Font(None, 24)
        }

    def load_image(self, path: str, scale: Optional[tuple] = None, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        if path not in self.images:
            try:
                img = pygame.image.load(path)
                if convert_alpha:
                    img = img.convert_alpha()
                else:
                    img = img.convert()
                if scale:
                    img = pygame.transform.scale(img, scale)
                self.images[path] = img
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                self.images[path] = None
        return self.images[path]

    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        if path not in self.sounds:
            try:
                self.sounds[path] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Error loading sound {path}: {e}")
                self.sounds[path] = None
        return self.sounds[path]

    def get_font(self, name: str) -> pygame.font.Font:
        return self.fonts.get(name, self.fonts['text'])

# ----------------------------------------------------------------------
# МЕНЕДЖЕР БАЗЫ ДАННЫХ (с улучшенной обработкой)
# ----------------------------------------------------------------------
class DatabaseManager:
    """Подключение к SQL Server с конфигурацией из файла."""
    def __init__(self, config_file: str = 'config.ini'):
        self.connection = None
        self.cursor = None
        self.connection_string = self._load_connection_string(config_file)

    def _load_connection_string(self, config_file: str) -> str:
        parser = ConfigParser()
        parser.read(config_file)
        if parser.has_section('database'):
            driver = parser.get('database', 'driver', fallback='{ODBC Driver 17 for SQL Server}')
            server = parser.get('database', 'server', fallback='localhost')
            database = parser.get('database', 'database', fallback='KindergartenDB')
            trusted = parser.getboolean('database', 'trusted_connection', fallback=True)
            if trusted:
                return f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes"
            else:
                user = parser.get('database', 'user')
                password = parser.get('database', 'password')
                return f"DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}"
        # Fallback
        return "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=KindergartenDB;Trusted_Connection=yes"

    def connect(self) -> bool:
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"DB connection error: {e}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_location_by_number(self, quest_id: int, loc_num: int) -> Optional[Dict[str, Any]]:
        query = """SELECT id, location_number, location_name, background_image, character_name,
                          character_portrait, dialogue_text, voice_file
                   FROM Locations WHERE quest_id=? AND location_number=?"""
        self.cursor.execute(query, (quest_id, loc_num))
        row = self.cursor.fetchone()
        if row:
            return {
                'id': row[0], 'number': row[1], 'name': row[2],
                'background_image': row[3], 'character_name': row[4],
                'character_portrait': row[5], 'dialogue_text': row[6],
                'voice_file': row[7]
            }
        return None

    def get_all_locations(self, quest_id: int) -> List[Dict[str, Any]]:
        query = """SELECT location_number, location_name
                   FROM Locations WHERE quest_id=? ORDER BY location_number"""
        self.cursor.execute(query, (quest_id,))
        return [{'number': row[0], 'name': row[1]} for row in self.cursor.fetchall()]

    def get_tasks_for_location(self, location_id: int) -> List[Dict[str, Any]]:
        query = """SELECT id, task_number, task_type, question_text, correct_answer,
                          hint_voice, lives_allowed
                   FROM Tasks WHERE location_id=? ORDER BY task_number"""
        self.cursor.execute(query, (location_id,))
        tasks = []
        for row in self.cursor.fetchall():
            tasks.append({
                'id': row[0], 'task_number': row[1], 'task_type': row[2],
                'question_text': row[3], 'correct_answer': row[4],
                'hint_voice': row[5], 'lives_allowed': row[6]
            })
        return tasks

    def get_clues_for_location(self, location_id: int) -> List[Dict[str, Any]]:
        query = "SELECT id, clue_name, clue_image FROM Clues WHERE location_id=?"
        self.cursor.execute(query, (location_id,))
        return [{'id': row[0], 'name': row[1], 'image': row[2]} for row in self.cursor.fetchall()]

    def get_or_create_progress(self, user_id: int, quest_id: int) -> Dict[str, Any]:
        query = """SELECT id, current_location, current_task, lives_remaining, stars_earned
                   FROM PlayerProgress WHERE user_id=? AND quest_id=? AND is_completed=0"""
        self.cursor.execute(query, (user_id, quest_id))
        row = self.cursor.fetchone()
        if row:
            progress_id = row[0]
            clues = self.get_player_clues(progress_id)
            return {
                'id': progress_id, 'current_location': row[1], 'current_task': row[2],
                'lives': row[3], 'stars': row[4], 'clues': clues
            }
        else:
            insert = """INSERT INTO PlayerProgress (user_id, quest_id, current_location, current_task, lives_remaining)
                        OUTPUT INSERTED.id VALUES (?,?,1,1,3)"""
            self.cursor.execute(insert, (user_id, quest_id))
            progress_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return {
                'id': progress_id, 'current_location': 1, 'current_task': 1,
                'lives': 3, 'stars': 0, 'clues': []
            }

    def get_player_clues(self, progress_id: int) -> List[int]:
        query = "SELECT clue_id FROM PlayerClues WHERE progress_id=?"
        self.cursor.execute(query, (progress_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_clue(self, progress_id: int, clue_id: int):
        query = "INSERT INTO PlayerClues (progress_id, clue_id) VALUES (?,?)"
        self.cursor.execute(query, (progress_id, clue_id))
        self.connection.commit()

    def update_progress(self, progress_id: int, location: int = None, task: int = None,
                        lives: int = None, stars: int = None):
        updates = []
        params = []
        if location is not None:
            updates.append("current_location=?")
            params.append(location)
        if task is not None:
            updates.append("current_task=?")
            params.append(task)
        if lives is not None:
            updates.append("lives_remaining=?")
            params.append(lives)
        if stars is not None:
            updates.append("stars_earned=?")
            params.append(stars)
        updates.append("last_played=GETDATE()")
        if updates:
            query = f"UPDATE PlayerProgress SET {', '.join(updates)} WHERE id=?"
            params.append(progress_id)
            self.cursor.execute(query, params)
            self.connection.commit()

    def complete_quest(self, progress_id: int):
        query = "UPDATE PlayerProgress SET is_completed=1, completed_at=GETDATE() WHERE id=?"
        self.cursor.execute(query, (progress_id,))
        self.connection.commit()

    def record_task_attempt(self, progress_id: int, task_id: int, attempts: int, success: bool, time_spent: int = 0):
        query = """INSERT INTO TaskAttempts (progress_id, task_id, attempts_count, is_successful, time_spent, completed_at)
                   VALUES (?,?,?,?,?,GETDATE())"""
        self.cursor.execute(query, (progress_id, task_id, attempts, success, time_spent))
        self.connection.commit()

# ----------------------------------------------------------------------
# АУДИО МЕНЕДЖЕР (без изменений, но использует AssetManager опционально)
# ----------------------------------------------------------------------
class AudioManager:
    def __init__(self, asset_mgr: AssetManager):
        self.music_volume = 0.3
        self.sfx_volume = 0.7
        self.voice_volume = 0.8
        self.current_music = None
        self.assets = asset_mgr

    def play_music(self, filename: str, loop: bool = True):
        try:
            path = os.path.join(MUSIC_PATH, filename)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"Music error: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_sfx(self, filename: str):
        path = os.path.join(SFX_PATH, filename)
        sound = self.assets.load_sound(path)
        if sound:
            sound.set_volume(self.sfx_volume)
            sound.play()

    def play_voice(self, filename: str):
        if not filename:
            return
        path = os.path.join(VOICES_PATH, filename)
        sound = self.assets.load_sound(path)
        if sound:
            sound.set_volume(self.voice_volume)
            sound.play()

# ----------------------------------------------------------------------
# БАЗОВЫЙ КЛАСС СЦЕНЫ
# ----------------------------------------------------------------------
class Scene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        pass

# ----------------------------------------------------------------------
# КАРТА
# ----------------------------------------------------------------------
class MapScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.icons = self._create_icons()
        self.back_button = Button(
            20, SCREEN_HEIGHT - 70, 120, 50, "Выйти",
            normal_color=COLORS['RED'], hover_color=COLORS['ORANGE'],
            assets=self.game.assets, callback=self.exit_game
        )
        # Загрузка фона
        self.background = self.game.assets.load_image(os.path.join(UI_PATH, "map_background.png"),
                                                      (SCREEN_WIDTH, SCREEN_HEIGHT))

    def exit_game(self):
        self.game.running = False

    def _create_icons(self):
        positions = [(150, 300), (350, 200), (550, 300), (450, 500), (700, 450), (800, 150)]
        locs = self.game.db.get_all_locations(self.game.quest_id)
        icons = []
        for i, loc in enumerate(locs):
            locked = (i+1) > self.game.progress['current_location']
            completed = (i+1) < self.game.progress['current_location']
            icon = MapIcon(positions[i][0], positions[i][1], i+1, loc['name'], locked,
                           completed, self.game.assets)
            icons.append(icon)
        return icons

    def handle_event(self, event: pygame.event.Event):
        self.back_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for icon in self.icons:
                if icon.rect.collidepoint(event.pos) and not icon.locked:
                    # Сохраняем выбранную локацию и переходим к диалогу
                    self.game.progress['current_location'] = icon.num
                    self.game.db.update_progress(self.game.progress['id'], location=icon.num)
                    self.game.load_location(icon.num)
                    self.game.change_scene("dialogue")

    def draw(self, screen: pygame.Surface):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLORS['DARK_BROWN'])
        for icon in self.icons:
            icon.draw(screen)
        self.back_button.draw(screen)
        # Отображаем прогресс
        self.game.draw_hud(screen)

# ----------------------------------------------------------------------
# ДИАЛОГОВАЯ СЦЕНА
# ----------------------------------------------------------------------
class DialogueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.dialog = DialogBox(50, SCREEN_HEIGHT - DIALOG_HEIGHT - 20, DIALOG_WIDTH, DIALOG_HEIGHT, game.assets)
        self.background = None
        self.voice_played = False
        self.back_button = Button(20, SCREEN_HEIGHT - 70, 120, 50, "Карта",
                                  normal_color=COLORS['RED'], hover_color=COLORS['ORANGE'],
                                  assets=self.game.assets, callback=self.go_to_map)

    def go_to_map(self):
        self.game.change_scene("map")

    def on_enter(self):
        loc = self.game.current_location_data
        bg_name = loc['background_image']
        self.background = self.game.assets.load_image(os.path.join(BG_PATH, bg_name), (SCREEN_WIDTH, SCREEN_HEIGHT))
        portrait_path = os.path.join(CHAR_PATH, loc['character_portrait'])
        self.dialog.set_dialog(loc['character_name'], loc['dialogue_text'], portrait_path)
        self.voice_played = False

    def handle_event(self, event: pygame.event.Event):
        self.back_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.dialog.is_finished():
                # Переход к заданиям
                self.game.state_task_index = 0
                self.game.task_lives = DEFAULT_LIVES
                self.game.task_attempts = 0
                self.game.change_scene("task")
            else:
                self.dialog.skip_typing()
                # Не воспроизводим голос при скипе

    def update(self, dt: float):
        self.dialog.update()
        # Воспроизведение голоса один раз при старте
        if not self.voice_played:
            voice = self.game.current_location_data.get('voice_file')
            if voice:
                self.game.audio.play_voice(voice)
            self.voice_played = True

    def draw(self, screen: pygame.Surface):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLORS['BROWN'])
        self.dialog.draw(screen)
        self.back_button.draw(screen)
        self.game.draw_hud(screen)

# ----------------------------------------------------------------------
# БАЗОВАЯ МИНИ-ИГРА (неблокирующая)
# ----------------------------------------------------------------------
class MiniGameScene(Scene):
    """Одна сцена для всех мини-игр. Конкретная игра выбирается по task_type."""
    def __init__(self, game):
        super().__init__(game)
        self.task = None
        self.finished = False
        self.success = False
        self.internal_state = {}  # для хранения данных конкретной игры
        self.buttons = []
        self.dragging = None
        self.drag_offset = (0, 0)

    def on_enter(self):
        self.task = self.game.get_current_task()
        if not self.task:
            self.game.change_scene("map")
            return
        self.finished = False
        self.success = False
        self.internal_state = {}
        self.buttons = []
        self.dragging = None
        self._init_game()

    def _init_game(self):
        """Инициализация конкретной мини-игры в зависимости от task_type."""
        task_type = self.task['task_type']
        asset = self.game.assets
        self.buttons.clear()
        if task_type == 'find_differences':
            self._init_find_differences(asset)
        elif task_type == 'count_items':
            self._init_count_items(asset)
        elif task_type == 'math_addition':
            self._init_math_addition(asset)
        elif task_type == 'pattern_recognition':
            self._init_pattern_recognition(asset)
        elif task_type == 'sorting':
            self._init_sorting(asset)
        elif task_type == 'puzzle_strip':
            self._init_puzzle_strip(asset)
        elif task_type == 'balance':
            self._init_balance(asset)
        elif task_type == 'color_mixing':
            self._init_color_mixing(asset)
        elif task_type == 'sound_matching':
            self._init_sound_matching(asset)
        elif task_type == 'connect_dots':
            self._init_connect_dots(asset)
        elif task_type == 'evidence_collector':
            self._init_evidence_collector(asset)
        else:
            self.finished = True
            self.success = False

    # ----- Инициализация каждой игры -----
    def _init_find_differences(self, asset):
        self.internal_state['plan_a'] = asset.load_image(os.path.join(MINIGAMES_PATH, "plan_a.png"), (400, 400))
        self.internal_state['plan_b'] = asset.load_image(os.path.join(MINIGAMES_PATH, "plan_b.png"), (400, 400))
        # Области отличий относительно plan_b
        self.internal_state['diffs'] = [
            pygame.Rect(50, 100, 60, 60),
            pygame.Rect(200, 250, 40, 40),
            pygame.Rect(350, 50, 50, 50)
        ]
        self.internal_state['found'] = [False, False, False]
        self.internal_state['total'] = 3

    def _init_count_items(self, asset):
        self.internal_state['img'] = asset.load_image(os.path.join(MINIGAMES_PATH, "count_cans.png"), (800, 500))
        self.internal_state['correct'] = 7
        # Создаём кнопки 0-10
        btn_w, btn_h = 60, 60
        start_x = SCREEN_WIDTH//2 - 5*btn_w - 20
        for i in range(11):
            btn = Button(start_x + i*(btn_w+10), SCREEN_HEIGHT-100, btn_w, btn_h, str(i),
                         COLORS['BLUE'], COLORS['GREEN'], assets=asset,
                         callback=lambda v=i: self.check_answer(v))
            self.buttons.append(btn)

    def _init_math_addition(self, asset):
        self.internal_state['a'] = random.randint(1, 3)
        self.internal_state['b'] = random.randint(1, 3)
        self.internal_state['correct'] = self.internal_state['a'] + self.internal_state['b']
        can_img = asset.load_image(os.path.join(MINIGAMES_PATH, "math_cans_1.png"), (100, 100))
        self.internal_state['can_img'] = can_img
        for i in range(1, 6):
            btn = Button(SCREEN_WIDTH//2 - 250 + (i-1)*100, SCREEN_HEIGHT-120, 80, 80, str(i),
                         COLORS['BLUE'], COLORS['GREEN'], assets=asset,
                         callback=lambda v=i: self.check_answer(v))
            self.buttons.append(btn)

    def _init_pattern_recognition(self, asset):
        patterns = [
            (['red', 'blue', 'red', 'blue'], 'red'),
            (['red', 'red', 'blue', 'blue'], 'red'),
            (['green', 'yellow', 'green', 'yellow'], 'green')
        ]
        pattern, correct = random.choice(patterns)
        self.internal_state['pattern'] = pattern
        self.internal_state['correct'] = correct
        color_map = {
            'red': 'pattern_red_can.png', 'blue': 'pattern_blue_can.png',
            'green': 'pattern_green_can.png', 'yellow': 'pattern_yellow_can.png',
            'purple': 'pattern_purple_can.png'
        }
        imgs = []
        for col in pattern:
            img = asset.load_image(os.path.join(MINIGAMES_PATH, color_map[col]), (80, 80))
            imgs.append(img)
        self.internal_state['imgs'] = imgs
        self.internal_state['q_img'] = asset.load_image(os.path.join(MINIGAMES_PATH, "pattern_question.png"), (80, 80))
        colors_choice = ['red', 'blue', 'green', 'yellow', 'purple']
        answer_rects = []
        for i, col in enumerate(colors_choice):
            rect = pygame.Rect(SCREEN_WIDTH//2 - 250 + i*100, SCREEN_HEIGHT-120, 70, 70)
            answer_rects.append((asset.load_image(os.path.join(MINIGAMES_PATH, color_map[col]), (70, 70)), rect, col))
        self.internal_state['answer_rects'] = answer_rects

    def _init_sorting(self, asset):
        items = [
            ('item_pineapple.png', True), ('item_cookie.png', True), ('item_can.png', True), ('item_apple.png', True),
            ('item_wrench.png', False), ('item_hammer.png', False), ('item_paint.png', False), ('item_battery.png', False)
        ]
        random.shuffle(items)
        self.internal_state['items'] = []
        start_x, start_y = 200, 300
        for i, (fname, edible) in enumerate(items):
            img = asset.load_image(os.path.join(MINIGAMES_PATH, fname), (80, 80))
            rect = pygame.Rect(start_x + (i%4)*90, start_y + (i//4)*90, 80, 80)
            self.internal_state['items'].append({'img': img, 'rect': rect, 'edible': edible, 'removed': False})
        self.internal_state['bowl_rect'] = pygame.Rect(200, 500, 150, 150)
        self.internal_state['trash_rect'] = pygame.Rect(SCREEN_WIDTH-350, 500, 150, 150)
        self.internal_state['bowl_img'] = asset.load_image(os.path.join(MINIGAMES_PATH, "sort_bowl.png"), (150, 150))
        self.internal_state['trash_img'] = asset.load_image(os.path.join(MINIGAMES_PATH, "sort_trash.png"), (150, 150))
        self.internal_state['correct'] = 0

    def _init_puzzle_strip(self, asset):
        self.internal_state['pieces'] = ['motor', 'belt', 'can']
        random.shuffle(self.internal_state['pieces'])
        self.internal_state['piece_imgs'] = {}
        for p in self.internal_state['pieces']:
            self.internal_state['piece_imgs'][p] = asset.load_image(
                os.path.join(MINIGAMES_PATH, f"puzzle_{p}.png"), (100, 100))
        self.internal_state['slot_imgs'] = {
            1: asset.load_image(os.path.join(MINIGAMES_PATH, "puzzle_slot_1.png"), (100, 100)),
            2: asset.load_image(os.path.join(MINIGAMES_PATH, "puzzle_slot_2.png"), (100, 100)),
            3: asset.load_image(os.path.join(MINIGAMES_PATH, "puzzle_slot_3.png"), (100, 100))
        }
        self.internal_state['slot_positions'] = {1: (300, 400), 2: (450, 400), 3: (600, 400)}
        piece_rects = {}
        start_x = 150
        for i, p in enumerate(self.internal_state['pieces']):
            rect = pygame.Rect(start_x + i*120, 250, 100, 100)
            piece_rects[p] = {'rect': rect, 'placed': False}
        self.internal_state['piece_rects'] = piece_rects
        self.internal_state['placed_order'] = [None, None, None]
        self.internal_state['correct_order'] = ['motor', 'belt', 'can']
        self.dragging = None

    def _init_balance(self, asset):
        self.internal_state['correct'] = 'right'
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT-100, 150, 60, "Левая чаша",
                   COLORS['BLUE'], COLORS['GREEN'], assets=asset, callback=lambda: self.check_answer_str('left')),
            Button(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT-100, 150, 60, "Правая чаша",
                   COLORS['BLUE'], COLORS['GREEN'], assets=asset, callback=lambda: self.check_answer_str('right'))
        ]

    def _init_color_mixing(self, asset):
        self.internal_state['correct'] = 'green'
        blue = asset.load_image(os.path.join(MINIGAMES_PATH, "color_blue.png"), (120, 120))
        yellow = asset.load_image(os.path.join(MINIGAMES_PATH, "color_yellow.png"), (120, 120))
        self.internal_state['blue'] = blue
        self.internal_state['yellow'] = yellow
        color_names = {'red': 'color_red.png', 'green': 'color_green.png', 'orange': 'color_orange.png', 'purple': 'color_purple.png'}
        answer_rects = []
        x = SCREEN_WIDTH//2 - 200
        for i, (name, fname) in enumerate(color_names.items()):
            img = asset.load_image(os.path.join(MINIGAMES_PATH, fname), (80, 80))
            rect = pygame.Rect(x + i*100, SCREEN_HEIGHT-120, 80, 80)
            answer_rects.append((img, rect, name))
        self.internal_state['answer_rects'] = answer_rects

    def _init_sound_matching(self, asset):
        correct = random.choice(['box', 'barrel', 'door'])
        self.internal_state['correct'] = correct
        silhouettes = {}
        for key in ['box', 'barrel', 'door']:
            silhouettes[key] = asset.load_image(os.path.join(MINIGAMES_PATH, f"silhouette_{key}.png"), (150, 150))
        self.internal_state['silhouettes'] = silhouettes
        self.internal_state['sounds'] = {
            'box': 'paper_rustle.wav', 'barrel': 'metal_clang.wav', 'door': 'door_creak.wav'
        }
        self.internal_state['btn_sound'] = pygame.Rect(SCREEN_WIDTH//2 - 50, 500, 100, 50)
        self.internal_state['positions'] = [(200, 300), (SCREEN_WIDTH//2-75, 300), (SCREEN_WIDTH-350, 300)]
        self.internal_state['keys'] = ['box', 'barrel', 'door']

    def _init_connect_dots(self, asset):
        self.internal_state['bg'] = asset.load_image(os.path.join(MINIGAMES_PATH, "dots_background.png"), (800, 500))
        self.internal_state['dots'] = [
            (200, 200), (250, 150), (300, 180), (350, 220), (400, 200),
            (450, 250), (500, 220), (550, 180), (600, 200), (650, 250)
        ]
        self.internal_state['next_dot'] = 1
        self.internal_state['lines'] = []
        self.internal_state['trap_shown'] = False

    def _init_evidence_collector(self, asset):
        evidence = [
            ('shadow.png', 'Тень', False), ('key.png', 'Ключ', False), ('slime.png', 'Слизь', True),
            ('badge.png', 'Бейдж', True), ('photo.png', 'Фото', True), ('recipe.png', 'Рецепт', False)
        ]
        random.shuffle(evidence)
        items = []
        start_x = 100
        for i, (fname, name, is_key) in enumerate(evidence):
            img = asset.load_image(os.path.join(ITEMS_PATH, fname), (80, 80))
            rect = pygame.Rect(start_x + (i%3)*100, 300 + (i//3)*100, 80, 80)
            items.append({'img': img, 'rect': rect, 'is_key': is_key, 'name': name, 'collected': False})
        self.internal_state['items'] = items
        self.internal_state['briefcase'] = asset.load_image(os.path.join(MINIGAMES_PATH, "briefcase.png"), (200, 150))
        self.internal_state['slot_img'] = asset.load_image(os.path.join(MINIGAMES_PATH, "evidence_slot.png"), (100, 100))
        self.internal_state['briefcase_rect'] = pygame.Rect(SCREEN_WIDTH-250, SCREEN_HEIGHT-200, 200, 150)
        self.internal_state['collected'] = []

    # ----- Обработка ответов -----
    def check_answer(self, value):
        """Проверка числового ответа."""
        if value == self.internal_state['correct']:
            self.finish_task(True)
        else:
            self.wrong_answer()

    def check_answer_str(self, value):
        if value == self.internal_state['correct']:
            self.finish_task(True)
        else:
            self.wrong_answer()

    def wrong_answer(self):
        self.game.audio.play_sfx("wrong.wav")
        self.game.task_attempts += 1
        # Уменьшаем жизни, если попытки исчерпаны (по логике, можно отнимать жизнь сразу)
        self.game.task_lives -= 1
        if self.game.task_lives <= 0:
            self.game.return_to_map()
        else:
            # Обновляем прогресс бар, но не завершаем игру
            pass

    def finish_task(self, success: bool):
        self.game.audio.play_sfx("correct.wav" if success else "wrong.wav")
        task = self.task
        self.game.db.record_task_attempt(self.game.progress['id'], task['id'],
                                         self.game.task_attempts + 1, success, 0)
        if success:
            self.game.on_task_success()
        else:
            self.wrong_answer()

    # ----- Обработка событий -----
    def handle_event(self, event: pygame.event.Event):
        task_type = self.task['task_type']
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if task_type == 'find_differences':
                self._handle_find_diff_click(pos)
            elif task_type in ('count_items', 'math_addition'):
                for btn in self.buttons:
                    btn.handle_event(event)
            elif task_type == 'pattern_recognition':
                self._handle_pattern_click(pos)
            elif task_type == 'sorting':
                self._start_drag(pos)
            elif task_type == 'puzzle_strip':
                self._start_puzzle_drag(pos)
            elif task_type == 'color_mixing':
                self._handle_color_mix_click(pos)
            elif task_type == 'sound_matching':
                self._handle_sound_click(pos)
            elif task_type == 'connect_dots':
                self._handle_connect_dot(pos)
            elif task_type == 'evidence_collector':
                self._start_evidence_drag(pos)
            elif task_type == 'balance':
                for btn in self.buttons:
                    btn.handle_event(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if task_type == 'sorting' and self.dragging is not None:
                self._end_drag(event.pos)
            elif task_type == 'puzzle_strip' and self.dragging is not None:
                self._end_puzzle_drag(event.pos)
            elif task_type == 'evidence_collector' and self.dragging is not None:
                self._end_evidence_drag(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging is not None:
                if task_type == 'sorting':
                    item = self.internal_state['items'][self.dragging]
                    item['rect'].center = event.pos
                elif task_type == 'puzzle_strip':
                    piece_name = self.dragging
                    self.internal_state['piece_rects'][piece_name]['rect'].center = event.pos
                elif task_type == 'evidence_collector':
                    item = self.internal_state['items'][self.dragging]
                    item['rect'].center = event.pos

    def _handle_find_diff_click(self, pos):
        x_offset = 512 - 200
        y_offset = 200
        local = (pos[0] - x_offset, pos[1] - y_offset)
        diffs = self.internal_state['diffs']
        found = self.internal_state['found']
        for i, rect in enumerate(diffs):
            if not found[i] and rect.collidepoint(local):
                found[i] = True
                self.game.audio.play_sfx("correct.wav")
                if all(found):
                    self.finish_task(True)
                return
        self.game.audio.play_sfx("wrong.wav")

    def _handle_pattern_click(self, pos):
        for img, rect, col in self.internal_state['answer_rects']:
            if rect.collidepoint(pos):
                if col == self.internal_state['correct']:
                    self.finish_task(True)
                else:
                    self.wrong_answer()

    def _start_drag(self, pos):
        for i, item in enumerate(self.internal_state['items']):
            if not item['removed'] and item['rect'].collidepoint(pos):
                self.dragging = i
                break

    def _end_drag(self, pos):
        item = self.internal_state['items'][self.dragging]
        dropped = False
        if self.internal_state['bowl_rect'].collidepoint(pos) and item['edible']:
            item['removed'] = True
            self.internal_state['correct'] += 1
            dropped = True
            self.game.audio.play_sfx("correct.wav")
        elif self.internal_state['trash_rect'].collidepoint(pos) and not item['edible']:
            item['removed'] = True
            self.internal_state['correct'] += 1
            dropped = True
            self.game.audio.play_sfx("correct.wav")
        if not dropped:
            # Возвращаем на исходную позицию (восстанавливаем из сохраненной)
            # Для простоты оставим на месте, но лучше сохранять начальные координаты
            self.game.audio.play_sfx("wrong.wav")
        self.dragging = None
        if all(it['removed'] for it in self.internal_state['items']):
            self.finish_task(True)

    def _start_puzzle_drag(self, pos):
        for piece, data in self.internal_state['piece_rects'].items():
            if not data['placed'] and data['rect'].collidepoint(pos):
                self.dragging = piece
                break

    def _end_puzzle_drag(self, pos):
        piece = self.dragging
        placed = False
        for slot_num, slot_pos in self.internal_state['slot_positions'].items():
            slot_rect = pygame.Rect(slot_pos[0], slot_pos[1], 100, 100)
            if slot_rect.collidepoint(pos) and self.internal_state['placed_order'][slot_num-1] is None:
                self.internal_state['placed_order'][slot_num-1] = piece
                self.internal_state['piece_rects'][piece]['placed'] = True
                self.game.audio.play_sfx("click.wav")
                placed = True
                break
        if not placed:
            # Возвращаем на место (не сохранили старт, оставим)
            pass
        self.dragging = None
        if all(p is not None for p in self.internal_state['placed_order']):
            if self.internal_state['placed_order'] == self.internal_state['correct_order']:
                self.finish_task(True)
            else:
                self.game.audio.play_sfx("wrong.wav")
                # Сброс
                for p in self.internal_state['piece_rects'].values():
                    p['placed'] = False
                self.internal_state['placed_order'] = [None, None, None]

    def _handle_color_mix_click(self, pos):
        for img, rect, name in self.internal_state['answer_rects']:
            if rect.collidepoint(pos):
                if name == self.internal_state['correct']:
                    self.finish_task(True)
                else:
                    self.wrong_answer()

    def _handle_sound_click(self, pos):
        if self.internal_state['btn_sound'].collidepoint(pos):
            self.game.audio.play_sfx(self.internal_state['sounds'][self.internal_state['correct']])
        else:
            for i, key in enumerate(self.internal_state['keys']):
                rect = pygame.Rect(self.internal_state['positions'][i][0],
                                   self.internal_state['positions'][i][1], 150, 150)
                if rect.collidepoint(pos):
                    if key == self.internal_state['correct']:
                        self.finish_task(True)
                    else:
                        self.wrong_answer()

    def _handle_connect_dot(self, pos):
        if self.internal_state['next_dot'] <= 10:
            target = self.internal_state['dots'][self.internal_state['next_dot']-1]
            if pygame.Rect(target[0]-12, target[1]-12, 24, 24).collidepoint(pos):
                if self.internal_state['next_dot'] > 1:
                    prev = self.internal_state['dots'][self.internal_state['next_dot']-2]
                    self.internal_state['lines'].append((prev, target))
                self.internal_state['next_dot'] += 1
                self.game.audio.play_sfx("click.wav")
                if self.internal_state['next_dot'] > 10:
                    # Показать ловушку
                    self.internal_state['trap_shown'] = True
                    self.game.audio.play_sfx("success.wav")
                    # Завершаем через 1 секунду
                    self.internal_state['trap_timer'] = 1000  # мс
            else:
                self.game.audio.play_sfx("wrong.wav")

    def _start_evidence_drag(self, pos):
        for i, item in enumerate(self.internal_state['items']):
            if not item['collected'] and item['rect'].collidepoint(pos):
                self.dragging = i
                break

    def _end_evidence_drag(self, pos):
        item = self.internal_state['items'][self.dragging]
        if self.internal_state['briefcase_rect'].collidepoint(pos):
            if item['is_key']:
                item['collected'] = True
                self.internal_state['collected'].append(item['name'])
                self.game.audio.play_sfx("collect_item.wav")
                if len(self.internal_state['collected']) >= 3:
                    self.finish_task(True)
            else:
                self.game.audio.play_sfx("wrong.wav")
        self.dragging = None

    # ----- Отрисовка -----
    def draw(self, screen: pygame.Surface):
        task_type = self.task['task_type']
        screen.fill(COLORS['BROWN'])
        getattr(self, f'_draw_{task_type}', lambda s: None)(screen)
        # Кнопки (если есть)
        for btn in self.buttons:
            btn.draw(screen)
        # HUD
        self.game.draw_hud(screen)

    def _draw_find_differences(self, screen):
        font = self.game.assets.get_font('big')
        screen.blit(self.internal_state['plan_a'], (50, 200))
        screen.blit(self.internal_state['plan_b'], (512+50, 200))
        text = font.render(f"Найди отличия: {sum(self.internal_state['found'])}/{self.internal_state['total']}", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))

    def _draw_count_items(self, screen):
        font = self.game.assets.get_font('big')
        screen.blit(self.internal_state['img'], (SCREEN_WIDTH//2 - 400, 150))
        text = font.render("Сколько банок упало на пол?", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 80))

    def _draw_math_addition(self, screen):
        font = self.game.assets.get_font('big')
        a, b = self.internal_state['a'], self.internal_state['b']
        can_img = self.internal_state['can_img']
        question = font.render(f"{a} + {b} = ?", True, COLORS['WHITE'])
        screen.blit(question, (SCREEN_WIDTH//2 - question.get_width()//2, 150))
        for i in range(a):
            screen.blit(can_img, (200 + i*60, 250))
        plus = font.render("+", True, COLORS['WHITE'])
        screen.blit(plus, (500, 260))
        for i in range(b):
            screen.blit(can_img, (550 + i*60, 250))

    def _draw_pattern_recognition(self, screen):
        font = self.game.assets.get_font('big')
        imgs = self.internal_state['imgs']
        x, y = 200, 300
        for img in imgs:
            screen.blit(img, (x, y))
            x += 90
        screen.blit(self.internal_state['q_img'], (x, y))
        text = font.render("Какой цвет следующий?", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150))
        for img, rect, col in self.internal_state['answer_rects']:
            screen.blit(img, rect.topleft)
            pygame.draw.rect(screen, COLORS['WHITE'], rect, 2)

    def _draw_sorting(self, screen):
        font = self.game.assets.get_font('big')
        screen.blit(self.internal_state['bowl_img'], self.internal_state['bowl_rect'])
        screen.blit(self.internal_state['trash_img'], self.internal_state['trash_rect'])
        small = self.game.assets.get_font('small')
        screen.blit(small.render("Съедобное", True, COLORS['WHITE']), (self.internal_state['bowl_rect'].x+10, self.internal_state['bowl_rect'].y+160))
        screen.blit(small.render("Несъедобное", True, COLORS['WHITE']), (self.internal_state['trash_rect'].x+10, self.internal_state['trash_rect'].y+160))
        for item in self.internal_state['items']:
            if not item['removed']:
                screen.blit(item['img'], item['rect'])
        text = font.render("Помоги Скуби: что можно съесть?", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))

    def _draw_puzzle_strip(self, screen):
        font = self.game.assets.get_font('big')
        for num, pos in self.internal_state['slot_positions'].items():
            screen.blit(self.internal_state['slot_imgs'][num], pos)
            placed = self.internal_state['placed_order'][num-1]
            if placed:
                screen.blit(self.internal_state['piece_imgs'][placed], pos)
        for piece, data in self.internal_state['piece_rects'].items():
            if not data['placed']:
                screen.blit(self.internal_state['piece_imgs'][piece], data['rect'])
        text = font.render("Поставь детали в порядке: Мотор -> Лента -> Банка", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))

    def _draw_balance(self, screen):
        scale = self.game.assets.load_image(os.path.join(MINIGAMES_PATH, "balance_scale.png"), (600, 400))
        left = self.game.assets.load_image(os.path.join(MINIGAMES_PATH, "balance_left.png"), (150, 150))
        right = self.game.assets.load_image(os.path.join(MINIGAMES_PATH, "balance_right.png"), (150, 150))
        screen.blit(scale, (SCREEN_WIDTH//2 - 300, 200))
        screen.blit(left, (SCREEN_WIDTH//2 - 280, 250))
        screen.blit(right, (SCREEN_WIDTH//2 + 130, 250))
        font = self.game.assets.get_font('big')
        text = font.render("Какая чашка весов перевесит?", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))

    def _draw_color_mixing(self, screen):
        screen.blit(self.internal_state['blue'], (350, 250))
        screen.blit(self.internal_state['yellow'], (550, 250))
        font = self.game.assets.get_font('big')
        plus = font.render("+", True, COLORS['WHITE'])
        eq = font.render("=", True, COLORS['WHITE'])
        screen.blit(plus, (490, 280))
        screen.blit(eq, (670, 280))
        text = font.render("Какой цвет получится?", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))
        for img, rect, name in self.internal_state['answer_rects']:
            screen.blit(img, rect)
            pygame.draw.rect(screen, COLORS['WHITE'], rect, 2)

    def _draw_sound_matching(self, screen):
        font = self.game.assets.get_font('big')
        for i, key in enumerate(self.internal_state['keys']):
            screen.blit(self.internal_state['silhouettes'][key], self.internal_state['positions'][i])
        pygame.draw.rect(screen, COLORS['BLUE'], self.internal_state['btn_sound'])
        screen.blit(font.render("Слушать", True, COLORS['WHITE']), (self.internal_state['btn_sound'].x+10, self.internal_state['btn_sound'].y+10))
        text = font.render("Кто издаёт звук? Нажми на силуэт", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))

    def _draw_connect_dots(self, screen):
        font = self.game.assets.get_font('big')
        screen.blit(self.internal_state['bg'], (SCREEN_WIDTH//2-400, 100))
        for line in self.internal_state['lines']:
            pygame.draw.line(screen, COLORS['GREEN'], line[0], line[1], 3)
        for i, pos in enumerate(self.internal_state['dots']):
            color = COLORS['YELLOW'] if i+1 == self.internal_state['next_dot'] else COLORS['GRAY']
            pygame.draw.circle(screen, color, pos, 12)
            num_text = font.render(str(i+1), True, COLORS['WHITE'])
            screen.blit(num_text, (pos[0]-10, pos[1]-10))
        text = font.render(f"Соедини точки по порядку: {self.internal_state['next_dot']}", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
        if self.internal_state['trap_shown']:
            trap = self.game.assets.load_image(os.path.join(MINIGAMES_PATH, "net_trap.png"), (800, 500))
            screen.blit(trap, (SCREEN_WIDTH//2-400, 100))

    def _draw_evidence_collector(self, screen):
        font = self.game.assets.get_font('big')
        screen.blit(self.internal_state['briefcase'], self.internal_state['briefcase_rect'])
        for i in range(3):
            screen.blit(self.internal_state['slot_img'], (self.internal_state['briefcase_rect'].x+10+i*60, self.internal_state['briefcase_rect'].y+60))
        for item in self.internal_state['items']:
            if not item['collected']:
                screen.blit(item['img'], item['rect'])
        text = font.render("Перетащи в портфель ТОЛЬКО настоящие улики", True, COLORS['WHITE'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))

    def update(self, dt: float):
        if self.task['task_type'] == 'connect_dots':
            if self.internal_state.get('trap_tunnel', 0) > 0:
                self.internal_state['trap_tunnel'] -= dt
                if self.internal_state['trap_tunnel'] <= 0:
                    self.finish_task(True)

# ----------------------------------------------------------------------
# ПЕРЕХОДНАЯ СЦЕНА
# ----------------------------------------------------------------------
class TransitionScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.timer = 2000  # мс
        self.font = game.assets.get_font('big')

    def on_enter(self):
        self.timer = 2000

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.game.change_scene("map")

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.game.change_scene("map")

    def draw(self, screen):
        screen.fill(COLORS['BLACK'])
        text = self.font.render("Локация пройдена!", True, COLORS['GREEN'])
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))

# ----------------------------------------------------------------------
# ФИНАЛЬНАЯ СЦЕНА
# ----------------------------------------------------------------------
class VictoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = game.assets.get_font('huge')

    def on_enter(self):
        self.game.audio.play_music("victory.wav", loop=False)
        self.game.audio.play_sfx("victory.wav")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.game.running = False

    def draw(self, screen):
        victory = self.game.assets.load_image(os.path.join(UI_PATH, "victory_screen.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
        if victory:
            screen.blit(victory, (0, 0))
        else:
            screen.fill(COLORS['BLACK'])
            text = self.font.render("ПОБЕДА! ДЕЛО РАСКРЫТО!", True, COLORS['GOLD'])
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))

# ----------------------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ UI КЛАССЫ (улучшенные)
# ----------------------------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, normal_color=COLORS['BLUE'], hover_color=COLORS['GREEN'],
                 text_color=COLORS['WHITE'], border_radius=10, assets: Optional[AssetManager]=None, callback=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.hovered = False
        self.callback = callback
        if assets:
            self.font = assets.get_font('button')
            self.normal_img = assets.load_image(os.path.join(UI_PATH, "button_normal.png"), (w, h))
            self.hover_img = assets.load_image(os.path.join(UI_PATH, "button_hover.png"), (w, h))
        else:
            self.font = pygame.font.Font(None, 36)
            self.normal_img = None
            self.hover_img = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback:
                self.callback()
                return True
        return False

    def draw(self, screen):
        if self.hovered and self.hover_img:
            screen.blit(self.hover_img, self.rect)
        elif self.normal_img:
            screen.blit(self.normal_img, self.rect)
        else:
            color = self.hover_color if self.hovered else self.normal_color
            pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(screen, COLORS['WHITE'], self.rect, 2, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class DialogBox:
    def __init__(self, x, y, w, h, assets: AssetManager):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.display_text = ""
        self.char_index = 0
        self.typing_speed = 2
        self.counter = 0
        self.character_name = ""
        self.portrait = None
        self.font_name = assets.get_font('name')
        self.font_text = assets.get_font('text')
        self.finished = False
        self.assets = assets

    def set_dialog(self, name, text, portrait_path=None):
        self.character_name = name
        self.text = text
        self.display_text = ""
        self.char_index = 0
        self.finished = False
        self.counter = 0
        if portrait_path and os.path.exists(portrait_path):
            self.portrait = self.assets.load_image(portrait_path, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        else:
            self.portrait = None

    def update(self):
        if not self.finished:
            self.counter += 1
            if self.counter >= self.typing_speed:
                self.counter = 0
                if self.char_index < len(self.text):
                    self.display_text += self.text[self.char_index]
                    self.char_index += 1
                else:
                    self.finished = True

    def is_finished(self):
        return self.finished

    def skip_typing(self):
        self.display_text = self.text
        self.char_index = len(self.text)
        self.finished = True

    def draw(self, screen):
        pygame.draw.rect(screen, COLORS['BLACK'], self.rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.rect, 3, border_radius=15)
        if self.portrait:
            screen.blit(self.portrait, (self.rect.x + 15, self.rect.y + 15))
        name_surf = self.font_name.render(self.character_name, True, COLORS['YELLOW'])
        screen.blit(name_surf, (self.rect.x + PORTRAIT_SIZE + 30, self.rect.y + 20))
        words = self.display_text.split(' ')
        lines = []
        line = ""
        max_width = self.rect.width - PORTRAIT_SIZE - 60
        for w in words:
            test = line + w + " "
            if self.font_text.size(test)[0] < max_width:
                line = test
            else:
                lines.append(line)
                line = w + " "
        lines.append(line)
        y_offset = self.rect.y + 70
        for line in lines:
            text_surf = self.font_text.render(line, True, COLORS['WHITE'])
            screen.blit(text_surf, (self.rect.x + PORTRAIT_SIZE + 30, y_offset))
            y_offset += 30

class ProgressBar:
    def __init__(self, x, y, max_lives, assets: AssetManager):
        self.rect = pygame.Rect(x, y, 0, 30)
        self.max = max_lives
        self.current = max_lives
        self.heart_full = assets.load_image(os.path.join(UI_PATH, "heart_full.png"))
        self.heart_empty = assets.load_image(os.path.join(UI_PATH, "heart_empty.png"))
        self.heart_size = self.heart_full.get_width() if self.heart_full else 30

    def set_value(self, val):
        self.current = max(0, min(val, self.max))

    def draw(self, screen):
        for i in range(self.max):
            x = self.rect.x - self.heart_size - 5 + i * (self.heart_size + 5)
            y = self.rect.y
            if i < self.current and self.heart_full:
                screen.blit(self.heart_full, (x, y))
            elif i < self.current:
                pygame.draw.circle(screen, COLORS['RED'], (x+15, y+15), 15)
            else:
                if self.heart_empty:
                    screen.blit(self.heart_empty, (x, y))
                else:
                    pygame.draw.circle(screen, COLORS['GRAY'], (x+15, y+15), 15)

class StarsDisplay:
    def __init__(self, x, y, max_stars, assets: AssetManager):
        self.x = x
        self.y = y
        self.max = max_stars
        self.current = 0
        self.star_gold = assets.load_image(os.path.join(UI_PATH, "star_gold.png"))
        self.star_gray = assets.load_image(os.path.join(UI_PATH, "star_gray.png"))
        self.star_size = self.star_gold.get_width() if self.star_gold else 30

    def draw(self, screen):
        for i in range(self.max):
            x = self.x + i * (self.star_size + 5)
            y = self.y
            if i < self.current and self.star_gold:
                screen.blit(self.star_gold, (x, y))
            elif i < self.current:
                # fallback
                pass
            else:
                if self.star_gray:
                    screen.blit(self.star_gray, (x, y))

class MapIcon:
    def __init__(self, x, y, num, name, locked, completed, assets: AssetManager):
        self.rect = pygame.Rect(x-30, y-30, 60, 60)
        self.num = num
        self.name = name
        self.locked = locked
        self.completed = completed
        self.font = assets.get_font('button')

    def draw(self, screen):
        color = COLORS['GRAY'] if self.locked else (COLORS['GREEN'] if not self.completed else COLORS['GOLD'])
        pygame.draw.circle(screen, color, self.rect.center, 30)
        pygame.draw.circle(screen, COLORS['WHITE'], self.rect.center, 30, 3)
        text = self.font.render(str(self.num), True, COLORS['WHITE'])
        screen.blit(text, text.get_rect(center=self.rect.center))
        if self.completed:
            check = pygame.font.Font(None, 30).render("✓", True, COLORS['WHITE'])
            screen.blit(check, (self.rect.right-20, self.rect.top-10))

# ----------------------------------------------------------------------
# ГЛАВНЫЙ КЛАСС ИГРЫ
# ----------------------------------------------------------------------
class GhostGame:
    def __init__(self, screen, user_id: int, quest_id: int = 1):
        pygame.init()
        self.screen = screen
        pygame.display.set_caption("Тайна Призрака в Консервном Замке")
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = AssetManager()
        self.db = DatabaseManager()
        if not self.db.connect():
            raise Exception("DB connection failed")
        self.audio = AudioManager(self.assets)
        self.audio.play_music("factory_ambient.wav")
        self.user_id = user_id
        self.quest_id = quest_id
        self.progress = self.db.get_or_create_progress(user_id, quest_id)

        # Состояния
        self.scenes = {
            'map': MapScene(self),
            'dialogue': DialogueScene(self),
            'task': MiniGameScene(self),
            'transition': TransitionScene(self),
            'victory': VictoryScene(self)
        }
        self.current_scene = self.scenes['map']
        self.current_scene_name = 'map'

        # Данные текущей локации и задания
        self.current_location_data = None
        self.tasks = []
        self.clues = []
        self.state_task_index = 0
        self.task_lives = DEFAULT_LIVES
        self.task_attempts = 0

        # Прогресс-бар и звёзды
        self.progress_bar = ProgressBar(SCREEN_WIDTH - 200, 20, DEFAULT_LIVES, self.assets)
        self.stars = StarsDisplay(20, 20, MAX_STARS, self.assets)
        self.stars.current = len(self.progress['clues'])

        # Загружаем первую локацию (ток прогресс)
        self.load_location(self.progress['current_location'])
        # Если текущее состояние не карта (например, задание сохранено), можно адаптировать
        # Для упрощения всегда начинаем с карты
        self.change_scene('map')

    def load_location(self, loc_num: int):
        self.current_location_data = self.db.get_location_by_number(self.quest_id, loc_num)
        if self.current_location_data:
            self.tasks = self.db.get_tasks_for_location(self.current_location_data['id'])
            self.clues = self.db.get_clues_for_location(self.current_location_data['id'])
            self.state_task_index = 0
            self.task_lives = DEFAULT_LIVES
            self.task_attempts = 0

    def change_scene(self, scene_name: str):
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene_name = scene_name
            # Если у сцены есть метод on_enter, вызываем
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter()
            # Для диалога и задания сразу запускаем нужные настройки
            if scene_name == 'dialogue':
                self.scenes['dialogue'].on_enter()
            elif scene_name == 'task':
                self.scenes['task'].on_enter()

    def get_current_task(self):
        if self.state_task_index < len(self.tasks):
            return self.tasks[self.state_task_index]
        return None

    def on_task_success(self):
        """Вызывается после успешного выполнения задания."""
        self.state_task_index += 1
        if self.state_task_index >= len(self.tasks):
            self.collect_clues()
            self.stars.current = len(self.progress['clues'])
            self.db.update_progress(self.progress['id'], stars=self.stars.current)
            next_loc = self.current_location_data['number'] + 1
            if next_loc <= 6:
                self.db.update_progress(self.progress['id'], location=next_loc)
                self.progress['current_location'] = next_loc
                self.change_scene('transition')
                self.audio.play_sfx("whoosh.wav")
            else:
                self.db.complete_quest(self.progress['id'])
                self.change_scene('victory')
        else:
            # Следующее задание
            self.task_lives = DEFAULT_LIVES
            self.task_attempts = 0
            next_task = self.tasks[self.state_task_index]
            if next_task.get('hint_voice'):
                self.audio.play_voice(next_task['hint_voice'])
            self.change_scene('task')  # перезапустит MiniGameScene с новым task

    def return_to_map(self):
        """Вызывается при поражении (потеря всех жизней)."""
        # Можно вернуться на карту или предложить повторить
        self.change_scene('map')

    def collect_clues(self):
        for clue in self.clues:
            if clue['id'] not in self.progress['clues']:
                self.db.add_clue(self.progress['id'], clue['id'])
                self.progress['clues'].append(clue['id'])
                self.audio.play_sfx("clue.wav")

    def draw_hud(self, screen):
        self.stars.current = len(self.progress['clues'])
        self.stars.draw(screen)
        self.progress_bar.set_value(self.task_lives if self.current_scene_name == 'task' else DEFAULT_LIVES)
        self.progress_bar.draw(screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Выход в карту из любой сцены, кроме карты
                    if self.current_scene_name != 'map':
                        self.change_scene('map')
                    else:
                        self.running = False
                    continue
                self.current_scene.handle_event(event)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()
        self.db.disconnect()
        return self.stars.current

# ----------------------------------------------------------------------
# ТОЧКА ВХОДА ДЛЯ ИНТЕГРАЦИИ
# ----------------------------------------------------------------------
def run_ghost_game(user_id: int, quest_id: int = 1) -> int:
    game = GhostGame(user_id, quest_id)
    stars = game.run()
    return stars

if __name__ == "__main__":
    stars = run_ghost_game(1)
    print(f"Игра завершена. Звёзд получено: {stars}")