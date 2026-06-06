"""
Главный файл приложения Scooby-Doo Quest
"""
import pygame
import sys
import os
from login_screen import LoginScreen
from admin_panel import AdminPanel
from teacher_panel import TeacherPanel
from database import db_manager

class ScoobyQuestGame:
    """Главный класс приложения"""
    
    def __init__(self):
        # Инициализация Pygame
        pygame.init()
        pygame.font.init()
        
        # Настройки окна
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Scooby-Doo: Детективный Квест")
        
        # Иконка приложения
        try:
            icon_path = os.path.join("assets", "images", "icon.png")
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
        except:
            pass
        
        # Текущий пользователь
        self.current_user = None
        self.running = True
        
        # Подключение к БД
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        print("Подключение к базе данных...")
        success = db_manager.db.connect()
        
        if success:
            print("База данных подключена успешно!")
        else:
            print("Ошибка подключения к базе данных!")
            # Создаём заглушку для демонстрации
            self.create_demo_data()
    
    def create_demo_data(self):
        """Создание демо-данных при отсутствии БД"""
        print("Используются демо-данные...")
        # В реальном приложении здесь должна быть обработка ошибки
    
    def show_loading_screen(self):
        """Показать экран загрузки"""
        self.screen.fill((0, 107, 61))  # Scooby Green
        
        # Заголовок
        font = pygame.font.Font(None, 60)
        title = font.render("Scooby-Doo Quest", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Индикатор загрузки
        loading_text = font.render("Загрузка...", True, (255, 255, 255))
        loading_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(loading_text, loading_rect)
        
        pygame.display.flip()
        pygame.time.delay(1000)  # Задержка для демонстрации
    
    def run(self):
        """Запуск главного цикла приложения"""
        self.show_loading_screen()
        
        while self.running:
            # Показываем экран входа
            login_screen = LoginScreen(self.screen)
            self.current_user = login_screen.run()
            
            if not self.current_user:
                # Выход из приложения
                self.running = False
                break
            
            # Перенаправление в зависимости от роли
            role = self.current_user['role']
            if role == 'admin':
                admin_panel = AdminPanel(self.screen, self.current_user)
                admin_panel.run()
            
            elif role == 'teacher':
                teacher_panel = TeacherPanel(self.screen, self.current_user)
                teacher_panel.run()
            
            elif role == 'child':
                from game_selector import get_game_for_child
                child_game = get_game_for_child(self.screen, self.current_user)
                child_game.run()
            
            # Сброс пользователя для следующего входа
            self.current_user = None
        
        self.quit()
    
    def quit(self):
        """Корректный выход из приложения"""
        db_manager.db.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Проверка существования необходимых папок
    required_folders = [
        "assets/fonts",
        "assets/images",
        "assets/sounds",
        "sql_scripts"
    ]
    
    for folder in required_folders:
        os.makedirs(folder, exist_ok=True)
    
    # Запуск приложения
    app = ScoobyQuestGame()
    app.run()