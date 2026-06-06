"""
Панель администратора
"""
import pygame
import sys
import os
from database import db_manager
from widgets import *

class AdminPanel:
    """Панель администратора"""
    
    def __init__(self, screen, user_data):
        self.screen = screen
        self.user = user_data
        self.width, self.height = screen.get_size()
        self.running = True
        
        self.current_section = "groups"
        self.modal_window = None
        
        self.groups = []
        self.archived_groups = []
        self.teachers = []
        self.quests = []
        self.settings = {}                 # оставлен словарь, если где-то ещё понадобится
        self.selected_group = None
        self.all_teachers = []
        
        self.edit_search_rects = []
        self.edit_selected_teacher_id = None
        
        self.load_resources()
        self.create_widgets()
        self.load_data()
        
        self.clock = pygame.time.Clock()
        self.inactive_timer = 0
        self.session_timeout = 900

        self.toast = ToastMessage()
    
    def load_resources(self):
        """Загружаем шрифты с уменьшенным размером"""
        text_font_path = "C:/Windows/Fonts/arial.ttf"
        if os.path.exists(text_font_path):
            self.font_large = pygame.font.Font(text_font_path, 26)    # было 32
            self.font_medium = pygame.font.Font(text_font_path, 20)   # было 24
            self.font_small = pygame.font.Font(text_font_path, 16)    # было 18
            self.font_mono = pygame.font.Font(text_font_path, 14)     # было 16
        else:
            self.font_large = pygame.font.Font(None, 26)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)
            self.font_mono = pygame.font.Font(None, 14)
    
    def create_widgets(self):
        nav_width = 180
        nav_height = 55
        nav_x = 20
        nav_y = 90
        
        self.btn_groups = Button(nav_x, nav_y, nav_width, nav_height, "Группы", font=self.font_small)
        self.btn_teachers = Button(nav_x, nav_y + 65, nav_width, nav_height, "Персонал", font=self.font_small)
        self.btn_archive = Button(nav_x, nav_y + 130, nav_width, nav_height, "Архив", font=self.font_small)
        self.btn_logout = Button(self.width - 120, 20, 100, 40, "Выход", font=self.font_small)

        self.create_group_widgets()
        self.create_archive_widgets()
        self.create_teacher_widgets()
    
    def create_group_widgets(self):
        self.group_table = Table(240, 90, self.width - 270, 400,
                                 ["ID", "Название", "Возраст", "Квест", "Детей", "Статус"],
                                 col_widths=[0.05, 0.2, 0.1, 0.35, 0.1, 0.2])
        self.btn_add_group = Button(self.width - 230, 520, 200, 40, "Добавить группу", font=self.font_small)
        self.btn_edit_group = Button(self.width - 230, 570, 200, 40, "Редактировать", font=self.font_small)
        self.btn_archive_group = Button(self.width - 230, 620, 200, 40, "Архивировать", font=self.font_small)
        self.btn_mass_transfer = Button(self.width - 230, 670, 200, 40, "Массовый перевод", font=self.font_small)
    
    def create_archive_widgets(self):
        self.archive_table = Table(240, 90, self.width - 270, 400,
                                   ["ID", "Название", "Возраст", "Квест", "Детей", "Статус"],
                                   col_widths=[0.05, 0.2, 0.1, 0.35, 0.1, 0.2])
        self.btn_unarchive = Button(self.width - 230, 520, 200, 40, "Разархивировать", font=self.font_small)
    
    def create_teacher_widgets(self):
        self.teacher_table = Table(240, 90, self.width - 270, 400,
                                   ["ID", "ФИО", "Email", "Группы", "Статус"])
        self.btn_add_teacher = Button(self.width - 230, 520, 200, 40, "Добавить воспитателя", font=self.font_small)
    
    def load_data(self):
        # Группы (активные)
        try:
            cursor = db_manager.conn.cursor()
            query = """
            SELECT g.id, g.group_name, g.age_category, 
                   q.quest_name, COUNT(u.id) as child_count,
                   CASE WHEN g.is_active = 1 THEN 'Активна' ELSE 'Неактивна' END
            FROM Groups g
            LEFT JOIN Quests q ON g.current_quest_id = q.id
            LEFT JOIN Users u ON u.group_name = g.group_name AND u.role = 'child'
            WHERE g.is_active = 1
            GROUP BY g.id, g.group_name, g.age_category, q.quest_name, g.is_active
            ORDER BY g.group_name
            """
            cursor.execute(query)
            self.groups = cursor.fetchall()
            self.group_table.set_data(self.groups)
        except Exception as e:
            self.toast.add(f"Ошибка загрузки групп: {str(e)}", "error")
        
        # Архивные группы
        try:
            self.archived_groups = db_manager.get_archived_groups()
            self.archive_table.set_data(self.archived_groups)
        except Exception as e:
            self.toast.add(f"Ошибка загрузки архива: {str(e)}", "error")
        
        # Воспитатели
        try:
            cursor = db_manager.conn.cursor()
            query = """
            SELECT u.id, u.full_name, u.username,
                   STRING_AGG(g.group_name, ', '), 'Активен'
            FROM Users u
            LEFT JOIN Groups g ON u.id = g.teacher_id
            WHERE u.role = 'teacher'
            GROUP BY u.id, u.full_name, u.username
            ORDER BY u.full_name
            """
            cursor.execute(query)
            self.teachers = cursor.fetchall()
            self.teacher_table.set_data(self.teachers)
        except Exception as e:
            self.toast.add(f"Ошибка загрузки персонала: {str(e)}", "error")
        
        try:
            self.quests = db_manager.get_all_quests()
        except Exception as e:
            self.toast.add(f"Ошибка загрузки квестов: {str(e)}", "error")
        
        try:
            self.all_teachers = db_manager.get_teachers_for_admin()
        except Exception as e:
            self.all_teachers = []
        
        # Системные настройки (просто сохраняем в словарь, не привязываем к UI)
        try:
            self.settings = db_manager.get_system_settings()
        except Exception as e:
            self.toast.add(f"Ошибка загрузки настроек: {str(e)}", "error")
    
    # ------------------ Модальные окна ------------------
    def show_edit_group_modal(self):
        if not self.selected_group:
            self.toast.add("Выберите группу в таблице", "warning")
            return
        group = self.selected_group
        self.modal_window = ModalWindow(600, 500, f"Редактировать группу: {group[1]}")
        self.modal_window.add_input("Название группы")
        self.modal_window.add_input("Возрастная категория")
        self.modal_window.add_input("Поиск воспитателя")
        self.modal_window.add_button("Отмена")
        self.modal_window.add_button("Сохранить")
        self.modal_window.visible = True
        self.modal_window.callback = self.handle_edit_group_modal
        self.edit_selected_teacher_id = None
        self.modal_window.inputs[0].text = group[1]
        self.modal_window.inputs[1].text = group[2]

    def handle_edit_group_modal(self, button_text):
        if button_text == "Сохранить":
            new_name = self.modal_window.inputs[0].get_text().strip()
            new_age = self.modal_window.inputs[1].get_text().strip()
            if not new_name or new_age not in ['4-5', '5-6', '6-7']:
                self.toast.add("Некорректные данные", "error")
                return
            group_id = self.selected_group[0]
            success = db_manager.update_group(group_id, group_name=new_name, age_category=new_age)
            if self.edit_selected_teacher_id:
                db_manager.update_group(group_id, teacher_id=self.edit_selected_teacher_id)
            if success:
                self.toast.add(f"Группа '{new_name}' обновлена", "success")
                self.load_data()
                self.modal_window.visible = False
            else:
                self.toast.add("Ошибка обновления", "error")
    
    def show_mass_transfer_modal(self):
        if not self.selected_group:
            self.toast.add("Выберите исходную группу", "warning")
            return
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT id, group_name FROM Groups WHERE is_active = 1 AND id != ?", (self.selected_group[0],))
        target_groups = cursor.fetchall()
        if not target_groups:
            self.toast.add("Нет других активных групп для перевода", "warning")
            return
        self.modal_window = ModalWindow(400, 300, "Массовый перевод")
        self.modal_window.add_input("Поиск целевой группы")
        self.modal_window.add_button("Отмена")
        self.modal_window.add_button("Перевести")
        self.modal_window.visible = True
        self.modal_window.callback = self.handle_mass_transfer_modal
        self.mass_transfer_targets = target_groups

    def handle_mass_transfer_modal(self, button_text):
        if button_text == "Перевести":
            search = self.modal_window.inputs[0].get_text().strip().lower()
            choices = [g for g in self.mass_transfer_targets if search in g[1].lower()]
            if not choices:
                self.toast.add("Группа не найдена", "error")
                return
            target_id = choices[0][0]
            success = db_manager.transfer_children(self.selected_group[0], target_id)
            if success:
                self.toast.add("Дети переведены, исходная группа архивирована", "success")
                self.load_data()
            else:
                self.toast.add("Ошибка перевода", "error")
    
    # ------------------ Отрисовка ------------------
    def fit_text(self, text, font, max_width, color):
        """Подбирает размер шрифта так, чтобы текст влез в max_width, но не меньше 10 pt."""
        current_font = font
        size = font.get_height()
        while current_font.size(text)[0] > max_width and size > 10:
            size -= 1
            current_font = pygame.font.Font(font.name if hasattr(font, 'name') else None, size)
        return current_font.render(text, True, color)

    def draw_navigation(self):
        nav_rect = pygame.Rect(0, 0, 240, self.height)
        pygame.draw.rect(self.screen, ColorScheme.ADMIN_PANEL, nav_rect)
        
        # Заголовок
        title = self.font_large.render("Админ-панель", True, ColorScheme.ADMIN_TEXT)
        self.screen.blit(title, (20, 30))
        
        # Информация о пользователе (с автоподбором размера)
        user_text = f"Администратор: {self.user['full_name']}"
        max_text_width = nav_rect.width - 30
        user_surf = self.fit_text(user_text, self.font_small, max_text_width, ColorScheme.ADMIN_TEXT_SECONDARY)
        self.screen.blit(user_surf, (20, 70))
        
        # Кнопки навигации (без Настроек)
        self.btn_groups.draw(self.screen)
        self.btn_teachers.draw(self.screen)
        self.btn_archive.draw(self.screen)
    
    def draw_groups_section(self):
        title = self.font_large.render("Управление группами", True, ColorScheme.ADMIN_TEXT)
        self.screen.blit(title, (250, 30))
        self.group_table.draw(self.screen)
        self.btn_add_group.draw(self.screen)
        self.btn_edit_group.draw(self.screen)
        self.btn_archive_group.draw(self.screen)
        self.btn_mass_transfer.draw(self.screen)
        hint = self.font_small.render("Выберите группу в таблице для управления", True, ColorScheme.ADMIN_TEXT_SECONDARY)
        self.screen.blit(hint, (250, 510))
    
    def draw_archive_section(self):
        title = self.font_large.render("Архив групп", True, ColorScheme.ADMIN_TEXT)
        self.screen.blit(title, (250, 30))
        self.archive_table.draw(self.screen)
        self.btn_unarchive.draw(self.screen)
        hint = self.font_small.render("Выберите группу для восстановления", True, ColorScheme.ADMIN_TEXT_SECONDARY)
        self.screen.blit(hint, (250, 510))
    
    def draw_teachers_section(self):
        title = self.font_large.render("Управление персоналом", True, ColorScheme.ADMIN_TEXT)
        self.screen.blit(title, (250, 30))
        self.teacher_table.draw(self.screen)
        self.btn_add_teacher.draw(self.screen)
    
    # ------------------ Обработка событий ------------------
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
                if hasattr(self, 'edit_search_rects') and self.modal_window.visible:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for rect, teacher_id in self.edit_search_rects:
                            if rect.collidepoint(event.pos):
                                self.edit_selected_teacher_id = teacher_id
                                for inp in self.modal_window.inputs:
                                    if inp.placeholder == "Поиск воспитателя":
                                        teacher = next((t for t in self.all_teachers if t[0] == teacher_id), None)
                                        if teacher:
                                            inp.text = teacher[2]
                                        break
                                self.edit_search_rects = []
                                break
                continue
            
            if self.btn_groups.update(mouse_pos, mouse_click):
                self.current_section = "groups"
            if self.btn_teachers.update(mouse_pos, mouse_click):
                self.current_section = "teachers"
            if self.btn_archive.update(mouse_pos, mouse_click):
                self.current_section = "archive"
            if self.btn_logout.update(mouse_pos, mouse_click):
                self.running = False
                return "logout"
            
            if self.current_section == "groups":
                selected = self.group_table.handle_event(event)
                if selected:
                    self.selected_group = selected
                if self.btn_add_group.update(mouse_pos, mouse_click):
                    self.show_add_group_modal()
                if self.btn_edit_group.update(mouse_pos, mouse_click):
                    self.show_edit_group_modal()
                if self.btn_archive_group.update(mouse_pos, mouse_click):
                    if self.selected_group:
                        if db_manager.archive_group(self.selected_group[0]):
                            self.toast.add(f"Группа '{self.selected_group[1]}' архивирована", "success")
                            self.load_data()
                        else:
                            self.toast.add("Ошибка архивации", "error")
                if self.btn_mass_transfer.update(mouse_pos, mouse_click):
                    self.show_mass_transfer_modal()
            
            elif self.current_section == "archive":
                selected_arch = self.archive_table.handle_event(event)
                if selected_arch:
                    self.selected_archived_group = selected_arch
                if self.btn_unarchive.update(mouse_pos, mouse_click):
                    if hasattr(self, 'selected_archived_group') and self.selected_archived_group:
                        if db_manager.unarchive_group(self.selected_archived_group[0]):
                            self.toast.add(f"Группа '{self.selected_archived_group[1]}' восстановлена", "success")
                            self.load_data()
                        else:
                            self.toast.add("Ошибка восстановления", "error")
                    else:
                        self.toast.add("Выберите группу в таблице", "warning")
            
            elif self.current_section == "teachers":
                self.teacher_table.handle_event(event)
                if self.btn_add_teacher.update(mouse_pos, mouse_click):
                    self.show_add_teacher_modal()
        
        self.inactive_timer += 1
        if self.inactive_timer > self.session_timeout * 60:
            self.toast.add("Сессия истекла из-за бездействия", "warning")
            return "timeout"
    
    def show_add_group_modal(self):
        self.modal_window = ModalWindow(500, 400, "Добавить группу")
        self.modal_window.add_input("Название группы")
        self.modal_window.add_input("Возрастная категория (4-5/5-6/6-7)")
        self.modal_window.add_button("Отмена")
        self.modal_window.add_button("Создать")
        self.modal_window.visible = True
        self.modal_window.callback = self.handle_group_modal
    
    def handle_group_modal(self, button_text):
        if button_text == "Создать":
            group_name = self.modal_window.inputs[0].get_text()
            age_category = self.modal_window.inputs[1].get_text()
            if group_name and age_category in ['4-5', '5-6', '6-7']:
                success = db_manager.create_new_group(group_name, age_category, self.user['id'])
                if success:
                    self.toast.add(f"Группа '{group_name}' создана!", "success")
                    self.load_data()
                else:
                    self.toast.add("Ошибка создания группы", "error")
            else:
                self.toast.add("Некорректные данные", "error")
    
    def show_add_teacher_modal(self):
        self.modal_window = ModalWindow(500, 400, "Добавить воспитателя")
        self.modal_window.add_input("Username (email)")
        self.modal_window.add_input("Пароль", is_password=True)
        self.modal_window.add_input("ФИО")
        self.modal_window.add_button("Отмена")
        self.modal_window.add_button("Создать")
        self.modal_window.visible = True
        self.modal_window.callback = self.handle_teacher_modal
    
    def handle_teacher_modal(self, button_text):
        if button_text == "Создать":
            username = self.modal_window.inputs[0].get_text().strip()
            password = self.modal_window.inputs[1].get_text()
            full_name = self.modal_window.inputs[2].get_text().strip()
            if not (username and password and full_name):
                self.toast.add("Заполните все поля", "error")
                return
            success = db_manager.create_teacher(username, password, full_name)
            if success:
                self.toast.add(f"Воспитатель '{full_name}' добавлен", "success")
                self.load_data()
            else:
                self.toast.add("Ошибка: возможно, такой email уже существует", "error")
    
    def draw(self):
        self.screen.fill(ColorScheme.ADMIN_BG)
        self.draw_navigation()
        if self.current_section == "groups":
            self.draw_groups_section()
        elif self.current_section == "archive":
            self.draw_archive_section()
        elif self.current_section == "teachers":
            self.draw_teachers_section()
        self.btn_logout.draw(self.screen)
        
        if self.modal_window and self.modal_window.visible:
            self.modal_window.show(self.screen)
            if hasattr(self, 'edit_selected_teacher_id') and self.modal_window.visible:
                if len(self.modal_window.inputs) >= 3:
                    search_input = self.modal_window.inputs[2]
                    search_text = search_input.get_text().strip().lower()
                    if search_text:
                        matches = [t for t in self.all_teachers if search_text in t[1].lower() or search_text in t[2].lower()]
                        self.edit_search_rects = []
                        base_x = search_input.rect.x
                        base_y = search_input.rect.y + 40
                        for i, t in enumerate(matches[:5]):
                            name = f"{t[2]} ({t[1]})"
                            surf = self.font_small.render(name, True, (0,0,0))
                            r = pygame.Rect(base_x, base_y + i*22, 300, 22)
                            pygame.draw.rect(self.screen, (220,220,220) if r.collidepoint(pygame.mouse.get_pos()) else (255,255,255), r)
                            self.screen.blit(surf, (base_x+5, base_y + i*22 + 2))
                            self.edit_search_rects.append((r, t[0]))
        
        self.toast.update()
        self.toast.draw(self.screen)
    
    def run(self):
        while self.running:
            result = self.handle_events()
            if result == "logout" or result == "timeout":
                self.running = False
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)