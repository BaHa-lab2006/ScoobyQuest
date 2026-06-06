"""
UI-компоненты для Pygame интерфейса
"""
import pygame
import os
from datetime import datetime

class ColorScheme:
    """Цветовые схемы для интерфейса"""
    # Основные цвета Scooby-Doo
    SCOOBY_GREEN = (0, 107, 61)        # #006B3D
    SCOOBY_RED = (156, 26, 28)         # #9C1A1C
    SCOOBY_PURPLE = (75, 0, 130)       # #4B0082
    SCOOBY_ORANGE = (255, 140, 0)      # #FF8C00
    
    # Цвета для кнопок
    BUTTON_NORMAL = (76, 175, 80)      # #4CAF50
    BUTTON_HOVER = (56, 142, 60)       # #388E3C
    BUTTON_CLICK = (27, 94, 32)        # #1B5E20
    BUTTON_DISABLED = (158, 158, 158)  # #9E9E9E
    
    # Цвета для админ панели
    ADMIN_BG = (46, 46, 46)            # #2E2E2E
    ADMIN_PANEL = (60, 60, 60)         # #3C3C3C
    ADMIN_TEXT = (255, 255, 255)       # #FFFFFF
    ADMIN_TEXT_SECONDARY = (204, 204, 204)  # #CCCCCC
    
    # Цвета для панели воспитателя
    TEACHER_BG = (245, 245, 245)       # #F5F5F5
    TEACHER_CARD = (255, 255, 255)     # #FFFFFF
    TEACHER_SUCCESS = (76, 175, 80)    # #4CAF50
    TEACHER_WARNING = (255, 152, 0)    # #FF9800
    TEACHER_INFO = (33, 150, 243)      # #2196F3
    
    # Цвета для игры ребёнка
    CHILD_BG = (240, 248, 255)         # #F0F8FF
    CHILD_PRIMARY = (255, 105, 180)    # #FF69B4
    CHILD_SECONDARY = (64, 224, 208)   # #40E0D0

class Button:
    """Кнопка с анимацией наведения (один шрифт)"""
    def __init__(self, x, y, width, height, text="", 
                 color_normal=None, color_hover=None, 
                 color_click=None, font_size=24, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_normal = color_normal or ColorScheme.BUTTON_NORMAL
        self.color_hover = color_hover or ColorScheme.BUTTON_HOVER
        self.color_click = color_click or ColorScheme.BUTTON_CLICK
        self.current_color = self.color_normal
        self.font_size = font_size
        self.font = font if font else pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_clicked = False
        self.enabled = True
        self.border_radius = 10
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, 
                        border_radius=self.border_radius)
        if self.is_hovered and self.enabled:
            shadow = pygame.Rect(self.rect.x, self.rect.y + 3, 
                               self.rect.width, self.rect.height)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow, 
                           border_radius=self.border_radius)
        if self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
    
    def update(self, mouse_pos, mouse_click):
        self.is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        if not self.enabled:
            self.current_color = ColorScheme.BUTTON_DISABLED
        elif self.is_hovered:
            if mouse_click:
                self.current_color = self.color_click
                self.is_clicked = True
                return True
            else:
                self.current_color = self.color_hover
                self.is_clicked = False
        else:
            self.current_color = self.color_normal
            self.is_clicked = False
        return False
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.current_color = ColorScheme.BUTTON_DISABLED

class InputBox:
    """Поле ввода текста с курсором и позиционированием"""
    def __init__(self, x, y, width, height, 
                 placeholder="", is_password=False, font_size=28, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.is_password = is_password
        self.font_size = font_size
        self.font = font if font else pygame.font.Font(None, font_size)
        self.active = False
        self.color_inactive = (200, 200, 200)
        self.color_active = ColorScheme.SCOOBY_PURPLE
        self.color = self.color_inactive
        self.cursor_pos = 0          # позиция курсора в строке
        self.cursor_visible = True
        self.cursor_timer = 0
        self.visible_text = not is_password  # если пароль – скрыт по умолчанию

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
                # Установка курсора по клику
                rel_x = event.pos[0] - self.rect.x - 10
                self.cursor_pos = self._estimate_cursor_pos(rel_x)
            else:
                self.active = False
                self.color = self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                try:
                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8')
                    self.text = self.text[:self.cursor_pos] + clipboard + self.text[self.cursor_pos:]
                    self.cursor_pos += len(clipboard)
                except:
                    pass
            else:
                if len(self.text) < 200:
                    char = event.unicode
                    if char.isprintable():
                        self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                        self.cursor_pos += 1
        return False

    def _estimate_cursor_pos(self, rel_x):
        """Примерное определение символа по координате X"""
        if not self.text:
            return 0
        # Для моноширинного шрифта можно делить на среднюю ширину символа
        # Здесь используем размер шрифта / 1.5 как грубую оценку
        char_width = self.font.size("A")[0]  # ширина заглавной буквы
        if char_width == 0:
            char_width = self.font_size // 2
        pos = int(rel_x / char_width)
        return max(0, min(pos, len(self.text)))

    def update(self):
        self.cursor_timer = (self.cursor_timer + 1) % 60
        self.cursor_visible = self.cursor_timer < 30

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)

        # Формируем отображаемый текст с учётом видимости и курсора
        if self.is_password and not self.visible_text:
            display_text = "•" * len(self.text)
        else:
            display_text = self.text

        # Вставляем курсор в позицию, если поле активно и мигание включено
        if self.active and self.cursor_visible:
            if self.cursor_pos <= len(display_text):
                display_text = display_text[:self.cursor_pos] + "|" + display_text[self.cursor_pos:]
            else:
                display_text += "|"

        # Рендеринг
        if display_text:
            text_surf = self.font.render(display_text, True, (0, 0, 0))
            screen.blit(text_surf, (self.rect.x + 10, self.rect.centery - text_surf.get_height() // 2))
        elif self.placeholder:
            # Если текст пустой – показываем placeholder
            placeholder_surf = self.font.render(self.placeholder, True, (150, 150, 150))
            screen.blit(placeholder_surf, (self.rect.x + 10, self.rect.centery - placeholder_surf.get_height() // 2))

    def get_text(self):
        return self.text

    def clear(self):
        self.text = ""
        self.cursor_pos = 0

class Table:
    """Таблица с данными (пропорциональные ширины колонок)"""
    def __init__(self, x, y, width, height, headers, 
                 row_height=40, font_size=20, col_widths=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.headers = headers
        self.row_height = row_height
        self.font_size = font_size
        self.data = []
        self.scroll_offset = 0
        self.max_visible_rows = height // row_height - 1
        self.selected_row = -1
        self.col_widths = col_widths
        
    def set_data(self, data):
        self.data = data
        self.scroll_offset = 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        font = pygame.font.Font(None, self.font_size)
        header_height = self.row_height
        
        if self.col_widths:
            total_weight = sum(self.col_widths)
            col_widths_px = [int(self.rect.width * w / total_weight) for w in self.col_widths]
        else:
            col_widths_px = [self.rect.width // len(self.headers)] * len(self.headers)
            remainder = self.rect.width - sum(col_widths_px)
            if remainder > 0 and len(col_widths_px) > 0:
                col_widths_px[-1] += remainder
        
        x_pos = self.rect.x
        for i, header in enumerate(self.headers):
            header_rect = pygame.Rect(x_pos, self.rect.y, col_widths_px[i], header_height)
            pygame.draw.rect(screen, ColorScheme.SCOOBY_GREEN, header_rect)
            pygame.draw.rect(screen, (150, 150, 150), header_rect, 1)
            text_surf = self._render_text(header, col_widths_px[i] - 10, font, (255,255,255))
            screen.blit(text_surf, (header_rect.x + 5, header_rect.centery - text_surf.get_height() // 2))
            x_pos += col_widths_px[i]
        
        start_row = self.scroll_offset
        end_row = min(start_row + self.max_visible_rows, len(self.data))
        for row_idx in range(start_row, end_row):
            row_data = self.data[row_idx]
            row_y = self.rect.y + header_height + (row_idx - start_row) * self.row_height
            if row_idx == self.selected_row:
                pygame.draw.rect(screen, (220, 240, 255),
                                 (self.rect.x, row_y, self.rect.width, self.row_height))
            x_pos = self.rect.x
            for col_idx in range(len(self.headers)):
                cell_rect = pygame.Rect(x_pos, row_y, col_widths_px[col_idx], self.row_height)
                pygame.draw.rect(screen, (240, 240, 240), cell_rect)
                pygame.draw.rect(screen, (200, 200, 200), cell_rect, 1)
                cell_text = str(row_data[col_idx]) if col_idx < len(row_data) else ""
                text_surf = self._render_text(cell_text, col_widths_px[col_idx] - 10, font, (0,0,0))
                screen.blit(text_surf, (cell_rect.x + 5, cell_rect.centery - text_surf.get_height() // 2))
                x_pos += col_widths_px[col_idx]
    
    def _render_text(self, text, max_width, font, color):
        if font.size(text)[0] <= max_width:
            return font.render(text, True, color)
        while font.size(text + "…")[0] > max_width and len(text) > 0:
            text = text[:-1]
        return font.render(text + "…", True, color)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                rel_y = mouse_pos[1] - self.rect.y - self.row_height
                row_idx = rel_y // self.row_height + self.scroll_offset
                if 0 <= row_idx < len(self.data):
                    self.selected_row = row_idx
                    return self.data[row_idx]
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, min(
                    len(self.data) - self.max_visible_rows,
                    self.scroll_offset - event.y
                ))
        return None

class ModalWindow:
    """Модальное окно"""
    def __init__(self, width, height, title=""):
        self.width = width
        self.height = height
        self.title = title
        self.buttons = []
        self.inputs = []
        self.visible = False
        self.callback = None
        
    def show(self, screen):
        if not self.visible:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        window_rect = pygame.Rect(
            (screen.get_width() - self.width) // 2,
            (screen.get_height() - self.height) // 2,
            self.width, self.height
        )
        pygame.draw.rect(screen, (255, 255, 255), window_rect, border_radius=15)
        pygame.draw.rect(screen, ColorScheme.SCOOBY_PURPLE, window_rect, 3, border_radius=15)
        if self.title:
            font = pygame.font.Font(None, 32)
            title_surf = font.render(self.title, True, ColorScheme.SCOOBY_PURPLE)
            title_rect = title_surf.get_rect(center=(window_rect.centerx, window_rect.y + 30))
            screen.blit(title_surf, title_rect)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        if self.buttons:
            button_width = 120
            button_height = 40
            spacing = 20
            total_buttons = len(self.buttons)
            total_buttons_width = total_buttons * button_width + (total_buttons - 1) * spacing
            start_x = window_rect.x + (self.width - total_buttons_width) // 2
            y = window_rect.y + self.height - 80
            for i, button in enumerate(self.buttons):
                bx = start_x + i * (button_width + spacing)
                button.rect.topleft = (bx, y)
                if button.update(mouse_pos, mouse_click):
                    if self.callback:
                        self.callback(button.text)
                    self.visible = False
                button.draw(screen)
        for i, input_box in enumerate(self.inputs):
            input_width = 300
            input_height = 40
            ix = window_rect.x + (self.width - input_width) // 2
            iy = window_rect.y + 100 + i * 60
            input_box.rect.topleft = (ix, iy)
            input_box.draw(screen)
    
    def add_button(self, text, action=None):
        button = Button(0, 0, 120, 40, text)
        if action:
            button.callback = action
        self.buttons.append(button)
    
    def add_input(self, placeholder="", is_password=False):
        input_box = InputBox(0, 0, 300, 40, placeholder, is_password)
        self.inputs.append(input_box)
        return input_box

class ProgressBar:
    """Индикатор прогресса"""
    def __init__(self, x, y, width, height, max_value=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = 0
        self.max_value = max_value
        self.border_radius = height // 2
        
    def set_value(self, value):
        self.value = max(0, min(value, self.max_value))
    
    def draw(self, screen):
        pygame.draw.rect(screen, (230, 230, 230), self.rect, border_radius=self.border_radius)
        fill_width = int((self.value / self.max_value) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        if self.value < 30:
            color = (244, 67, 54)
        elif self.value < 70:
            color = (255, 152, 0)
        else:
            color = (76, 175, 80)
        pygame.draw.rect(screen, color, fill_rect, border_radius=self.border_radius)
        font = pygame.font.Font(None, 20)
        percent = int((self.value / self.max_value) * 100)
        text_surf = font.render(f"{percent}%", True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        pygame.draw.rect(screen, (180, 180, 180), self.rect, 2, border_radius=self.border_radius)

class ToastMessage:
    """Всплывающее уведомление"""
    def __init__(self):
        self.messages = []
        self.duration = 3000
        
    def add(self, text, message_type="info"):
        self.messages.append({
            'text': text,
            'type': message_type,
            'time': pygame.time.get_ticks()
        })
    
    def update(self):
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages 
                         if current_time - msg['time'] < self.duration]
    
    def draw(self, screen):
        for i, msg in enumerate(self.messages):
            y = screen.get_height() - 100 - i * 60
            if msg['type'] == 'success':
                color = (76, 175, 80)
            elif msg['type'] == 'error':
                color = (244, 67, 54)
            elif msg['type'] == 'warning':
                color = (255, 152, 0)
            else:
                color = (33, 150, 243)
            font = pygame.font.Font(None, 24)
            text_surf = font.render(msg['text'], True, (255, 255, 255))
            rect_width = text_surf.get_width() + 40
            rect_height = 40
            rect = pygame.Rect((screen.get_width() - rect_width) // 2, y, rect_width, rect_height)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
            screen.blit(text_surf, (rect.x + 20, rect.centery - text_surf.get_height() // 2))

class LoadingSpinner:
    """Индикатор загрузки"""
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0
        self.speed = 5
    
    def update(self):
        self.angle = (self.angle + self.speed) % 360
    
    def draw(self, screen):
        points = []
        for i in range(8):
            angle = self.angle + i * 45
            radius = self.size // 2 * (0.5 + (i % 2) * 0.5)
            x = self.x + radius * pygame.math.Vector2(1, 0).rotate(angle).x
            y = self.y + radius * pygame.math.Vector2(1, 0).rotate(angle).y
            points.append((x, y))
        for i in range(8):
            pygame.draw.line(screen, ColorScheme.SCOOBY_ORANGE, 
                           points[i], points[(i + 1) % 8], 3)