"""
Панель воспитателя
"""
import pygame
import sys
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from database import db_manager
from widgets import *

# ----------------------------------------------------------------------
# НАСТРОЙКИ ПОЧТЫ
# ----------------------------------------------------------------------
SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465
SMTP_USERNAME = "vbabyleva@yandex.ru"
SMTP_PASSWORD = "xvqmzvwkontgpjji"
TEACHER_NAME = "Ваше воспитатель"
# ----------------------------------------------------------------------

class ChildCard:
    def __init__(self, x, y, width, height, child_data, child_index):
        self.rect = pygame.Rect(x, y, width, height)
        self.data = child_data
        self.child_index = child_index
        self.is_hovered = False

    def draw(self, screen, font_small):
        if self.data[7] == 'active':
            border_color = ColorScheme.TEACHER_SUCCESS
        elif self.data[7] == 'paused':
            border_color = ColorScheme.TEACHER_WARNING
        else:
            border_color = (150, 150, 150)

        pygame.draw.rect(screen, ColorScheme.TEACHER_CARD, self.rect, border_radius=10)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)

        if self.is_hovered:
            shadow = pygame.Rect(self.rect.x, self.rect.y + 3,
                                 self.rect.width, self.rect.height)
            pygame.draw.rect(screen, (0, 0, 0, 30), shadow, border_radius=10)

        avatar_rect = pygame.Rect(self.rect.x + 15, self.rect.y + 15, 60, 60)
        avatar_id = self.data[2] if self.data[2] is not None else 0
        avatar_color = [
            (255, 182, 193),
            (173, 216, 230),
            (152, 251, 152),
            (255, 218, 185),
            (221, 160, 221)
        ][avatar_id % 5]
        pygame.draw.circle(screen, avatar_color, avatar_rect.center, 30)

        font = pygame.font.Font(None, 18)
        name = self.data[1]
        if len(name) > 15:
            name = name[:12] + "..."
        name_surf = font.render(name, True, (0, 0, 0))
        screen.blit(name_surf, (self.rect.x + 90, self.rect.y + 20))

        completed = self.data[4] or 0
        total = self.data[5] or 1
        progress = (completed / total) * 100 if total > 0 else 0
        progress_rect = pygame.Rect(self.rect.x + 90, self.rect.y + 45, 150, 8)
        pygame.draw.rect(screen, (230, 230, 230), progress_rect, border_radius=4)
        fill_width = int(progress_rect.width * progress / 100)
        fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, progress_rect.height)
        if progress < 30:
            color = (244, 67, 54)
        elif progress < 70:
            color = (255, 152, 0)
        else:
            color = (76, 175, 80)
        pygame.draw.rect(screen, color, fill_rect, border_radius=4)

        progress_text = f"{completed}/{total} этапов"
        text_surf = font.render(progress_text, True, (100, 100, 100))
        screen.blit(text_surf, (self.rect.x + 250, self.rect.y + 42))

        stage_text = f"Этап: {self.data[3] or 1}"
        stage_surf = font.render(stage_text, True, (0, 0, 0))
        screen.blit(stage_surf, (self.rect.x + 90, self.rect.y + 60))

        if self.data[8]:
            last_active = self.data[8]
            time_text = "Сегодня" if isinstance(last_active, str) else "Недавно"
        else:
            time_text = "Нет активности"
        time_surf = font.render(time_text, True, (150, 150, 150))
        screen.blit(time_surf, (self.rect.x + 200, self.rect.y + 60))

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class TeacherPanel:
    """Панель воспитателя"""

    def __init__(self, screen, user_data):
        self.screen = screen
        self.user = user_data
        self.width, self.height = screen.get_size()
        self.running = True

        self.current_section = "my_group"
        self.selected_child = None
        self.selected_group = None
        self.selected_period = 0

        self.groups = []
        self.children = []
        self.child_cards = []

        self.scroll_offset_mygroup = 0
        self.details_text = ""

        self.modal_window = None
        self.toast = ToastMessage()

        self.load_resources()

        self.search_text = ""

        self.create_widgets()
        self.load_data()

        self.clock = pygame.time.Clock()

        self.reports_tab = 2
        self.selected_report_child_idx = None
        self.report_preview = ""
        self.report_children_scroll_offset = 0

        self.quest_description = ""
        self.quest_stages = []
        self.quest_stages_scroll_offset = 0
        self.quest_stages_loaded = False

    def load_resources(self):
        """Загружаем шрифты с уменьшенным размером"""
        text_font_path = "C:/Windows/Fonts/arial.ttf"
        if os.path.exists(text_font_path):
            self.font_large = pygame.font.Font(text_font_path, 26)
            self.font_medium = pygame.font.Font(text_font_path, 20)
            self.font_small = pygame.font.Font(text_font_path, 16)   # будет для навигации
        else:
            self.font_large = pygame.font.Font(None, 26)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)

    def create_widgets(self):
        nav_width = 180
        nav_height = 45
        nav_x = 20
        nav_y = 100

        # ВСЕ НАВИГАЦИОННЫЕ КНОПКИ ТЕПЕРЬ ИСПОЛЬЗУЮТ font_small
        self.btn_my_group = Button(nav_x, nav_y, nav_width, nav_height,
                                "Моя группа", font=self.font_small)
        self.btn_progress = Button(nav_x, nav_y + 55, nav_width, nav_height,
                                "Прогресс", font=self.font_small)
        self.btn_quest = Button(nav_x, nav_y + 110, nav_width, nav_height,
                                "Текущий квест", font=self.font_small)
        self.btn_reports = Button(nav_x, nav_y + 165, nav_width, nav_height,
                                "Отчёты", font=self.font_small)

        self.btn_logout = Button(self.width - 120, 20, 100, 40, "Выход", font=self.font_medium)

        self.btn_pause_child = Button(0, 0, 180, 40, "Пауза", font=self.font_medium)
        self.btn_reset_progress = Button(0, 0, 180, 40, "Сбросить", font=self.font_medium)
        self.btn_details = Button(0, 0, 180, 40, "Подробнее", font=self.font_medium)

        self.btn_add_child = Button(self.width - 220, self.height - 70,
                                    200, 45, "Добавить ребёнка", font=self.font_medium)

        self.search_input = InputBox(300, 100, 300, 36, "Поиск ребёнка...",
                                    font=self.font_small)

        self.btn_generate_report = Button(self.width - 250, 200, 200, 40,
                                        "Сформировать отчёт", font=self.font_medium)
        self.btn_send_report = Button(self.width - 250, 260, 200, 40,
                                    "Отправить родителю", font=self.font_medium)
        self.btn_send_all = Button(self.width - 250, 320, 200, 40,
                                "Отправить всем", font=self.font_medium)

        self.message_input = InputBox(250, self.height - 180, 600, 40,
                                    "Ваше сообщение к отчёту...", font=self.font_small)

    def load_data(self):
        try:
            self.groups = db_manager.get_user_groups(self.user['id'])
            if self.groups:
                self.selected_group = self.groups[0][1]
                self.load_children(self.selected_group)
        except Exception as e:
            self.toast.add(f"Ошибка загрузки групп: {str(e)}", "error")

    def load_children(self, group_name):
        try:
            self.children = db_manager.get_group_children(group_name, self.user['id'])
            self.selected_child = None
            self.details_text = ""
            self.create_child_cards()
        except Exception as e:
            self.toast.add(f"Ошибка загрузки детей: {str(e)}", "error")

    def create_child_cards(self):
        self.child_cards = []
        card_width = 400
        card_height = 100
        spacing = 10
        start_x = 250
        start_y = 150

        for i, child in enumerate(self.children):
            if self.search_text and self.search_text.lower() not in child[1].lower():
                continue
            y = start_y + i * (card_height + spacing)
            card = ChildCard(start_x, y, card_width, card_height, child, i)
            self.child_cards.append(card)

        self.selected_child = None
        self.details_text = ""
        self.scroll_offset_mygroup = 0

    def get_current_quest_name(self):
        if self.groups and self.selected_group:
            for group in self.groups:
                if group[1] == self.selected_group:
                    return group[3] or "Не назначен"
        return "Не назначен"

    def load_quest_stages(self):
        self.quest_description = ""
        self.quest_stages = []
        quest_name = self.get_current_quest_name()
        if quest_name == "Не назначен":
            return
        quest_id = db_manager.get_quest_id_by_name(quest_name)
        if not quest_id:
            self.toast.add(f"Квест '{quest_name}' не найден в системе", "error")
            return
        desc = db_manager.get_quest_description(quest_id)
        self.quest_description = desc if desc else "Описание отсутствует."
        stages_raw = db_manager.get_quest_stages(quest_id)
        for stage in stages_raw:
            stage_number = stage[0]
            name = stage[1]
            description = stage[2] if len(stage) > 2 else ''
            self.quest_stages.append({
                'number': stage_number,
                'title': name,
                'description': description
            })
        self.quest_stages_loaded = True

    def send_email_report(self, parent_email, child_name, report_text, personal_message=""):
        if not parent_email or "@" not in parent_email:
            self.toast.add(f"Некорректный email родителя для {child_name}", "error")
            return False
        try:
            msg = EmailMessage()
            msg["From"] = SMTP_USERNAME
            msg["To"] = parent_email
            msg["Subject"] = f"Отчёт о прогрессе - {child_name}"
            body = f"Здравствуйте!\n\n{TEACHER_NAME} отправляет вам отчёт о прогрессе вашего ребёнка:\n\n"
            body += report_text + "\n"
            if personal_message.strip():
                body += f"\nЛичное сообщение от воспитателя:\n{personal_message}\n"
            body += "\nС уважением,\nПанель воспитателя"
            msg.set_content(body, "plain", charset="utf-8")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n=== ОШИБКА АУТЕНТИФИКАЦИИ ===\n{e}\n==============================\n")
            self.toast.add("Ошибка аутентификации почты! Проверьте логин/пароль.", "error")
        except smtplib.SMTPException as e:
            self.toast.add(f"Почтовая ошибка: {str(e)}", "error")
        except Exception as e:
            self.toast.add(f"Не удалось отправить письмо: {str(e)}", "error")
        return False

    def show_add_child_modal(self):
        """Модальное окно с полем пароля"""
        self.modal_window = ModalWindow(520, 460, "Добавить ребёнка")
        self.modal_window.add_input("Полное имя")
        self.modal_window.add_input("Пароль", is_password=True)
        self.modal_window.add_input("Email родителя (необязательно)")
        self.modal_window.add_button("Отмена")
        self.modal_window.add_button("Создать")
        self.modal_window.visible = True
        self.modal_window.callback = self.handle_child_modal

    def handle_child_modal(self, button_text):
        if button_text == "Создать":
            full_name = self.modal_window.inputs[0].get_text().strip()
            password = self.modal_window.inputs[1].get_text()
            parent_email = self.modal_window.inputs[2].get_text().strip()
            if not full_name:
                self.toast.add("Имя обязательно", "error")
                return
            if not password:
                self.toast.add("Пароль обязателен", "error")
                return
            group_name = self.selected_group
            if not group_name:
                self.toast.add("Группа не выбрана", "error")
                return
            success, msg = db_manager.create_child(full_name, group_name,
                                                   password=password,
                                                   parent_email=parent_email if parent_email else None)
            if success:
                self.toast.add(f"Ребёнок '{full_name}' добавлен (login: {msg})", "success")
                self.load_children(group_name)
                self.modal_window.visible = False
                # Очищаем поля
                for inp in self.modal_window.inputs:
                    inp.clear()
            else:
                self.toast.add(f"Ошибка: {msg}", "error")

    def fit_text(self, text, font, max_width, color, base_size=None):
        """Уменьшает размер шрифта, чтобы текст поместился в max_width, минимум 10 pt."""
        if base_size is None:
            size = font.get_height()
        else:
            size = base_size
        while size > 10:
            try:
                if hasattr(font, 'name') and font.name:
                    current_font = pygame.font.Font(font.name, size)
                else:
                    current_font = pygame.font.Font(None, size)
            except:
                current_font = pygame.font.Font(None, size)
            if current_font.size(text)[0] <= max_width:
                return current_font.render(text, True, color)
            size -= 1
        return pygame.font.Font(None, 10).render(text, True, color)

    def draw_navigation(self):
        nav_rect = pygame.Rect(0, 0, 230, self.height)
        pygame.draw.rect(self.screen, ColorScheme.SCOOBY_GREEN, nav_rect)
    
        # Заголовок с автоподбором, чтобы влез в ширину панели
        title_text = "Панель воспитателя"
        max_text_width = nav_rect.width - 30  # отступы по 15 px с каждой стороны
        title_surf = self.fit_text(title_text, self.font_large, max_text_width, (255, 255, 255), base_size=26)
        self.screen.blit(title_surf, (15, 20))
    
        # Имя воспитателя (уже было с автоподбором)
        user_text = f"{self.user['full_name']}"
        info_surf = self.fit_text(user_text, self.font_small, max_text_width, (255, 255, 255), base_size=16)
        self.screen.blit(info_surf, (15, 70))
    
        self.btn_my_group.draw(self.screen)
        self.btn_progress.draw(self.screen)
        self.btn_quest.draw(self.screen)
        self.btn_reports.draw(self.screen)

    def draw_my_group(self):
        if self.selected_group:
            title_text = f"Группа: {self.selected_group}"
            active_children = len([c for c in self.children if c[7] == 'active'])
            stats_text = f"Дети: {len(self.children)} | Активные: {active_children}"
        else:
            title_text = "Выберите группу"
            stats_text = ""
        title = self.font_large.render(title_text, True, (0, 0, 0))
        stats = self.font_medium.render(stats_text, True, (100, 100, 100))
        self.screen.blit(title, (250, 30))
        self.screen.blit(stats, (250, 70))
        self.search_input.draw(self.screen)

        list_rect = pygame.Rect(250, 140, 420, self.height - 230)
        pygame.draw.rect(self.screen, (240, 240, 240), list_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 180), list_rect, 1, border_radius=8)

        self.screen.set_clip(list_rect)
        mouse_pos = pygame.mouse.get_pos()
        for card in self.child_cards:
            original_y = card.rect.y
            card.rect.y -= self.scroll_offset_mygroup
            card.update(mouse_pos)
            if card.rect.colliderect(list_rect):
                card.draw(self.screen, self.font_small)
            card.rect.y = original_y
        self.screen.set_clip(None)

        total_height = len(self.child_cards) * 110
        if total_height > list_rect.height:
            bar_height = max(20, list_rect.height * list_rect.height / total_height)
            bar_y = list_rect.y + (self.scroll_offset_mygroup / max(1, total_height - list_rect.height)) * (list_rect.height - bar_height)
            pygame.draw.rect(self.screen, (150, 150, 150), (list_rect.right - 10, bar_y, 8, bar_height), border_radius=3)

        # Теперь кнопка уже в create_widgets позиционирована внизу справа
        self.btn_add_child.draw(self.screen)

        if self.selected_child is not None and self.selected_child < len(self.children):
            child = self.children[self.selected_child]
            panel_x = 690
            panel_y = 140
            panel_width = 280
            panel_height = 300 if not self.details_text else 480
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, border_radius=10)
            pygame.draw.rect(self.screen, ColorScheme.SCOOBY_ORANGE, panel_rect, 2, border_radius=10)

            name_surf = self.font_medium.render(child[1], True, (0, 0, 0))
            self.screen.blit(name_surf, (panel_x + 10, panel_y + 15))

            completed = child[4] or 0
            total = child[5] or 1
            progress = (completed / total) * 100 if total > 0 else 0
            progress_text = f"Прогресс: {completed}/{total} ({progress:.0f}%)"
            prog_surf = self.font_small.render(progress_text, True, (50, 50, 50))
            self.screen.blit(prog_surf, (panel_x + 10, panel_y + 45))

            stage_text = f"Текущий этап: {child[3] or 1}"
            stage_surf = self.font_small.render(stage_text, True, (50, 50, 50))
            self.screen.blit(stage_surf, (panel_x + 10, panel_y + 70))

            score_text = f"Баллы: {child[6] or 0:.1f}"
            score_surf = self.font_small.render(score_text, True, (50, 50, 50))
            self.screen.blit(score_surf, (panel_x + 10, panel_y + 95))

            status = child[7]
            status_color = ColorScheme.TEACHER_SUCCESS if status == 'active' else ColorScheme.TEACHER_WARNING if status == 'paused' else (150,150,150)
            pygame.draw.circle(self.screen, status_color, (panel_x + 15, panel_y + 125), 8)
            status_text = "Активен" if status == 'active' else "На паузе" if status == 'paused' else "Неактивен"
            status_surf = self.font_small.render(status_text, True, (0, 0, 0))
            self.screen.blit(status_surf, (panel_x + 30, panel_y + 118))

            self.btn_pause_child.rect.topleft = (panel_x + 10, panel_y + 150)
            self.btn_reset_progress.rect.topleft = (panel_x + 10, panel_y + 200)
            self.btn_details.rect.topleft = (panel_x + 10, panel_y + 250)

            self.btn_pause_child.draw(self.screen)
            self.btn_reset_progress.draw(self.screen)
            self.btn_details.draw(self.screen)

            if self.details_text:
                detail_y = panel_y + 300
                detail_rect = pygame.Rect(panel_x + 10, detail_y, panel_width - 20, 160)
                pygame.draw.rect(self.screen, (245, 245, 245), detail_rect, border_radius=5)
                pygame.draw.rect(self.screen, (200, 200, 200), detail_rect, 1, border_radius=5)
                lines = self.details_text.split('\n')
                line_y = detail_y + 10
                for line in lines:
                    line_surf = self.font_small.render(line, True, (0, 0, 0))
                    self.screen.blit(line_surf, (panel_x + 20, line_y))
                    line_y += 22

    def draw_progress_section(self):
        title = self.font_large.render("Мониторинг прогресса", True, (0, 0, 0))
        self.screen.blit(title, (250, 30))
        periods = ["Неделя", "Месяц", "Весь квест"]
        for i, period in enumerate(periods):
            btn_rect = pygame.Rect(250 + i * 110, 100, 100, 40)
            color = ColorScheme.SCOOBY_GREEN if i == self.selected_period else (200, 200, 200)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), btn_rect, 1, border_radius=5)
            text = self.font_small.render(period, True, (255, 255, 255) if i == self.selected_period else (50, 50, 50))
            self.screen.blit(text, text.get_rect(center=btn_rect.center))
        period_name = periods[self.selected_period]
        if self.children:
            total_progress = sum(c[4] or 0 for c in self.children)
            total_stages = sum(c[5] or 1 for c in self.children)
            avg_progress = (total_progress / total_stages * 100) if total_stages > 0 else 0
            text_surf = self.font_medium.render(
                f"Прогресс группы за {period_name.lower()}: {avg_progress:.1f}%",
                True, (0, 0, 0))
            self.screen.blit(text_surf, (250, 160))
            progress_bar = ProgressBar(250, 200, 500, 30, 100)
            progress_bar.set_value(avg_progress)
            progress_bar.draw(self.screen)
        headers = ["Имя", "Прогресс", "Этап", "Баллы", "Статус"]
        table_data = []
        for child in self.children:
            completed = child[4] or 0
            total = child[5] or 1
            progress = (completed / total * 100) if total > 0 else 0
            table_data.append([
                child[1],
                f"{progress:.0f}%",
                f"{child[3] or 1}/{total}",
                f"{child[6] or 0:.1f}",
                "Активен" if child[7] == 'active' else "Пауза"
            ])
        table = Table(250, 250, 700, 300, headers)
        table.set_data(table_data)
        table.draw(self.screen)

    def draw_quest_section(self):
        title = self.font_large.render("Текущий квест", True, (0, 0, 0))
        self.screen.blit(title, (250, 30))
        quest_name = self.get_current_quest_name()
        quest_surf = self.font_medium.render(f"Квест: {quest_name}", True, (0, 0, 0))
        self.screen.blit(quest_surf, (250, 90))
        if not self.quest_stages_loaded:
            self.load_quest_stages()
        if quest_name == "Не назначен":
            no_quest = self.font_medium.render("Квест не назначен.", True, (100,100,100))
            self.screen.blit(no_quest, (280, 150))
            return
        if not self.quest_description and not self.quest_stages:
            empty_surf = self.font_medium.render("Нет данных по квесту.", True, (100,100,100))
            self.screen.blit(empty_surf, (280, 150))
            return
        content_rect = pygame.Rect(280, 140, self.width - 300, self.height - 200)
        pygame.draw.rect(self.screen, (245,245,245), content_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180,180,180), content_rect, 1, border_radius=8)

        desc_y = content_rect.y + 10
        desc_surf = self.font_medium.render("Описание:", True, ColorScheme.SCOOBY_GREEN)
        self.screen.blit(desc_surf, (content_rect.x + 10, desc_y))
        desc_y += 30
        words = self.quest_description.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.font_small.size(test_line)[0] < content_rect.width - 20:
                line = test_line
            else:
                text_surf = self.font_small.render(line, True, (0,0,0))
                self.screen.blit(text_surf, (content_rect.x + 10, desc_y))
                desc_y += 25
                line = word + " "
        if line:
            text_surf = self.font_small.render(line, True, (0,0,0))
            self.screen.blit(text_surf, (content_rect.x + 10, desc_y))
            desc_y += 25
        desc_y += 10
        stage_title = self.font_medium.render("Задания:", True, ColorScheme.SCOOBY_GREEN)
        self.screen.blit(stage_title, (content_rect.x + 10, desc_y))
        desc_y += 35

        row_height = 60
        total_stages = len(self.quest_stages)
        max_scroll = max(0, total_stages * row_height - (content_rect.height - (desc_y - content_rect.y)))
        self.quest_stages_scroll_offset = max(0, min(self.quest_stages_scroll_offset, max_scroll))

        for idx, stage in enumerate(self.quest_stages):
            y_pos = desc_y + idx * row_height - self.quest_stages_scroll_offset
            if y_pos + row_height < content_rect.y + 30 or y_pos > content_rect.y + content_rect.height:
                continue
            stage_rect = pygame.Rect(content_rect.x + 5, y_pos, content_rect.width - 10, row_height - 4)
            pygame.draw.rect(self.screen, (255,255,255), stage_rect, border_radius=5)
            pygame.draw.rect(self.screen, ColorScheme.SCOOBY_GREEN, stage_rect, 1, border_radius=5)
            stage_num = str(stage['number'])
            title_text = f"{stage_num}. {stage['title']}"
            title_surf = self.font_small.render(title_text, True, (0,0,0))
            self.screen.blit(title_surf, (stage_rect.x + 10, stage_rect.y + 5))
            if stage['description']:
                desc_text = stage['description'][:80]
                desc_surf = self.font_small.render(desc_text, True, (80,80,80))
                self.screen.blit(desc_surf, (stage_rect.x + 10, stage_rect.y + 25))

        btn_refresh_rect = pygame.Rect(280, self.height - 50, 150, 35)
        pygame.draw.rect(self.screen, ColorScheme.SCOOBY_ORANGE, btn_refresh_rect, border_radius=5)
        refresh_text = self.font_medium.render("Обновить", True, (255,255,255))
        self.screen.blit(refresh_text, refresh_text.get_rect(center=btn_refresh_rect.center))

    def draw_reports_section(self):
        title = self.font_large.render("Отчёты и статистика", True, (0, 0, 0))
        self.screen.blit(title, (250, 30))
        tabs = ["Сводный", "Индивидуальный", "Для родителей"]
        for i, tab in enumerate(tabs):
            tab_rect = pygame.Rect(250 + i * 150, 90, 150, 40)
            color = ColorScheme.SCOOBY_GREEN if i == self.reports_tab else (200, 200, 200)
            pygame.draw.rect(self.screen, color, tab_rect, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), tab_rect, 1, border_radius=5)
            text = self.font_small.render(tab, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=tab_rect.center))

        if self.reports_tab == 0:
            if self.children:
                total = len(self.children)
                active = len([c for c in self.children if c[7] == 'active'])
                paused = total - active
                total_points = sum(c[6] or 0 for c in self.children)
                avg_points = total_points / total if total > 0 else 0
                lines = [
                    f"Всего детей: {total}",
                    f"Активных: {active}",
                    f"На паузе: {paused}",
                    f"Средний балл: {avg_points:.1f}",
                    f"Квест: {self.get_current_quest_name()}"
                ]
                y = 150
                for line in lines:
                    surf = self.font_medium.render(line, True, (0, 0, 0))
                    self.screen.blit(surf, (280, y))
                    y += 35
            else:
                self.screen.blit(self.font_medium.render("Нет данных по группе", True, (100,100,100)), (280, 150))
            headers = ["Имя", "Прогресс", "Статус"]
            table_data = []
            for child in self.children:
                cmpl = child[4] or 0
                total_st = child[5] or 1
                prg = (cmpl / total_st * 100) if total_st > 0 else 0
                table_data.append([child[1], f"{prg:.0f}%", "Активен" if child[7]=='active' else "Пауза"])
            table = Table(250, 320, 500, 250, headers)
            table.set_data(table_data)
            table.draw(self.screen)

        elif self.reports_tab == 1:
            list_rect = pygame.Rect(280, 150, 200, self.height - 250)
            pygame.draw.rect(self.screen, (240, 240, 240), list_rect, border_radius=5)
            row_y = list_rect.y + 10
            for idx, child in enumerate(self.children):
                if idx == self.selected_report_child_idx:
                    hl_rect = pygame.Rect(list_rect.x+5, row_y-2, list_rect.w-10, 22)
                    pygame.draw.rect(self.screen, (173,216,230), hl_rect, border_radius=3)
                name_surf = self.font_small.render(child[1], True, (0,0,0))
                self.screen.blit(name_surf, (list_rect.x+10, row_y))
                row_y += 25
            if self.selected_report_child_idx is not None:
                child = self.children[self.selected_report_child_idx]
                detail_x = 520
                y = 160
                lines = [
                    f"Имя: {child[1]}",
                    f"Прогресс: {child[4] or 0}/{child[5] or 1}",
                    f"Баллы: {child[6] or 0}",
                    f"Этап: {child[3] or 1}",
                    f"Статус: {child[7]}"
                ]
                for line in lines:
                    surf = self.font_medium.render(line, True, (0,0,0))
                    self.screen.blit(surf, (detail_x, y))
                    y += 35

        elif self.reports_tab == 2:
            list_rect = pygame.Rect(280, 160, 220, 240)
            pygame.draw.rect(self.screen, (245,245,245), list_rect, border_radius=5)
            pygame.draw.rect(self.screen, (180,180,180), list_rect, 1, border_radius=5)
            row_height = 25
            total_children = len(self.children)
            max_scroll = max(0, total_children * row_height - list_rect.height)
            for idx, child in enumerate(self.children):
                y_pos = list_rect.y + 5 + idx * row_height - self.report_children_scroll_offset
                if list_rect.y <= y_pos < list_rect.y + list_rect.height - row_height:
                    if idx == self.selected_report_child_idx:
                        hl_rect = pygame.Rect(list_rect.x+5, y_pos-2, list_rect.w-10, row_height)
                        pygame.draw.rect(self.screen, (173,216,230), hl_rect, border_radius=3)
                    name_surf = self.font_small.render(child[1], True, (0,0,0))
                    self.screen.blit(name_surf, (list_rect.x+8, y_pos+2))
            if total_children > 0 and max_scroll > 0:
                visible_rows = list_rect.height // row_height
                if total_children > visible_rows:
                    bar_x = list_rect.right - 10
                    bar_h = max(20, list_rect.height * list_rect.height // (total_children * row_height))
                    bar_y = list_rect.y + (self.report_children_scroll_offset / max_scroll) * (list_rect.height - bar_h)
                    pygame.draw.rect(self.screen, (150,150,150), (bar_x, bar_y, 8, bar_h), border_radius=3)
            if self.selected_report_child_idx is not None:
                child = self.children[self.selected_report_child_idx]
                detail_x = 530
                y = 170
                info_rect = pygame.Rect(detail_x, y-10, 400, 120)
                pygame.draw.rect(self.screen, (255,255,255), info_rect, border_radius=8)
                pygame.draw.rect(self.screen, (150,150,150), info_rect, 1, border_radius=8)
                lines = [
                    f"Имя: {child[1]}",
                    f"Прогресс: {child[4] or 0}/{child[5] or 1}",
                    f"Баллы: {child[6] or 0}",
                    f"Этап: {child[3] or 1}",
                    f"Статус: {child[7]}"
                ]
                for line in lines:
                    surf = self.font_small.render(line, True, (0,0,0))
                    self.screen.blit(surf, (info_rect.x+15, y))
                    y += 22
                self.btn_generate_report.draw(self.screen)
                self.btn_send_report.draw(self.screen)
                self.btn_send_all.draw(self.screen)
                if self.report_preview:
                    preview_y = 380
                    preview_rect = pygame.Rect(detail_x, preview_y, 400, 150)
                    pygame.draw.rect(self.screen, (255,255,240), preview_rect, border_radius=5)
                    pygame.draw.rect(self.screen, (0,0,0), preview_rect, 1, border_radius=5)
                    line_y = preview_rect.y + 5
                    for line in self.report_preview.split('\n'):
                        surf = self.font_small.render(line, True, (50,50,50))
                        self.screen.blit(surf, (preview_rect.x+10, line_y))
                        line_y += 20
            self.message_input.rect.x = 280
            self.message_input.rect.y = self.height - 180
            self.message_input.width = 500
            self.message_input.draw(self.screen)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.modal_window and self.modal_window.visible:
                for input_box in self.modal_window.inputs:
                    input_box.handle_event(event)
                continue

            self.search_input.handle_event(event)
            new_search = self.search_input.get_text()
            if new_search != self.search_text:
                self.search_text = new_search
                self.create_child_cards()

            if self.current_section == "reports" and self.reports_tab == 2:
                self.message_input.handle_event(event)

            if event.type == pygame.MOUSEWHEEL:
                if self.current_section == "reports" and self.reports_tab == 2:
                    list_rect = pygame.Rect(280, 160, 220, 240)
                    if list_rect.collidepoint(mouse_pos):
                        self.report_children_scroll_offset -= event.y * 20
                        total_children = len(self.children)
                        row_height = 25
                        max_scroll = max(0, total_children * row_height - list_rect.height)
                        self.report_children_scroll_offset = max(0, min(self.report_children_scroll_offset, max_scroll))
                elif self.current_section == "my_group":
                    list_rect = pygame.Rect(250, 140, 420, self.height - 230)
                    if list_rect.collidepoint(mouse_pos):
                        self.scroll_offset_mygroup -= event.y * 30
                        total_height = len(self.child_cards) * 110
                        max_scroll = max(0, total_height - list_rect.height)
                        self.scroll_offset_mygroup = max(0, min(self.scroll_offset_mygroup, max_scroll))
                elif self.current_section == "quest":
                    content_rect = pygame.Rect(280, 140, self.width - 300, self.height - 200)
                    if content_rect.collidepoint(mouse_pos):
                        self.quest_stages_scroll_offset -= event.y * 30
                        total_stages = len(self.quest_stages)
                        row_height = 60
                        max_scroll = max(0, total_stages * row_height - (content_rect.height - 120))
                        self.quest_stages_scroll_offset = max(0, min(self.quest_stages_scroll_offset, max_scroll))

            if self.btn_my_group.update(mouse_pos, mouse_click):
                self.current_section = "my_group"
            if self.btn_progress.update(mouse_pos, mouse_click):
                self.current_section = "progress"
            if self.btn_quest.update(mouse_pos, mouse_click):
                self.current_section = "quest"
                self.quest_stages_loaded = False
                self.quest_stages_scroll_offset = 0
            if self.btn_reports.update(mouse_pos, mouse_click):
                self.current_section = "reports"
                self.report_children_scroll_offset = 0

            if self.btn_logout.update(mouse_pos, mouse_click):
                self.running = False
                return "logout"

            if self.btn_add_child.update(mouse_pos, mouse_click):
                self.show_add_child_modal()

            if self.current_section == "progress" and event.type == pygame.MOUSEBUTTONDOWN:
                periods = ["Неделя", "Месяц", "Весь квест"]
                for i in range(3):
                    btn_rect = pygame.Rect(250 + i * 110, 100, 100, 40)
                    if btn_rect.collidepoint(event.pos):
                        self.selected_period = i
                        break

            if self.current_section == "my_group" and event.type == pygame.MOUSEBUTTONDOWN:
                card_clicked = False
                for card in self.child_cards:
                    adjusted_rect = card.rect.move(0, -self.scroll_offset_mygroup)
                    if adjusted_rect.collidepoint(event.pos):
                        self.selected_child = card.child_index
                        self.details_text = ""
                        card_clicked = True
                        break
                if not card_clicked:
                    panel_rect = pygame.Rect(690, 140, 280, 300 if not self.details_text else 480)
                    if not (self.btn_pause_child.rect.collidepoint(event.pos) or
                            self.btn_reset_progress.rect.collidepoint(event.pos) or
                            self.btn_details.rect.collidepoint(event.pos) or
                            self.btn_add_child.rect.collidepoint(event.pos) or
                            panel_rect.collidepoint(event.pos)):
                        self.selected_child = None
                        self.details_text = ""

            if self.selected_child is not None and self.selected_child < len(self.children):
                child = self.children[self.selected_child]
                child_id = child[0]

                if self.btn_pause_child.update(mouse_pos, mouse_click):
                    current_status = child[7]
                    new_status = 'paused' if current_status == 'active' else 'active'
                    if db_manager.update_child_status(child_id, new_status):
                        self.toast.add(f"Статус изменён на {new_status}", "success")
                        self.load_children(self.selected_group)
                    else:
                        self.toast.add("Ошибка изменения статуса", "error")

                if self.btn_reset_progress.update(mouse_pos, mouse_click):
                    if db_manager.reset_child_progress(child_id):
                        self.toast.add("Прогресс сброшен", "warning")
                        self.load_children(self.selected_group)
                    else:
                        self.toast.add("Ошибка сброса прогресса", "error")

                if self.btn_details.update(mouse_pos, mouse_click):
                    if self.details_text:
                        self.details_text = ""
                    else:
                        self.details_text = (
                            f"Прогресс: {child[4] or 0}/{child[5] or 1}\n"
                            f"Баллы: {child[6] or 0}\n"
                            f"Этап: {child[3] or 1}\n"
                            f"Статус: {child[7]}\n"
                            f"Email родителя: {child[9] if len(child) > 9 else 'не указан'}"
                        )

            if self.current_section == "quest" and event.type == pygame.MOUSEBUTTONDOWN:
                btn_refresh_rect = pygame.Rect(280, self.height - 50, 150, 35)
                if btn_refresh_rect.collidepoint(event.pos):
                    self.quest_stages_loaded = False

            if self.current_section == "reports":
                if event.type == pygame.MOUSEBUTTONDOWN and 90 <= mouse_pos[1] <= 130:
                    tab_idx = (mouse_pos[0] - 250) // 150
                    if 0 <= tab_idx < 3:
                        self.reports_tab = tab_idx
                        self.selected_report_child_idx = None
                        self.report_preview = ""
                        self.report_children_scroll_offset = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.reports_tab == 1:
                        list_rect = pygame.Rect(280, 150, 200, self.height - 250)
                        if list_rect.collidepoint(mouse_pos):
                            idx = (mouse_pos[1] - list_rect.y - 10) // 25
                            if 0 <= idx < len(self.children):
                                self.selected_report_child_idx = idx
                    elif self.reports_tab == 2:
                        list_rect = pygame.Rect(280, 160, 220, 240)
                        if list_rect.collidepoint(mouse_pos):
                            rel_y = mouse_pos[1] - list_rect.y - 5 + self.report_children_scroll_offset
                            idx = rel_y // 25
                            if 0 <= idx < len(self.children):
                                self.selected_report_child_idx = int(idx)
                                self.report_preview = ""
                if self.btn_generate_report.update(mouse_pos, mouse_click):
                    if self.selected_report_child_idx is not None and self.reports_tab == 2:
                        child = self.children[self.selected_report_child_idx]
                        completed = child[4] or 0
                        total = child[5] or 1
                        progress = (completed / total * 100) if total > 0 else 0
                        points = child[6] or 0
                        quest_name = self.get_current_quest_name()
                        self.report_preview = (
                            f"Отчёт для родителей\n"
                            f"Ребёнок: {child[1]}\n"
                            f"Квест: {quest_name}\n"
                            f"Прогресс: {completed}/{total} этапов ({progress:.1f}%)\n"
                            f"Баллы: {points}\n"
                            f"Текущий этап: {child[3] or 1}\n"
                            f"Статус: {child[7]}"
                        )
                    else:
                        self.toast.add("Сначала выберите ребёнка!", "warning")
                if self.btn_send_report.update(mouse_pos, mouse_click):
                    if self.reports_tab == 2 and self.selected_report_child_idx is not None and self.report_preview:
                        child = self.children[self.selected_report_child_idx]
                        parent_email = child[9] if len(child) > 9 else None
                        personal_msg = self.message_input.get_text()
                        if parent_email:
                            success = self.send_email_report(parent_email, child[1], self.report_preview, personal_msg)
                            if success:
                                self.toast.add(f"Отчёт для {child[1]} отправлен на {parent_email}", "success")
                                self.message_input.clear()
                                self.report_preview = ""
                        else:
                            self.toast.add("У ребёнка не указан email родителя!", "error")
                    else:
                        self.toast.add("Сформируйте отчёт перед отправкой", "warning")
                if self.btn_send_all.update(mouse_pos, mouse_click):
                    if not self.children:
                        self.toast.add("Нет детей в группе", "warning")
                    else:
                        sent_count = 0
                        failed_count = 0
                        for child in self.children:
                            if child[7] == 'active':
                                completed = child[4] or 0
                                total = child[5] or 1
                                progress = (completed / total * 100) if total > 0 else 0
                                report = (
                                    f"Отчёт для родителей\n"
                                    f"Ребёнок: {child[1]}\n"
                                    f"Квест: {self.get_current_quest_name()}\n"
                                    f"Прогресс: {completed}/{total} этапов ({progress:.1f}%)\n"
                                    f"Баллы: {child[6] or 0}\n"
                                    f"Текущий этап: {child[3] or 1}\n"
                                    f"Статус: Активен"
                                )
                                parent_email = child[9] if len(child) > 9 else None
                                if parent_email and self.send_email_report(parent_email, child[1], report):
                                    sent_count += 1
                                else:
                                    failed_count += 1
                        if sent_count > 0:
                            self.toast.add(f"Отправлено {sent_count} отчётов", "success")
                        if failed_count > 0:
                            self.toast.add(f"Не удалось отправить {failed_count} отчётов", "warning")
                        self.message_input.clear()
                        self.report_preview = ""

    def draw(self):
        self.screen.fill(ColorScheme.TEACHER_BG)
        self.draw_navigation()
        if self.current_section == "my_group":
            self.draw_my_group()
        elif self.current_section == "progress":
            self.draw_progress_section()
        elif self.current_section == "quest":
            self.draw_quest_section()
        elif self.current_section == "reports":
            self.draw_reports_section()
        self.btn_logout.draw(self.screen)

        if self.modal_window and self.modal_window.visible:
            self.modal_window.show(self.screen)

        self.toast.update()
        self.toast.draw(self.screen)

    def run(self):
        while self.running:
            result = self.handle_events()
            if result == "logout":
                self.running = False
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)