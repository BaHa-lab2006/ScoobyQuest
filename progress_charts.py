"""
Модуль для визуализации графиков и диаграмм
"""
import pygame
import math

class ProgressChart:
    """График прогресса"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = []
        self.labels = []
        
    def set_data(self, data, labels=None):
        """Установка данных для отображения"""
        self.data = data
        self.labels = labels or [str(i) for i in range(len(data))]
    
    def draw(self, screen):
        """Отрисовка графика"""
        if not self.data:
            return
        
        # Фон
        chart_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (255, 255, 255), chart_rect)
        pygame.draw.rect(screen, (200, 200, 200), chart_rect, 2)
        
        # Масштабирование данных
        max_value = max(self.data) if self.data else 1
        scale_y = self.height * 0.8 / max_value
        
        # Оси
        pygame.draw.line(screen, (0, 0, 0),
                        (self.x + 40, self.y + self.height - 30),
                        (self.x + self.width - 20, self.y + self.height - 30), 2)
        
        pygame.draw.line(screen, (0, 0, 0),
                        (self.x + 40, self.y + 20),
                        (self.x + 40, self.y + self.height - 30), 2)
        
        # Данные
        point_radius = 4
        for i in range(len(self.data) - 1):
            x1 = self.x + 40 + (i * (self.width - 60) / (len(self.data) - 1))
            y1 = self.y + self.height - 30 - (self.data[i] * scale_y)
            
            x2 = self.x + 40 + ((i + 1) * (self.width - 60) / (len(self.data) - 1))
            y2 = self.y + self.height - 30 - (self.data[i + 1] * scale_y)
            
            # Линия
            pygame.draw.line(screen, (76, 175, 80), (x1, y1), (x2, y2), 3)
            
            # Точка
            pygame.draw.circle(screen, (27, 94, 32), (int(x1), int(y1)), point_radius)
            
            # Подпись
            if i < len(self.labels):
                font = pygame.font.Font(None, 16)
                label = font.render(self.labels[i], True, (0, 0, 0))
                screen.blit(label, (x1 - label.get_width() // 2, self.y + self.height - 15))
        
        # Последняя точка
        if len(self.data) > 0:
            last_x = self.x + 40 + ((len(self.data) - 1) * (self.width - 60) / (len(self.data) - 1))
            last_y = self.y + self.height - 30 - (self.data[-1] * scale_y)
            pygame.draw.circle(screen, (27, 94, 32), (int(last_x), int(last_y)), point_radius)
        
        # Заголовок
        font = pygame.font.Font(None, 20)
        title = font.render("Прогресс группы", True, (0, 0, 0))
        screen.blit(title, (self.x + self.width // 2 - title.get_width() // 2, self.y + 5))

class PieChart:
    """Круговая диаграмма"""
    
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.data = {}
        
    def set_data(self, data):
        """Установка данных"""
        self.data = data
    
    def draw(self, screen):
        """Отрисовка диаграммы"""
        if not self.data:
            return
        
        # Общая сумма
        total = sum(self.data.values())
        if total == 0:
            return
        
        # Цвета для секторов
        colors = [
            (76, 175, 80),    # Зелёный
            (255, 152, 0),    # Оранжевый
            (33, 150, 243),   # Синий
            (156, 39, 176),   # Фиолетовый
            (244, 67, 54)     # Красный
        ]
        
        # Рисуем сектора
        start_angle = 0
        color_idx = 0
        
        for label, value in self.data.items():
            # Угол сектора
            angle = 360 * (value / total)
            
            # Рисуем сектор
            pygame.draw.arc(screen, colors[color_idx % len(colors)],
                          (self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2),
                          math.radians(start_angle),
                          math.radians(start_angle + angle),
                          self.radius // 2)
            
            # Легенда
            legend_x = self.x + self.radius + 30
            legend_y = self.y - self.radius + color_idx * 30
            
            # Цветной квадрат
            pygame.draw.rect(screen, colors[color_idx % len(colors)],
                           (legend_x, legend_y, 20, 20))
            
            # Текст
            percentage = (value / total) * 100
            legend_text = f"{label}: {percentage:.1f}%"
            font = pygame.font.Font(None, 18)
            text_surf = font.render(legend_text, True, (0, 0, 0))
            screen.blit(text_surf, (legend_x + 30, legend_y))
            
            start_angle += angle
            color_idx += 1
        
        # Центр диаграммы
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius // 3)