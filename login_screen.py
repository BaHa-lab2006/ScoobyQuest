"""
Экран входа в систему
"""
import pygame
import sys
import os
from database import db_manager
from widgets import *

class LoginScreen:
    """Класс экрана входа"""

    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True

        # Загрузка ресурсов
        self.load_resources()

        # Создание UI элементов
        self.create_widgets()

        # Таймер для анимаций
        self.clock = pygame.time.Clock()
        self.animation_timer = 0

        # Сообщения
        self.error_message = ""
        self.error_timer = 0
        self.toast = ToastMessage()

        # Индикатор загрузки
        self.loading = False
        self.loading_spinner = LoadingSpinner(self.width // 2, self.height // 2)

        # Звуки
        self.sounds = {}
        self.load_sounds()

    def load_resources(self):
        """Загрузка ресурсов"""
        # Шрифты
        try:
            font_path = os.path.join("assets", "fonts", "comicsans.ttf")
            if os.path.exists(font_path):
                self.font_medium = pygame.font.Font(font_path, 32)
                self.font_small = pygame.font.Font(font_path, 24)
            else:
                self.font_medium = pygame.font.Font(None, 32)
                self.font_small = pygame.font.Font(None, 24)

            # Специальный шрифт для заголовка
            title_font_path = os.path.join("assets", "fonts", "scooby.ttf")
            if os.path.exists(title_font_path):
                self.font_title = pygame.font.Font(title_font_path, 52)
            else:
                self.font_title = pygame.font.Font(None, 52)
        except:
            self.font_title = pygame.font.Font(None, 52)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

        # Фоновое изображение
        self.background = None
        bg_path = os.path.join("assets", "images", "login_bg.png")
        if os.path.exists(bg_path):
            try:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background,
                                                         (self.width, self.height))
            except:
                self.background = None

        if not self.background:
            # Создаём градиентный фон (чтобы не было пустоты)
            self.background = pygame.Surface((self.width, self.height))
            for y in range(self.height):
                color = (
                    int(0 * (1 - y / self.height) + 240 * (y / self.height)),
                    int(107 * (1 - y / self.height) + 248 * (y / self.height)),
                    int(61 * (1 - y / self.height) + 255 * (y / self.height))
                )
                pygame.draw.line(self.background, color, (0, y), (self.width, y))

    def load_sounds(self):
        """Загрузка звуков"""
        try:
            click_path = os.path.join("assets", "sounds", "click.wav")
            if os.path.exists(click_path):
                self.sounds['click'] = pygame.mixer.Sound(click_path)
        except:
            pass

    def create_widgets(self):
        center_x = self.width // 2

        self.input_username = InputBox(
            center_x - 200, 300, 400, 50,
            "Имя пользователя"
        )

        self.input_password = InputBox(
            center_x - 200, 380, 400, 50,
            "Пароль", is_password=True
        )
        self.input_password.visible_text = False  # пароль скрыт по умолчанию

        # Кнопка входа
        self.btn_login = Button(
            center_x - 150, 480, 300, 60,
            "Войти", font_size=28
        )

        # Кнопка показать/скрыть пароль – прямо у правого края поля ввода пароля
        self.btn_show_password = Button(
            center_x + 210, 380, 110, 50,
            "Показать", font_size=18
        )
        self.password_visible = False

    def play_sound(self, sound_name):
        """Воспроизведение звука"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        self.error_message = message
        self.error_timer = 180  # 3 секунды при 60 FPS
        self.toast.add(message, "error")

    def draw_background(self):
        """Отрисовка фона"""
        # Фон (картинка или градиент)
        self.screen.blit(self.background, (0, 0))

        # Полупрозрачное затемнение для читаемости
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        self.screen.blit(overlay, (0, 0))

        # Заголовок с тенью
        title = "Scooby-Doo"
        shadow = self.font_title.render(title, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.width // 2 + 3 - 175, 173))
        self.screen.blit(shadow, shadow_rect)

        title_surf = self.font_title.render(title, True, ColorScheme.SCOOBY_ORANGE)
        title_rect = title_surf.get_rect(center=(self.width // 2 - 175, 170))
        self.screen.blit(title_surf, title_rect)

        # Подзаголовок
        subtitle = "Модульная образовательная"
        subtitle_surf = self.font_medium.render(subtitle, True, (255, 255, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(self.width // 2 - 182, 230))
        self.screen.blit(subtitle_surf, subtitle_rect)
        subtitle = "игра для дошкольников"
        subtitle_surf = self.font_medium.render(subtitle, True, (255, 255, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(self.width // 2 - 182, 260))
        self.screen.blit(subtitle_surf, subtitle_rect)

        # Убраны декоративные персонажи

    def handle_events(self):
        result = None
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]  # всё ещё нужно для ховера кнопок

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None

            self.input_username.handle_event(event)
            if self.input_password.handle_event(event):
                result = self.attempt_login()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_login.rect.collidepoint(event.pos):
                    result = self.attempt_login()
                elif self.btn_show_password.rect.collidepoint(event.pos):
                    self.toggle_password_visibility()

        # Только визуальное обновление (цвет при наведении), без проверки нажатия
        self.btn_login.update(mouse_pos, mouse_click)
        self.btn_show_password.update(mouse_pos, mouse_click)

        self.input_username.update()
        self.input_password.update()

        # Обновление таймера ошибки
        if self.error_timer > 0:
            self.error_timer -= 1
            if self.error_timer == 0:
                self.error_message = ""

        return result

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.input_password.visible_text = self.password_visible
        self.btn_show_password.text = "Скрыть" if self.password_visible else "Показать"
        self.play_sound('click')

    def attempt_login(self):
        """Попытка входа в систему"""
        username = self.input_username.get_text()
        password = self.input_password.get_text()

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return

        self.loading = True
        self.play_sound('click')

        user = db_manager.verify_user(username, password)

        if user:
            self.toast.add(f"Добро пожаловать, {user['full_name']}!", "success")
            pygame.time.delay(1000)
            self.running = False
            return user
        else:
            self.show_error("Неверный логин или пароль")
            self.loading = False

        return None

    def draw(self):
        """Отрисовка экрана"""
        self.draw_background()

        # Поля ввода
        self.input_username.draw(self.screen)
        self.input_password.draw(self.screen)

        # Кнопки
        self.btn_login.draw(self.screen)
        self.btn_show_password.draw(self.screen)

        # Сообщение об ошибке
        if self.error_message:
            font = pygame.font.Font(None, 24)
            error_surf = font.render(self.error_message, True, (255, 50, 50))
            error_rect = error_surf.get_rect(center=(self.width // 2, 620))
            self.screen.blit(error_surf, error_rect)

        # Индикатор загрузки
        if self.loading:
            self.loading_spinner.update()
            self.loading_spinner.draw(self.screen)
            font = pygame.font.Font(None, 24)
            loading_text = font.render("Проверка данных...", True, (255, 255, 255))
            text_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
            self.screen.blit(loading_text, text_rect)

        # Уведомления
        self.toast.update()
        self.toast.draw(self.screen)

    def run(self):
        """Запуск основного цикла"""
        user_data = None

        while self.running:
            result = self.handle_events()
            if result is not None:
                user_data = result

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        print(user_data)
        return user_data