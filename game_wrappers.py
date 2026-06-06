import pygame
from scooby_game_final import GameManager as ScoobyGame
from ghost_game import GhostGame
from library_ghost_game import LibraryGame, SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class BaseGameWrapper:
    """Базовый класс для всех игр, чтобы main.py мог единообразно вызывать run()."""
    def run(self):
        raise NotImplementedError

class ScoobyGameWrapper(BaseGameWrapper):
    def __init__(self, screen, user_info):
        self.game = ScoobyGame(screen, user_info)  # уже доработанный конструктор

    def run(self):
        self.game.run()

class GhostGameWrapper(BaseGameWrapper):
    def __init__(self, screen, user_info):
        # user_id из текущего пользователя
        self.game = GhostGame(screen, user_info['id'])

    def run(self):
        self.game.run()

class LibraryGhostGameWrapper(BaseGameWrapper):
    def __init__(self, screen, user_info):
        db_config = {
            'server': 'IMOZEPC\\MSSQLSERVER04',
            'database': 'ScoobyQuestDB',
            'username': 'Shagy',
            'password': 'v.b070217',
            'driver': '{ODBC Driver 17 for SQL Server}'
        }
        child_id = user_info['id']
        username = user_info.get('username', 'Ребёнок')
        self.game = LibraryGame(screen, db_config, child_id, username,
                                on_exit=self.game_exit, on_finish=self.game_finish)
        self.exited = False

    def game_exit(self):
        self.exited = True

    def game_finish(self):
        self.exited = True

    def run(self):
        clock = pygame.time.Clock()
        while self.game.running:
            dt = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                self.game.handle_event(event)
            self.game.update(dt)
            self.game.draw()
            pygame.display.flip()