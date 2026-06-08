import pygame
import sys
import random
import time
import math
from typing import Dict, List, Tuple, Optional, Any

from database import db_manager

# ========== КОНФИГУРАЦИЯ ==========
class Config:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 60
    DB_SERVER = "localhost\MSSQLSERVER04"
    DB_NAME = "ScoobyQuestDB"
    DB_USER = "Shagy"
    DB_PASSWORD = "v.b070217"
    ASSETS_PATH = "assets/game1/"

# ========== МЕНЕДЖЕР АССЕТОВ ==========
class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.voices = {}
        self.fonts = {}
        self.voice_channel = None
        self._load_all()

    def _load_all(self):
        base = Config.ASSETS_PATH
        # Фоны
        self.load_image("prologue_bg", f"{base}images/backgrounds/prologue_bg.png", (1200, 800))
        self.load_image("game_room_bg", f"{base}images/backgrounds/game_room_bg.png", (1200, 800))
        self.load_image("bedroom_bg", f"{base}images/backgrounds/bedroom_bg.png", (1200, 800))
        self.load_image("canteen_bg", f"{base}images/backgrounds/canteen_bg.png", (1200, 800))
        self.load_image("music_hall_bg", f"{base}images/backgrounds/music_hall_bg.png", (1200, 800))
        self.load_image("office_bg", f"{base}images/backgrounds/office_bg.png", (1200, 800))
        # Персонажи
        self.load_image("velma_normal", f"{base}images/characters/velma_normal.png", (150,200))
        self.load_image("velma_thinking", f"{base}images/characters/velma_thinking.png", (150,200))
        self.load_image("velma_happy", f"{base}images/characters/velma_happy.png", (150,200))
        self.load_image("scooby_scared", f"{base}images/characters/scooby_scared.png", (180,200))
        self.load_image("scooby_happy", f"{base}images/characters/scooby_happy.png", (180,200))
        self.load_image("scooby_sad", f"{base}images/characters/scooby_sad.png", (180,200))
        self.load_image("shaggy_normal", f"{base}images/characters/shaggy_normal.png", (150,200))
        self.load_image("shaggy_scared", f"{base}images/characters/shaggy_scared.png", (150,200))
        self.load_image("fred_normal", f"{base}images/characters/fred_normal.png", (150,200))
        self.load_image("fred_pointing", f"{base}images/characters/fred_pointing.png", (150,200))
        self.load_image("daphne_normal", f"{base}images/characters/daphne_normal.png", (150,200))
        self.load_image("guard_normal", f"{base}images/characters/guard_normal.png", (150,200))
        self.load_image("guard_clues", f"{base}images/characters/guard_normal.png", (500, 700))
        self.load_image("guard_happy", f"{base}images/characters/guard_happy.png", (150,200))
        # Предметы
        self.load_image("red_cube", f"{base}images/items/red_cube.png", (60,60))
        self.load_image("blue_cube", f"{base}images/items/blue_cube.png", (60,60))
        self.load_image("yellow_cube", f"{base}images/items/yellow_cube.png", (60,60))
        self.load_image("red_basket", f"{base}images/items/red_basket.png", (200,200))
        self.load_image("blue_basket", f"{base}images/items/blue_basket.png", (200,200))
        self.load_image("yellow_basket", f"{base}images/items/yellow_basket.png", (200,200))
        self.load_image("button_clue", f"{base}images/items/button_clue.png", (60,60))
        self.load_image("newspaper_clue", f"{base}images/items/newspaper_clue.png", (60,60))
        self.load_image("green_paint_clue", f"{base}images/items/green_paint.png", (60,60))
        self.load_image("screwdriver_clue", f"{base}images/items/screwdriver.png", (60,60))
        # Игрушки
        self.load_image("duck_toy", f"{base}images/toys/duck_toy.png", (100,100))
        self.load_image("bunny_toy", f"{base}images/toys/bunny_toy.png", (100,100))
        self.load_image("car_toy", f"{base}images/toys/car_toy.png", (100,100))
        self.load_image("doll_toy", f"{base}images/toys/doll_toy.png", (100,100))
        # UI
        self.load_image("lupa", f"{base}images/ui/lupa.png", (50,50))
        self.load_image("door", f"{base}images/ui/door.png", (100,150))
        self.load_image("door_active", f"{base}images/ui/door_active.png", (100,150))
        # Миниигры
        self.load_image("difference_img_a", f"{base}images/minigames/difference_img_a.png", (450,500))
        self.load_image("difference_img_b", f"{base}images/minigames/difference_img_b.png", (450,500))
        self.load_image("big_slipper", f"{base}images/minigames/big_slipper.png", (80,60))
        self.load_image("small_slipper", f"{base}images/minigames/small_slipper.png", (60,45))
        self.load_image("emotion_happy", f"{base}images/minigames/emotion_happy.png", (120,120))
        self.load_image("emotion_sad", f"{base}images/minigames/emotion_sad.png", (120,120))
        self.load_image("emotion_scared", f"{base}images/minigames/emotion_scared.png", (120,120))
        self.load_image("plate", f"{base}images/minigames/plate.png", (80,80))
        self.load_image("spoon", f"{base}images/minigames/spoon.png", (40,60))
        self.load_image("dirty_note", f"{base}images/minigames/dirty_note.png", (800,400))
        self.load_image("clean_note", f"{base}images/minigames/clean_note.png", (800,400))
        self.load_image("tambourine_1", f"{base}images/minigames/tambourine_1.png", (150,150))
        self.load_image("tambourine_2", f"{base}images/minigames/tambourine_2.png", (150,150))
        self.load_image("tambourine_3", f"{base}images/minigames/tambourine_3.png", (150,150))
        self.load_image("puzzle_1", f"{base}images/minigames/puzzle_1.png", (174, 174))
        self.load_image("puzzle_2", f"{base}images/minigames/puzzle_2.png", (138, 174))
        self.load_image("puzzle_3", f"{base}images/minigames/puzzle_3.png", (138, 138))
        self.load_image("puzzle_4", f"{base}images/minigames/puzzle_4.png", (174, 138))
        self.load_image("puzzle_frame", f"{base}images/minigames/puzzle_frame.png", (435, 390))
        # Звуки (загружаем только если нужны, иначе заглушки)
        # Голоса оставим псевдозагрузкой – реальные файлы mp3
        self.load_sound("click", f"{base}sounds/sfx/click.wav")
        self.load_sound("success", f"{base}sounds/sfx/success.wav")
        self.load_sound("error", f"{base}sounds/sfx/error.wav")
        self.load_sound("fanfare", f"{base}sounds/sfx/fanfare.mp3")
        self.load_sound("complete_level", f"{base}sounds/sfx/complete_level.wav")
        self.load_sound("collect_item", f"{base}sounds/sfx/collect_item.wav")
        self.load_sound("drag_start", f"{base}sounds/sfx/drag_start.wav")
        self.load_sound("drag_drop", f"{base}sounds/sfx/drag_drop.wav")
        self.load_sound("door_open", f"{base}sounds/sfx/door_open.mp3")
        self.load_sound("secret_found", f"{base}sounds/sfx/secret_found.wav")
        self.load_sound("applause", f"{base}sounds/sfx/applause.wav")
        self.load_sound("level_up", f"{base}sounds/sfx/level_up.wav")
        self.load_sound("hint", f"{base}sounds/sfx/hint.wav")
        self.load_sound("timer_tick", f"{base}sounds/sfx/timer_tick.wav")
        self.load_sound("sort_place", f"{base}sounds/sfx/sort_place.wav")
        self.load_sound("difference_found", f"{base}sounds/sfx/difference_found.wav")
        self.load_sound("match_pair", f"{base}sounds/sfx/match_pair.mp3")
        self.load_sound("emotion_correct", f"{base}sounds/sfx/emotion_correct.wav")
        self.load_sound("spoon_place", f"{base}sounds/sfx/spoon_place.wav")
        self.load_sound("erase", f"{base}sounds/sfx/erase.wav")
        self.load_sound("rhythm_correct", f"{base}sounds/sfx/rhythm_correct.wav")
        self.load_sound("puzzle_place", f"{base}sounds/sfx/puzzle_place.wav")
        self.load_sound("tambourine_sound_1", f"{base}sounds/sfx/tambourine_sound_1.wav")
        self.load_sound("tambourine_sound_2", f"{base}sounds/sfx/tambourine_sound_2.wav")
        self.load_sound("tambourine_sound_3", f"{base}sounds/sfx/tambourine_sound_3.wav")
        # Голоса персонажей
        self.load_sound("velma_intro_1", f"{base}voices/velma/intro_1.wav")
        self.load_sound("velma_sort_instr", f"{base}voices/velma/sort_instruction.wav")
        self.load_sound("velma_sort_success", f"{base}voices/velma/sort_success.wav")
        self.load_sound("velma_diff_success", f"{base}voices/velma/differences_success.wav")
        self.load_sound("velma_game_room", f"{base}voices/velma/game_room_1.wav")
        self.load_sound("velma_finale_1", f"{base}voices/velma/finale_1.wav")

        self.load_sound("scooby_scared", f"{base}voices/scooby/scared.wav")
        self.load_sound("scooby_happy_bark", f"{base}voices/scooby/happy_bark.wav")

        self.load_sound("shaggy_bedroom", f"{base}voices/shaggy/bedroom_1.wav")
        self.load_sound("shaggy_success", f"{base}voices/shaggy/bedroom_success.wav")

        self.load_sound("fred_intro", f"{base}voices/fred/intro.wav")
        self.load_sound("fred_music_hall", f"{base}voices/fred/music_hall_1.wav")
        self.load_sound("fred_rhythm_success", f"{base}voices/fred/rhythm_success.wav")

        self.load_sound("daphne_intro", f"{base}voices/daphne/intro.wav")
        self.load_sound("daphne_canteen", f"{base}voices/daphne/canteen_1.wav")
        self.load_sound("daphne_note_success", f"{base}voices/daphne/clean_note_success.wav")

        self.load_sound("guard_intro", f"{base}voices/guard/intro.wav")
        self.load_sound("guard_confession", f"{base}voices/guard/finale_confession.wav")
        self.load_sound("guard_explanation", f"{base}voices/guard/finale_explanation.wav")
        # Шрифты
        self.fonts["main"] = pygame.font.Font(None, 36)
        self.fonts["big"] = pygame.font.Font(None, 56)
        self.fonts["small"] = pygame.font.Font(None, 24)

    def load_image(self, key, path, size=None):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            self.images[key] = img
        except Exception:
            self.images[key] = pygame.Surface(size if size else (100,100))
            self.images[key].fill((200,200,200))
            print(f"⚠️ Не удалось загрузить {path}, используем заглушку")

    def load_sound(self, key, path):
        try:
            self.sounds[key] = pygame.mixer.Sound(path)
        except Exception:
            self.sounds[key] = None
            print(f"⚠️ Не удалось загрузить звук {path}")

    def get_image(self, key):
        return self.images.get(key, pygame.Surface((50,50)))

    def get_sound(self, key):
        return self.sounds.get(key)

    def play_sound(self, key):
        snd = self.get_sound(key)
        if snd:
            snd.play()

    def play_voice(self, key):
        """Проигрывает голосовую реплику, останавливая предыдущую."""
        if self.voice_channel is None:
            self.voice_channel = pygame.mixer.Channel(0)  # зарезервируем канал 0 под голос
        snd = self.sounds.get(key)   # голоса тоже хранятся в self.sounds
        if snd:
            self.voice_channel.stop()
            self.voice_channel.play(snd)

# ========== ДИАЛОГОВАЯ СИСТЕМА ==========
class DialogueBox:

    CHARACTER_PORTRAITS = {
        "Велма": "velma_normal",
        "Скуби": "scooby_scared",      # или scooby_happy, в зависимости от контекста
        "Шэгги": "shaggy_normal",
        "Фред": "fred_normal",
        "Дафна": "daphne_normal",
        "Ночной сторож": "guard_normal",
        "Сторож": "guard_normal",      # упрощённый вариант
    }

    def __init__(self, asset_mgr):
        self.am = asset_mgr
        self.font = self.am.fonts["main"]
        self.showing = False
        self.texts = []
        self.current_idx = 0
        self.width = 1000
        self.height = 200
        self.rect = pygame.Rect(
            (Config.SCREEN_WIDTH - self.width) // 2,
            Config.SCREEN_HEIGHT - self.height - 20,
            self.width,
            self.height
        )
        self.portrait_size = (150, 180)    # ширина, высота
        self.portrait_padding = 20

    def start(self, lines: List[str]):
        self._just_started = True
        self.current_idx = 0
        self.showing = True
        self.texts = []
        self.voices = []
        for item in lines:
            if isinstance(item, tuple):
                text, voice = item
                self.texts.append(text)
                self.voices.append(voice)
            else:
                self.texts.append(item)
                self.voices.append(None)

    def next_line(self) -> bool:
        """Возвращает True, если диалог завершён"""
        self.current_idx += 1
        if self.current_idx >= len(self.texts):
            self.showing = False
            return True
        if self.showing and self.voices[self.current_idx]:
            self.am.play_voice(self.voices[self.current_idx])
        return False
    
    def _parse_line(self, line: str) -> Tuple[Optional[str], str]:
        """
        Извлекает имя персонажа и текст реплики.
        Ожидается формат: "Имя: Текст" или просто "Текст".
        Возвращает (character_name, text). Имя может быть None.
        """
        if ':' in line:
            name, text = line.split(':', 1)
            return name.strip(), text.strip()
        return None, line
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Разбивает текст на строки, не превышающие max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            # Проверяем ширину тестовой строки
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, screen):
        if not self.showing or not self.texts:
            return
        
        if self._just_started:
            self._just_started = False
            if self.voices[self.current_idx]:
                self.am.play_voice(self.voices[self.current_idx])

        # Полупрозрачный фон диалогового окна
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 128))
        screen.blit(bg_surf, self.rect)
        pygame.draw.rect(screen, (255, 255, 200), self.rect, 3)

        current_line = self.texts[self.current_idx]
        char_name, text = self._parse_line(current_line)

        # --- Отображение портрета ---
        portrait_img = None
        if char_name and char_name in self.CHARACTER_PORTRAITS:
            img_key = self.CHARACTER_PORTRAITS[char_name]
            portrait_img = pygame.transform.scale(
                self.am.get_image(img_key),
                self.portrait_size
            )

        # Координаты начала области текста
        text_start_x = self.rect.x + self.portrait_padding
        text_start_y = self.rect.y + self.portrait_padding
        max_text_width = self.width - 2 * self.portrait_padding

        if portrait_img:
            # Если портрет есть, сдвигаем текст вправо
            portrait_x = self.rect.x + self.portrait_padding
            portrait_y = self.rect.y + (self.height - self.portrait_size[1]) // 2
            screen.blit(portrait_img, (portrait_x, portrait_y))
            # Текст начинается справа от портрета
            text_start_x = portrait_x + self.portrait_size[0] + self.portrait_padding
            max_text_width = self.rect.right - text_start_x - self.portrait_padding

        # --- Перенос текста ---
        lines = self._wrap_text(text, self.font, max_text_width)
        y_offset = text_start_y
        for line in lines:
            text_surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surf, (text_start_x, y_offset))
            y_offset += self.font.get_height() + 5

        # --- Имя персонажа (если не отображено портретом) ---
        if char_name and not portrait_img:
            name_surf = self.font.render(char_name + ":", True, (255, 255, 0))
            screen.blit(name_surf, (text_start_x, text_start_y - self.font.get_height() - 5))

        # --- Стрелка продолжения ---
        arrow_font = pygame.font.Font(None, 40)
        arrow_surf = arrow_font.render("►", True, (255, 255, 0))
        screen.blit(arrow_surf, (self.rect.right - 50, self.rect.bottom - 50))

# ========== БАЗОВЫЙ КЛАСС МИНИ-ИГРЫ ==========
class MiniGame:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.am = game_manager.am
        self.db = game_manager.db
        self.completed = False
        self.score = 10
        self.task_id = 0
        self.clue_name = None
        self.toy_name = None
        self.start_time = time.time()
        self.attempts = 0

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    def draw_background(self, screen, darkness=150):
        loc_id = self.gm.current_location_id
        bg_key = self.gm.locations[loc_id]["bg"]
        bg_img = self.am.get_image(bg_key)
        screen.blit(bg_img, (0, 0))
        dark = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, darkness))
        screen.blit(dark, (0, 0))

    def finish(self, success=True):
        elapsed = int(time.time() - self.start_time)
        self.completed = True
        self.gm.add_score(self.score if success else 0)
        self.db.save_completed_task(self.gm.child_id, self.task_id, self.score, elapsed, self.attempts)
        if success:
            self.am.play_sound("success")
        if success and self.clue_name:
            self.db.save_found_clue(self.gm.child_id, self.clue_name)
        if success and self.toy_name:
            self.db.save_collected_toy(self.gm.child_id, self.toy_name)

# ========== КОНКРЕТНЫЕ МИНИ-ИГРЫ ==========

class SortingGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 1
        self.cubes = []
        self.baskets = [
            {"color": "red", "rect": pygame.Rect(200, 400, 200, 200), "count": 0},
            {"color": "blue", "rect": pygame.Rect(500, 400, 200, 200), "count": 0},
            {"color": "yellow", "rect": pygame.Rect(800, 400, 200, 200), "count": 0},
        ]
        self.dragging = None
        self.offset_x = 0
        self.offset_y = 0
        colors = ["red","blue","yellow"]*2
        random.shuffle(colors)
        for col in colors:
            x = random.randint(100, 700)
            y = random.randint(100, 400)
            self.cubes.append({"color": col, "rect": pygame.Rect(x, y, 60, 60)})
        self.total_cubes = len(self.cubes)
        self.sorted_count = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.gm.quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for cube in self.cubes:
                    if cube["rect"].collidepoint(pos):
                        self.dragging = cube
                        self.offset_x = cube["rect"].x - pos[0]
                        self.offset_y = cube["rect"].y - pos[1]
                        self.am.play_sound("drag_start")
                        break
            if event.type == pygame.MOUSEBUTTONUP:
                if self.dragging:
                    self.am.play_sound("drag_drop") 
                    for basket in self.baskets:
                        if basket["rect"].collidepoint(event.pos):
                            if self.dragging["color"] == basket["color"]:
                                self.am.play_sound("sort_place")
                                self.cubes.remove(self.dragging)
                                basket["count"] += 1
                                self.sorted_count += 1
                                if self.sorted_count == self.total_cubes:
                                    self.finish()
                            else:
                                self.attempts += 1
                                self.am.play_sound("error")
                    self.dragging = None
            if event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.dragging["rect"].x = event.pos[0] + self.offset_x
                    self.dragging["rect"].y = event.pos[1] + self.offset_y

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Положи каждый кубик в корзину такого же цвета!", True, (255,255,255))
        screen.blit(txt, (50, 50))
        for basket in self.baskets:
            img_key = basket["color"] + "_basket"
            screen.blit(self.am.get_image(img_key), basket["rect"])
        for cube in self.cubes:
            img_key = cube["color"] + "_cube"
            screen.blit(self.am.get_image(img_key), cube["rect"])

class DifferencesGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 2
        self.diff_spots = [
            pygame.Rect(115,61,40,40),
            pygame.Rect(225,35,40,40),
            pygame.Rect(163,151,40,40),
            pygame.Rect(229,231,40,40),
            pygame.Rect(51,138,40,40)
        ]
        self.found = [False]*5
        self.diff_found_count = 0
        self.img_a_rect = pygame.Rect(50, 100, 450, 500)
        self.img_b_rect = pygame.Rect(524, 100, 450, 500)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.img_a_rect.collidepoint(pos):
                    local_pos = (pos[0]-self.img_a_rect.x, pos[1]-self.img_a_rect.y)
                    for i, spot in enumerate(self.diff_spots):
                        if spot.collidepoint(local_pos) and not self.found[i]:
                            self.found[i] = True
                            self.diff_found_count += 1
                            self.am.play_sound("difference_found")
                            if self.diff_found_count == 5:
                                self.finish()
                if self.img_b_rect.collidepoint(pos):
                    local_pos = (pos[0]-self.img_b_rect.x, pos[1]-self.img_b_rect.y)
                    for i, spot in enumerate(self.diff_spots):
                        if spot.collidepoint(local_pos) and not self.found[i]:
                            self.found[i] = True
                            self.diff_found_count += 1
                            self.am.play_sound("difference_found")
                            if self.diff_found_count == 5:
                                self.finish()

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Найди 5 отличий!", True, (255,255,255))
        screen.blit(txt, (50,50))
        screen.blit(self.am.get_image("difference_img_a"), self.img_a_rect)
        screen.blit(self.am.get_image("difference_img_b"), self.img_b_rect)
        for i, found in enumerate(self.found):
            if found:
                spot = self.diff_spots[i]
                c = (self.img_a_rect.x+spot.centerx, self.img_a_rect.y+spot.centery)
                pygame.draw.circle(screen, (0,255,0), c, 15, 3)
                c = (self.img_b_rect.x+spot.centerx, self.img_b_rect.y+spot.centery)
                pygame.draw.circle(screen, (0,255,0), c, 15, 3)

class BigSmallGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 3

        # Создаём 6 больших и 6 маленьких тапочков (чётное число каждого размера)
        items = []
        for _ in range(6):
            items.append({"type": "big"})
        for _ in range(6):
            items.append({"type": "small"})
        random.shuffle(items)

        self.slippers = []
        for item in items:
            w, h = (100, 75) if item["type"] == "big" else (70, 50)
            x = random.randint(100, 1100 - w)
            y = random.randint(100, 700 - h)
            rect = pygame.Rect(x, y, w, h)
            self.slippers.append({
                "rect": rect,
                "type": item["type"],
                "start_pos": (x, y)
            })

        self.dragging_index = None
        self.drag_offset = (0, 0)
        self.attempts = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, s in enumerate(self.slippers):
                    if s["rect"].collidepoint(pos):
                        self.dragging_index = i
                        self.drag_offset = (s["rect"].x - pos[0], s["rect"].y - pos[1])
                        self.am.play_sound("drag_start")
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_index is not None:
                    self.am.play_sound("drag_drop")
                    dragged = self.slippers[self.dragging_index]
                    match_found = False
                    for i, other in enumerate(self.slippers):
                        if i == self.dragging_index:
                            continue
                        # Совпадение: тот же размер (любой рисунок)
                        if (dragged["rect"].colliderect(other["rect"]) and
                            dragged["type"] == other["type"]):
                            # Удаляем оба тапочка (сначала с большим индексом, чтобы не сбить)
                            idx1, idx2 = self.dragging_index, i
                            if idx1 < idx2:
                                del self.slippers[idx2]
                                del self.slippers[idx1]
                            else:
                                del self.slippers[idx1]
                                del self.slippers[idx2]
                            self.am.play_sound("match_pair")
                            match_found = True
                            if len(self.slippers) == 0:   # всё убрано — победа
                                self.finish()
                            break
                    if not match_found:
                        self.attempts += 1
                        self.am.play_sound("error")
                    self.dragging_index = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_index is not None:
                    s = self.slippers[self.dragging_index]
                    s["rect"].x = event.pos[0] + self.drag_offset[0]
                    s["rect"].y = event.pos[1] + self.drag_offset[1]

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Соедини тапочки одинакового размера в пары!", True, (255,255,255))
        screen.blit(txt, (50, 50))
        for s in self.slippers:
            img = self.am.get_image("big_slipper" if s["type"] == "big" else "small_slipper")
            img = pygame.transform.scale(img, (s["rect"].width, s["rect"].height))
            screen.blit(img, s["rect"])


class EmotionGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 4
        self.emotions = ["happy", "sad", "scared"]
        self.correct = "sad"
        self.emotion_rects = {}
        x = 200
        for e in self.emotions:
            self.emotion_rects[e] = pygame.Rect(x, 300, 120, 120)
            x += 200

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for e, rect in self.emotion_rects.items():
                    if rect.collidepoint(pos):
                        if e == self.correct:
                            self.am.play_sound("emotion_correct")
                            self.finish()
                        else:
                            self.attempts += 1
                            self.am.play_sound("error")

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render('"Игрушкам стало грустно, когда их забрали" - какая эмоция?', True, (255,255,255))
        screen.blit(txt, (100,100))
        for e, rect in self.emotion_rects.items():
            img_key = f"emotion_{e}"
            screen.blit(self.am.get_image(img_key), rect)

class CountGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 5
        self.plates = [pygame.Rect(100 + i*120, 400, 80,80) for i in range(5)]
        self.spoons = []
        for _ in range(5):
            x = random.randint(50, 750)
            y = random.randint(50, 300)
            rect = pygame.Rect(x, y, 40, 60)
            self.spoons.append({
                "rect": rect,
                "placed": False,
                "start_pos": (x,y)
            })
        self.dragging_spoon_index = None
        self.drag_offset = (0, 0)
        self.placed_count = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, spoon in enumerate(self.spoons):
                    if not spoon["placed"] and spoon["rect"].collidepoint(pos):
                        self.dragging_spoon_index = i
                        self.drag_offset = (
                            spoon["rect"].x - pos[0],
                            spoon["rect"].y - pos[1]
                        )
                        self.am.play_sound("drag_start")
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_spoon_index is not None:
                    idx = self.dragging_spoon_index
                    spoon = self.spoons[idx]
                    self.am.play_sound("drag_drop")
                    placed = False
                    for plate in self.plates:
                        if plate.colliderect(spoon["rect"]):
                            # Проверяем, не занята ли уже тарелка
                            occupied = any(
                                s["placed"] and s["rect"].colliderect(plate)
                                for s in self.spoons
                            )
                            if not occupied:
                                spoon["placed"] = True
                                # Центрируем ложку на тарелке
                                spoon["rect"].centerx = plate.centerx
                                spoon["rect"].centery = plate.centery - 10
                                self.placed_count += 1
                                self.am.play_sound("spoon_place")
                                placed = True
                                if self.placed_count == 5:
                                    self.finish()
                                break
                    if not placed:
                        # Возвращаем на исходную позицию
                        spoon["rect"].topleft = spoon["start_pos"]
                    self.dragging_spoon_index = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_spoon_index is not None:
                    spoon = self.spoons[self.dragging_spoon_index]
                    spoon["rect"].x = event.pos[0] + self.drag_offset[0]
                    spoon["rect"].y = event.pos[1] + self.drag_offset[1]

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render(
            "Положи по одной ложке на каждую тарелку (счёт до 5)!",
            True, (255, 255, 255)
        )
        screen.blit(txt, (50, 50))
        for plate in self.plates:
            screen.blit(self.am.get_image("plate"), plate)
        for spoon in self.spoons:
            screen.blit(self.am.get_image("spoon"), spoon["rect"])

class CleanNoteGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 6
        self.dirty_surf = pygame.Surface((800,400), pygame.SRCALPHA)
        self.dirty_surf.fill((139,90,43, 255))
        self.note_rect = pygame.Rect(112, 184, 800, 400)
        self.prev_mask_count = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                pos = event.pos
                if self.note_rect.collidepoint(pos):
                    local = (pos[0]-self.note_rect.x, pos[1]-self.note_rect.y)
                    pygame.draw.circle(self.dirty_surf, (0,0,0,0), local, 30)
                    self.am.play_sound("erase") 
            if event.type == pygame.MOUSEBUTTONUP:
                mask = pygame.mask.from_surface(self.dirty_surf)
                if mask.count() < 0.7 * 800 * 400:  # около 30% очищено
                    self.finish()

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Потри пятно, чтобы прочитать записку!", True, (255,255,255))
        screen.blit(txt, (50,50))
        screen.blit(self.am.get_image("clean_note"), self.note_rect)
        screen.blit(self.dirty_surf, self.note_rect)

class RhythmGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 7
        self.tamb_rects = [
            pygame.Rect(150, 400, 150,150),
            pygame.Rect(437, 400, 150,150),
            pygame.Rect(724, 400, 150,150)
        ]
        self.sequence = random.choices([0,1,2], k=3)
        self.player_input = []
        self.showing_sequence = True
        self.show_step = 0
        self.show_timer = 0
        self.show_delay = 800
        self.tamb_sounds = [
            "tambourine_sound_1",
            "tambourine_sound_2",
            "tambourine_sound_3"
        ]

    def handle_events(self, events):
        if self.showing_sequence:
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, rect in enumerate(self.tamb_rects):
                    if rect.collidepoint(pos):
                        self.player_input.append(i)
                        self.am.play_sound(self.tamb_sounds[i])
                        if self.player_input == self.sequence[:len(self.player_input)]:
                            if len(self.player_input) == len(self.sequence):
                                self.am.play_sound("rhythm_correct")
                                self.finish()
                        else:
                            self.attempts += 1
                            self.player_input.clear()
                            self.am.play_sound("error")

    def update(self):
        if self.showing_sequence:
            now = pygame.time.get_ticks()
            if self.show_timer == 0:
                self.show_timer = now
                first_idx = self.sequence[0]
                self.am.play_sound(self.tamb_sounds[first_idx])
            elif now - self.show_timer > self.show_delay:
                self.show_step += 1
                self.show_timer = now
                if self.show_step >= len(self.sequence):
                    self.showing_sequence = False
                    self.show_step = -1
                else:
                    idx = self.sequence[self.show_step]
                    self.am.play_sound(self.tamb_sounds[idx])

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Повтори ритм! Запомни последовательность.", True, (255,255,255))
        screen.blit(txt, (50,50))
        for i, rect in enumerate(self.tamb_rects):
            img_key = f"tambourine_{i+1}"
            screen.blit(self.am.get_image(img_key), rect)
            if self.showing_sequence and i == self.sequence[self.show_step]:
                pygame.draw.rect(screen, (255,255,0), rect, 6)
        seq_txt = " ".join(str(x+1) for x in self.player_input)
        surf = font.render(f"Твой ритм: {seq_txt}", True, (255,255,255))
        screen.blit(surf, (300, 200))

class PuzzleGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 8

        # Рамка пазла (размер 435x390). Центрируем на экране 1200x800.
        frame_w, frame_h = 435, 390
        self.frame_rect = pygame.Rect(
            (Config.SCREEN_WIDTH - frame_w) // 2,
            (Config.SCREEN_HEIGHT - frame_h) // 2,
            frame_w,
            frame_h
        )

        # Целевые зоны для каждого кусочка (координаты из отладки)
        self.targets = [
            pygame.Rect(462, 266, 174, 174),  # кусочек 1 (верхний левый)
            pygame.Rect(600, 266, 138, 174),  # кусочек 2 (верхний правый)
            pygame.Rect(600, 404, 138, 138),  # кусочек 3 (нижний правый)
            pygame.Rect(462, 404, 174, 138)   # кусочек 4 (нижний левый)
        ]

        # Кусочки: размеры уже масштабированы (174x174, 138x174, 138x138, 174x138)
        piece_sizes = [
            (174, 174),  # кусочек 1
            (138, 174),  # кусочек 2
            (138, 138),  # кусочек 3
            (174, 138)   # кусочек 4
        ]
        self.pieces = []
        # Стартовые позиции — столбиком справа от рамки
        start_x = 900
        start_y = 200
        step_y = 130
        for i, (w, h) in enumerate(piece_sizes):
            rect = pygame.Rect(start_x, start_y + i * step_y, w, h)
            self.pieces.append({
                "img": f"puzzle_{i+1}",
                "rect": rect,
                "target_idx": i,
                "placed": False
            })

        self.dragging_piece = None
        self.drag_offset = (0, 0)
        # Допуск: на сколько пикселей можно ошибиться при установке
        self.SNAP_TOLERANCE = 25

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.gm.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for p in self.pieces:
                    if not p["placed"] and p["rect"].collidepoint(pos):
                        self.dragging_piece = p
                        self.drag_offset = (p["rect"].x - pos[0], p["rect"].y - pos[1])
                        self.am.play_sound("drag_start")
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_piece:
                    self.am.play_sound("drag_drop")
                    piece = self.dragging_piece
                    target = self.targets[piece["target_idx"]]
                    # Проверяем, находится ли кусочек близко к целевой зоне
                    if (abs(piece["rect"].x - target.x) <= self.SNAP_TOLERANCE and
                        abs(piece["rect"].y - target.y) <= self.SNAP_TOLERANCE):
                        # Примагничиваем точно на место
                        piece["rect"].topleft = target.topleft
                        piece["placed"] = True
                        self.am.play_sound("puzzle_place")
                        # Проверяем, все ли кусочки на месте
                        if all(p["placed"] for p in self.pieces):
                            self.finish()
                    self.dragging_piece = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_piece:
                    self.dragging_piece["rect"].x = event.pos[0] + self.drag_offset[0]
                    self.dragging_piece["rect"].y = event.pos[1] + self.drag_offset[1]

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Собери пазл: перетащи кусочки на рамку!", True, (255,255,255))
        screen.blit(txt, (50, 50))

        # Рисуем рамку
        frame_img = self.am.get_image("puzzle_frame")
        screen.blit(frame_img, self.frame_rect)

        # Рисуем кусочки
        for p in self.pieces:
            img = self.am.get_image(p["img"])
            img = pygame.transform.scale(img, (p["rect"].width, p["rect"].height))
            screen.blit(img, p["rect"])

    def update(self):
        pass

class FinalClueGame(MiniGame):
    def __init__(self, gm):
        super().__init__(gm)
        self.task_id = 9
        self.photo_rect = pygame.Rect(50, 100, 500, 700)
        self.spots = {
            "green_paint": pygame.Rect(236, 581, 40, 40),
            "screwdriver": pygame.Rect(363, 466, 40, 40),
            "newspaper":   pygame.Rect(574, 330, 40, 40),
            "button":      pygame.Rect(210, 324, 40, 40)
        }
        self.clues = [
            {"type": "button",       "rect": pygame.Rect(750, 150, 60, 60)},
            {"type": "newspaper",    "rect": pygame.Rect(750, 250, 60, 60)},
            {"type": "green_paint",  "rect": pygame.Rect(750, 350, 60, 60)},
            {"type": "screwdriver",  "rect": pygame.Rect(750, 450, 60, 60)}
        ]
        self.dragging_clue = None
        self.offset = (0,0)
        self.placed = set()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for clue in self.clues:
                    if clue["rect"].collidepoint(pos) and clue["type"] not in self.placed:
                        self.dragging_clue = clue
                        self.offset = (clue["rect"].x - pos[0], clue["rect"].y - pos[1])
                        self.am.play_sound("drag_start")
                        break
            if event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_clue:
                    self.am.play_sound("drag_drop")
                    clue_type = self.dragging_clue["type"]
                    spot_rect = self.spots[clue_type]
                    if self.dragging_clue["rect"].colliderect(spot_rect):
                        self.placed.add(clue_type)
                        self.am.play_sound("match_pair")
                        if len(self.placed) == 4:
                            self.finish()
                    self.dragging_clue = None
            if event.type == pygame.MOUSEMOTION:
                if self.dragging_clue:
                    self.dragging_clue["rect"].x = event.pos[0] + self.offset[0]
                    self.dragging_clue["rect"].y = event.pos[1] + self.offset[1]

    def draw(self, screen):
        self.draw_background(screen)
        font = self.am.fonts["small"]
        txt = font.render("Сопоставь улики на фото сторожа!", True, (255,255,255))
        screen.blit(txt, (50,50))
        screen.blit(self.am.get_image("guard_clues"), self.photo_rect)
        for spot in self.spots.values():
            pygame.draw.rect(screen, (255,0,0), spot, 2)
        for clue in self.clues:
            img_key = clue["type"] + "_clue"
            screen.blit(self.am.get_image(img_key), clue["rect"])

# ========== ИГРОВОЙ МЕНЕДЖЕР ==========
class GameManager:
    def __init__(self, screen, user_info):
        # ========== ОТЛАДКА ==========
        # self.DEBUG_START_LOCATION = 4
        # self.DEBUG_PRINT_CLICKS = True
        # ========== ОТЛАДКА ==========

        pygame.mixer.init()
        self.screen = screen
        pygame.display.set_caption("Скуби-Ду и Тайна Пропавших Игрушек")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"

        self.am = AssetManager()
        self.db = db_manager
        self.dialogue = DialogueBox(self.am)

        self.user_info = user_info
        self.child_id = user_info['id']

        progress = self.db.get_child_progress(self.child_id)
        if progress:
            self.quest_id = progress['quest_id']
        else:
            self.quest_id = 1

        self.current_location_id = 1
        self.total_score = 0
        self.hints_used = 0
        self.collected_toys = []
        self.found_clues = []
        self.tasks_completed = {loc: [] for loc in range(1,6)}

        self.locations = self._init_locations()
        self.active_minigame = None

        self.prologue_lines = [
            ("Велма: Ребята, к нам в детский сад 'Радуга' пришла беда! Каждое утро игрушки исчезают из группы!", "velma_intro_1"),
            ("Скуби: Ррр-ррябя?!", "scooby_scared"),
            ("Ночной сторож: Это Ворчащий Гномик! Он не любит, когда дети шумят, вот и забирает игрушки!", "guard_intro"),
            ("Фред: Но мы, 'Тайна Инкорпорейтед', не верим в сказки! Помоги нам найти настоящую причину!", "fred_intro"),
            ("Дафна: Будь нашим глазами и ушами в садике! Вперёд!", "daphne_intro")
        ]
        self.prologue_idx = 0

        self.DOOR_POS = (1050, 590)
        self.DOOR_RECT = pygame.Rect(1050, 590, 150, 210)

        self.zones = {
            1: [
                {'rect': pygame.Rect(801, 270, 70, 100), 'action': ('minigame', 2)},
                {'rect': pygame.Rect(0, 730, 220, 70), 'action': ('minigame', 1)},
                {'rect': self.DOOR_RECT, 'action': ('door', 2), 'needs_complete': True},
            ],
            2: [
                {'rect': pygame.Rect(930, 732, 269, 51), 'action': ('minigame', 3)},
                {'rect': pygame.Rect(330, 712, 107, 85), 'action': ('minigame', 4)},
                {'rect': self.DOOR_RECT, 'action': ('door', 3), 'needs_complete': True},
            ],
            3: [
                {'rect': pygame.Rect(433, 518, 281, 35), 'action': ('minigame', 5)},
                {'rect': pygame.Rect(623, 216, 35, 57), 'action': ('minigame', 6)},
                {'rect': self.DOOR_RECT, 'action': ('door', 4), 'needs_complete': True},
            ],
            4: [
                {'rect': pygame.Rect(33, 545, 524, 236), 'action': ('minigame', 7)},
                {'rect': pygame.Rect(667, 1, 92, 43), 'action': ('minigame', 8)},
                {'rect': self.DOOR_RECT, 'action': ('door', 5), 'needs_complete': True},
            ]
        }

        # ========== ОТЛАДКА ==========
        # if self.DEBUG_START_LOCATION > 0:
        #     self.state = "LOCATION"
        #     self.current_location_id = self.DEBUG_START_LOCATION
        #     for loc_id in range(1, self.DEBUG_START_LOCATION):
        #         for task_id in self.locations[loc_id]["tasks"]:
        #             self.tasks_completed[loc_id].append(task_id)
        # ========== ОТЛАДКА ==========

    def _init_locations(self):
        return {
            1: {"name": "Игровая комната", "bg": "game_room_bg", "tasks": [1,2], "next_loc": 2},
            2: {"name": "Спальня", "bg": "bedroom_bg", "tasks": [3,4], "next_loc": 3},
            3: {"name": "Столовая", "bg": "canteen_bg", "tasks": [5,6], "next_loc": 4},
            4: {"name": "Музыкальный зал", "bg": "music_hall_bg", "tasks": [7,8], "next_loc": 5},
            5: {"name": "Кабинет заведующей", "bg": "office_bg", "tasks": [9], "next_loc": None},
        }

    def quit_game(self):
        self.running = False

    def add_score(self, pts):
        self.total_score += pts

    def get_location_progress(self):
        loc = self.locations[self.current_location_id]
        tasks = loc["tasks"]
        completed = [t for t in tasks if t in self.tasks_completed[self.current_location_id]]
        return len(completed), len(tasks)

    def is_location_complete(self):
        done, total = self.get_location_progress()
        return done == total

    def start_minigame(self, task_id):
        if task_id in self.tasks_completed[self.current_location_id]:
            return
        mg = None
        if task_id == 1: mg = SortingGame(self)
        elif task_id == 2: mg = DifferencesGame(self)
        elif task_id == 3: mg = BigSmallGame(self)
        elif task_id == 4: mg = EmotionGame(self)
        elif task_id == 5: mg = CountGame(self)
        elif task_id == 6: mg = CleanNoteGame(self)
        elif task_id == 7: mg = RhythmGame(self)
        elif task_id == 8: mg = PuzzleGame(self)
        elif task_id == 9: mg = FinalClueGame(self)
        if mg:
            self.active_minigame = mg
            self.state = "MINIGAME"

    def complete_task(self, task_id):
        if task_id not in self.tasks_completed[self.current_location_id]:
            self.tasks_completed[self.current_location_id].append(task_id)
            clue_map = {1: "button", 3: "newspaper", 5: "green_paint", 7: "screwdriver"}
            toy_map = {1: "duck_toy", 3: "bunny_toy", 5: "car_toy", 7: "doll_toy"}
            if task_id in clue_map:
                self.found_clues.append(clue_map[task_id])
                self.am.play_sound("secret_found")   
            if task_id in toy_map:
                self.collected_toys.append(toy_map[task_id])
                self.am.play_sound("collect_item")  
            # --- Диалоги после завершения задания (согласно сценарию) ---
            task_dialogs = {
                1: [("Велма: Отлично! Мы нашли первую игрушку и улику!", "velma_sort_success")],
                2: [("Велма: Молодец! Мы нашли все отличия!", "velma_diff_success")],
                3: [("Шэгги: Ого! Ещё одна! И газета... Может, Гномик их чинит?", "shaggy_success")],
                4: [("Скуби: (радостно тявкает)", "scooby_happy_bark")],
                5: [("Улика: Пятно зелёной краски (отпечаток пальца) — под крайней тарелкой", None)],
                6: [("Дафна: Не гном... Интересно! Кто же красил что-то зелёным?", "daphne_note_success")],
                7: [("Фред: Отвёртка, краска... Он чинил игрушки!", "fred_rhythm_success")],
                9: [
                    ("Сторож: Ох, ребята, вы меня раскусили... Это был я. Но я не вор!", "guard_confession"),
                    ("Велма: Всё сходится! Пуговица, краска, отвёртка, объявление...", "velma_finale_1"),
                    ("Сторож: Я чинил игрушки по ночам, а про Гномика придумал, чтобы не мешали.", "guard_explanation")
                ]
            }
            if task_id in task_dialogs:
                self.dialogue.start(task_dialogs[task_id])
            if self.is_location_complete():                 # <-- добавить
                self.am.play_sound("complete_level")


    def go_to_location(self, loc_id):
        self.am.play_sound("door_open")
        self.current_location_id = loc_id
        if loc_id > 1:
            self.am.play_sound("level_up")
        self.state = "LOCATION"
        # --- Диалоги при входе в каждую локацию (как в сценарии) ---
        if loc_id == 1:
            self.dialogue.start([
                ("Велма: Смотри, какой беспорядок! Игрушки не просто потерялись – их кто-то унёс. Давай наведём порядок и поищем подсказки.", "velma_game_room")
            ])
        elif loc_id == 2:
            self.dialogue.start([
                ("Шэгги: Здесь так тихо... Жутковато! Я слышал, Гномик особенно любит брать игрушки отсюда!", "shaggy_bedroom"),
                ("Скуби: (кивает и облизывается от волнения)", "scooby_scared")
            ])
        elif loc_id == 3:
            self.dialogue.start([
                ("Дафна: Смотри, кто-то здесь перекусил ночью. И не просто так... Кажется, он оставил нам записку. Но она перепачкана кашей!", "daphne_canteen")
            ])
        elif loc_id == 4:
            self.dialogue.start([
                ("Фред: По моим расчётам, все найденные улики ведут сюда! И смотри – на полу возле горшка с цветком тоже зелёная краска!", "fred_music_hall")
            ])
        elif loc_id == 5:
            self.state = "FINALE"
            if 9 not in self.tasks_completed[5]:
                self.start_minigame(9)
            else:
                self.state = "END_SCREEN"

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    tasks_done = self.tasks_completed.get(self.current_location_id, [])
                    self.db.save_scooby_progress(
                        child_id=self.child_id,
                        location=self.current_location_id,
                        tasks_completed=tasks_done,
                        collected_toys=self.collected_toys,
                        found_clues=self.found_clues,
                        score=self.total_score
                    )
                    self.quit_game()

            if self.state == "MENU":
                self._handle_menu(events)
            elif self.state == "PROLOGUE":
                self._handle_prologue(events)
            elif self.state == "LOCATION":
                self._handle_location(events)
            elif self.state == "MINIGAME":
                self._handle_minigame(events)
            elif self.state == "FINALE":
                self._handle_finale(events)
            elif self.state == "END_SCREEN":
                self._handle_end_screen(events)

            self.screen.fill((0,0,0))
            if self.state == "MENU":
                self._draw_menu()
            elif self.state == "PROLOGUE":
                self._draw_prologue()
            elif self.state in ("LOCATION", "FINALE"):
                self._draw_location()
                self._draw_highlights()
                self.dialogue.draw(self.screen)
            elif self.state == "MINIGAME":
                if self.active_minigame:
                    self.active_minigame.draw(self.screen)
            elif self.state == "END_SCREEN":
                self._draw_end_screen()

            pygame.display.flip()
            self.clock.tick(Config.FPS)

    def _handle_menu(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(400,500,200,80).collidepoint(event.pos):
                    self.am.play_sound("click")
                    self.state = "PROLOGUE"
                    self.dialogue.start(self.prologue_lines)

    def _draw_menu(self):
        font = self.am.fonts["big"]
        title = font.render("Скуби-Ду и Тайна Пропавших Игрушек", True, (255,255,255))
        self.screen.blit(title, (100,200))
        pygame.draw.rect(self.screen, (0,200,0), (400,500,200,80))
        txt = self.am.fonts["main"].render("ИГРАТЬ", True, (255,255,255))
        self.screen.blit(txt, (450,520))

    def _handle_prologue(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.dialogue.showing:
                    done = self.dialogue.next_line()
                    if done:
                        self.go_to_location(1)

    def _draw_prologue(self):
        self.screen.blit(self.am.get_image("prologue_bg"), (0,0))
        self.dialogue.draw(self.screen)

    def _draw_highlights(self):
        """
        Рисует жёлтую рамку вокруг зоны под указателем мыши,
        если зона активна (условие needs_complete выполнено).
        Также меняет курсор на 'руку' при наведении.
        """
        mouse_pos = pygame.mouse.get_pos()
        loc_id = self.current_location_id
        zones = self.zones.get(loc_id, [])
        highlighted = False
        for zone in zones:
            if zone.get('needs_complete') and not self.is_location_complete():
                continue
            if zone['rect'].collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (255, 255, 0), zone['rect'], 3)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                highlighted = True
                break
        if not highlighted:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def _handle_location(self, events):
        """
        Универсальный обработчик кликов по зонам текущей локации.
        """
        loc_id = self.current_location_id
        zones = self.zones.get(loc_id, [])
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.dialogue.showing:
                    self.dialogue.next_line()
                    continue

                pos = event.pos
                for zone in zones:
                    # Пропускаем зоны, требующие завершения мини-игр, если условие не выполнено
                    if zone.get('needs_complete') and not self.is_location_complete():
                        continue
                    if zone['rect'].collidepoint(pos):
                        action, value = zone['action']
                        if action == 'minigame':
                            self.start_minigame(value)
                        elif action == 'door':
                            self.go_to_location(value)
                        break  # Обрабатываем только одно попадание за клик

    def _draw_location(self):
        loc = self.locations[self.current_location_id]
        bg = self.am.get_image(loc["bg"])
        self.screen.blit(bg, (0,0))
        if self.current_location_id != 5:
            done, total = self.get_location_progress()
            
            bar_x, bar_y = 20, 20
            bar_width, bar_height = 300, 30
            pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

            fill_width = int(bar_width * (done / total if total else 0))
            if fill_width > 0:
                pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))

            pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

            txt = self.am.fonts["small"].render(f"{done}/{total}", True, (255,255,255))
            self.screen.blit(txt, (bar_x + bar_width + 10, bar_y + 5))

        if self.is_location_complete() and self.current_location_id < 5:
            door = self.am.get_image("door_active")
        else:
            door = self.am.get_image("door")
        door_img = pygame.transform.scale(door, (self.DOOR_RECT.width, self.DOOR_RECT.height))
        self.screen.blit(door_img, self.DOOR_POS)

    def _handle_minigame(self, events):
        if not self.active_minigame:
            return
        self.active_minigame.handle_events(events)
        self.active_minigame.update()
        if self.active_minigame.completed:
            task_id = self.active_minigame.task_id
            self.complete_task(task_id)
            self.active_minigame = None
            self.state = "LOCATION" if self.current_location_id < 5 else "FINALE"

    def _handle_finale(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.dialogue.showing:
                    done = self.dialogue.next_line()
                    if done:
                        if 9 in self.tasks_completed[self.current_location_id]:
                            self.am.play_sound("fanfare")
                            self.am.play_sound("applause")
                            self.state = "END_SCREEN"


    def _handle_end_screen(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if pygame.Rect(300,600,200,80).collidepoint(pos):
                    self.state = "MENU"
                if pygame.Rect(524,600,200,80).collidepoint(pos):
                    self.state = "MENU"

    def _draw_end_screen(self):
        self.screen.fill((20,20,50))

        center_x, center_y = 512, 250
        # Рисуем звезду
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5  # для 5-лучевой звезды
            if i % 2 == 0:
                r = 80
            else:
                r = 35
            points.append((center_x + int(r * math.cos(angle)),
                        center_y - int(r * math.sin(angle))))
        pygame.draw.polygon(self.screen, (255, 215, 0), points)
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 3)

        font = self.am.fonts["big"]
        congrats = font.render("ПОЗДРАВЛЯЕМ!", True, (255,215,0))
        self.screen.blit(congrats, (380,400))

        font2 = self.am.fonts["main"]
        txt = font2.render("Ты раскрыл тайну! Заработано очков: "+str(self.total_score), True, (255,255,255))
        self.screen.blit(txt, (300,500))

        btn_w, btn_h = 200, 80
        btn_y = 600

        btn1_rect = pygame.Rect(300, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (0, 150, 0), btn1_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), btn1_rect, 2, border_radius=10)
        btn_text = self.am.fonts["small"].render("В МЕНЮ", True, (255, 255, 255))
        self.screen.blit(btn_text, (btn1_rect.x + 60, btn1_rect.y + 25))

        btn2_rect = pygame.Rect(524, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (0, 150, 0), btn2_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), btn2_rect, 2, border_radius=10)
        btn_text2 = self.am.fonts["small"].render("ЗАНОВО", True, (255, 255, 255))
        self.screen.blit(btn_text2, (btn2_rect.x + 65, btn2_rect.y + 25))


if __name__ == "__main__":
    game = GameManager()
    game.run()