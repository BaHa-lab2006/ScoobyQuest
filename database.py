"""
Модуль для работы с базой данных Microsoft SQL Server
"""
import pyodbc
import hashlib
import os
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Карта транслитерации русских букв в латиницу
RU_TO_EN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}


def transliterate_ru(text):
    """Простая транслитерация русского текста в латиницу"""
    result = ""
    for ch in text:
        if ch in RU_TO_EN:
            result += RU_TO_EN[ch]
        else:
            if ch.isascii() and (ch.isalnum() or ch == '_'):
                result += ch
            elif ch == ' ':
                result += '_'
            else:
                result += '_'
    result = '_'.join(filter(None, result.split('_')))
    return result.lower()


class DatabaseConnection:
    """Класс для управления подключением к БД"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def connect(self, server=None, database=None, username=None, password=None):
        """Установка подключения к SQL Server"""
        try:
            if server is None:
                server = os.getenv('SQL_SERVER', 'IMOZEPC\\MSSQLSERVER04')
            if database is None:
                database = os.getenv('SQL_DATABASE', 'ScoobyQuestDB')
            if username is None:
                username = os.getenv('SQL_USERNAME', 'Shagy')
            if password is None:
                password = os.getenv('SQL_PASSWORD', 'v.b070217')
            
            connection_string = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
            
            self.connection = pyodbc.connect(connection_string)
            self.connection.autocommit = True
            logger.info("Успешное подключение к базе данных")
            return True
            
        except pyodbc.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False
    
    def get_connection(self):
        """Получение активного подключения"""
        if self.connection is None:
            self.connect()
        return self.connection
    
    def close(self):
        """Закрытие подключения"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Подключение к БД закрыто")


class DatabaseManager:
    """Менеджер для работы с данными"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.conn = self.db.get_connection()
    
    @staticmethod
    def hash_password(password):
        """Хеширование пароля с солью"""
        salt = "scooby_salt_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_user(self, username, password):
        """Проверка пользователя"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT id, username, password_hash, role, full_name, group_name, avatar_id
            FROM Users 
            WHERE username = ?
            """
            
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if user:
                stored_hash = user.password_hash
                input_hash = self.hash_password(password)
                
                if stored_hash == input_hash:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role,
                        'full_name': user.full_name,
                        'group_name': user.group_name,
                        'avatar_id': user.avatar_id
                    }
            
            return None
            
        except pyodbc.Error as e:
            logger.error(f"Ошибка при проверке пользователя: {e}")
            return None
    
    # ---------- Административные методы ----------
    def update_child_status(self, child_id, status):
        """Обновление статуса ребёнка (active/paused)"""
        try:
            cursor = self.conn.cursor()
            query = "UPDATE ChildProgress SET status = ? WHERE child_id = ?"
            cursor.execute(query, (status, child_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка обновления статуса: {e}")
        return False

    def reset_child_progress(self, child_id):
        """Сброс прогресса ребёнка"""
        try:
            cursor = self.conn.cursor()
            query = """
            UPDATE ChildProgress 
            SET current_stage = 1, completed_stages = 0, score = 0, last_activity = GETDATE()
            WHERE child_id = ? AND status = 'active'
            """
            cursor.execute(query, (child_id,))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка сброса прогресса: {e}")
            return False

    def create_teacher(self, username, password, full_name):
        """Создание нового воспитателя (роль 'teacher')"""
        try:
            cursor = self.conn.cursor()
            check_query = "SELECT COUNT(*) FROM Users WHERE username = ?"
            cursor.execute(check_query, (username,))
            if cursor.fetchone()[0] > 0:
                return False

            password_hash = self.hash_password(password)
            query = """
            INSERT INTO Users (username, password_hash, role, full_name)
            VALUES (?, ?, 'teacher', ?)
            """
            cursor.execute(query, (username, password_hash, full_name))
            self.conn.commit()
            self.log_action(None, 'create_teacher', f'Создан воспитатель {full_name} ({username})')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка при создании воспитателя: {e}")
        return False

    def create_child(self, full_name, group_name, password=None, parent_email=None, avatar_id=0):
        """Создание нового ребёнка с автогенерацией логина"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Groups WHERE group_name = ? AND is_active = 1", (group_name,))
            if cursor.fetchone()[0] == 0:
                return False, "Группа не найдена"
            
            trans_group = transliterate_ru(group_name)
            base_username = f"child_{trans_group}"
            
            cursor.execute("SELECT COUNT(*) FROM Users WHERE group_name = ? AND role = 'child'", (group_name,))
            child_count = cursor.fetchone()[0]
            counter = child_count + 1
            
            username = f"{base_username}_{counter}"
            while True:
                cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", (username,))
                if cursor.fetchone()[0] == 0:
                    break
                counter += 1
                username = f"{base_username}_{counter}"
            
            if not password:
                password = "child_default"
            password_hash = self.hash_password(password)
            
            query = """
            INSERT INTO Users (username, password_hash, role, full_name, group_name, avatar_id, parent_email)
            VALUES (?, ?, 'child', ?, ?, ?, ?)
            """
            cursor.execute(query, (username, password_hash, full_name, group_name, avatar_id, parent_email))
            self.conn.commit()
            self.log_action(None, 'create_child', f'Создан ребёнок {full_name} в группе {group_name} (username: {username})')
            return True, username
        except pyodbc.Error as e:
            logger.error(f"Ошибка при создании ребёнка: {e}")
            return False, str(e)

    def set_parent_email(self, child_id, email):
        """Установить email родителя для ребёнка"""
        try:
            cursor = self.conn.cursor()
            query = "UPDATE Users SET parent_email = ? WHERE id = ? AND role = 'child'"
            cursor.execute(query, (email, child_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка при обновлении parent_email: {e}")
            return False

    def get_parent_email(self, child_id):
        """Получить email родителя ребёнка"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT parent_email FROM Users WHERE id = ? AND role = 'child'"
            cursor.execute(query, (child_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении parent_email: {e}")
            return None

    def get_teachers_for_admin(self):
        """Список воспитателей: id, username, full_name"""
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT id, username, full_name FROM Users
            WHERE role = 'teacher'
            ORDER BY full_name
            """
            cursor.execute(query)
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения воспитателей: {e}")
            return []

    def update_group(self, group_id, group_name=None, age_category=None, quest_id=None, teacher_id=None):
        """Обновление параметров группы"""
        try:
            cursor = self.conn.cursor()
            updates = []
            params = []
            if group_name is not None:
                updates.append("group_name = ?")
                params.append(group_name)
            if age_category is not None:
                updates.append("age_category = ?")
                params.append(age_category)
            if quest_id is not None:
                updates.append("current_quest_id = ?")
                params.append(quest_id)
            if teacher_id is not None:
                updates.append("teacher_id = ?")
                params.append(teacher_id)
            if not updates:
                return False
            params.append(group_id)
            query = f"UPDATE Groups SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
            self.log_action(None, 'update_group', f'Изменена группа id={group_id}')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка обновления группы: {e}")
            return False

    def archive_group(self, group_id):
        """Архивировать группу"""
        try:
            cursor = self.conn.cursor()
            query = "UPDATE Groups SET is_active = 0 WHERE id = ?"
            cursor.execute(query, (group_id,))
            self.conn.commit()
            self.log_action(None, 'archive_group', f'Архивирована группа id={group_id}')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка архивации группы: {e}")
            return False

    def get_group_name_by_id(self, group_id):
        """Получить название группы по id"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT group_name FROM Groups WHERE id = ?"
            cursor.execute(query, (group_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения названия группы: {e}")
            return None

    def transfer_children(self, from_group_id, to_group_id):
        """Переместить всех детей из одной группы в другую и архивировать исходную"""
        try:
            cursor = self.conn.cursor()
            from_name = self.get_group_name_by_id(from_group_id)
            to_name = self.get_group_name_by_id(to_group_id)
            if not from_name or not to_name:
                return False
            update_query = """
            UPDATE Users SET group_name = ? 
            WHERE group_name = ? AND role = 'child'
            """
            cursor.execute(update_query, (to_name, from_name))
            self.archive_group(from_group_id)
            self.conn.commit()
            self.log_action(None, 'mass_transfer', f'Перевод детей из {from_name} в {to_name}')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка массового перевода: {e}")
            return False

    def get_archived_groups(self):
        """Получить список архивированных групп"""
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT g.id, g.group_name, g.age_category, 
                q.quest_name, COUNT(u.id) as child_count,
                'Архив'
            FROM Groups g
            LEFT JOIN Quests q ON g.current_quest_id = q.id
            LEFT JOIN Users u ON u.group_name = g.group_name AND u.role = 'child'
            WHERE g.is_active = 0
            GROUP BY g.id, g.group_name, g.age_category, q.quest_name
            ORDER BY g.group_name
            """
            cursor.execute(query)
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения архива групп: {e}")
            return []

    def unarchive_group(self, group_id):
        """Восстановить (разархивировать) группу"""
        try:
            cursor = self.conn.cursor()
            query = "UPDATE Groups SET is_active = 1 WHERE id = ?"
            cursor.execute(query, (group_id,))
            self.conn.commit()
            self.log_action(None, 'unarchive_group', f'Восстановлена группа id={group_id}')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка разархивации группы: {e}")
            return False

    # ---------- Квесты ----------
    def get_quest_id_by_name(self, quest_name):
        """Получить id квеста по имени"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT id FROM Quests WHERE quest_name = ?"
            cursor.execute(query, (quest_name,))
            row = cursor.fetchone()
            return row[0] if row else None
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения id квеста: {e}")
            return None

    def get_quest_stages(self, quest_id):
        """Получить этапы квеста"""
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT stage_number, stage_name, description
            FROM QuestStages
            WHERE quest_id = ?
            ORDER BY stage_number
            """
            cursor.execute(query, (quest_id,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения этапов квеста: {e}")
            return []

    def get_quest_description(self, quest_id):
        """Получить описание квеста"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT description FROM Quests WHERE id = ?"
            cursor.execute(query, (quest_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения описания квеста: {e}")
            return None

    # ---------- Базовые методы для групп и детей ----------
    def get_user_groups(self, teacher_id):
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT g.id, g.group_name, g.age_category, q.quest_name, 
                   COUNT(DISTINCT u.id) as child_count
            FROM Groups g
            LEFT JOIN Quests q ON g.current_quest_id = q.id
            LEFT JOIN Users u ON u.group_name = g.group_name AND u.role = 'child'
            WHERE g.teacher_id = ? AND g.is_active = 1
            GROUP BY g.id, g.group_name, g.age_category, q.quest_name
            """
            cursor.execute(query, (teacher_id,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении групп: {e}")
            return []
    
    def get_group_children(self, group_name, teacher_id=None):
        try:
            cursor = self.conn.cursor()
            if teacher_id:
                query = """
                SELECT u.id, u.full_name, u.avatar_id, cp.current_stage, 
                       cp.completed_stages, cp.total_stages, cp.score, cp.status,
                       cp.last_activity, u.parent_email
                FROM Users u
                LEFT JOIN ChildProgress cp ON u.id = cp.child_id AND cp.status = 'active'
                LEFT JOIN Groups g ON u.group_name = g.group_name
                WHERE u.role = 'child' AND u.group_name = ? 
                AND g.teacher_id = ?
                ORDER BY u.full_name
                """
                cursor.execute(query, (group_name, teacher_id))
            else:
                query = """
                SELECT u.id, u.full_name, u.avatar_id, cp.current_stage, 
                       cp.completed_stages, cp.total_stages, cp.score, cp.status,
                       cp.last_activity, u.parent_email
                FROM Users u
                LEFT JOIN ChildProgress cp ON u.id = cp.child_id AND cp.status = 'active'
                WHERE u.role = 'child' AND u.group_name = ?
                ORDER BY u.full_name
                """
                cursor.execute(query, (group_name,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении детей: {e}")
            return []
    
    def get_child_progress(self, child_id):
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT cp.*, q.quest_name, g.group_name
            FROM ChildProgress cp
            JOIN Quests q ON cp.quest_id = q.id
            JOIN Users u ON cp.child_id = u.id
            JOIN Groups g ON u.group_name = g.group_name
            WHERE cp.child_id = ? AND cp.status = 'active'
            """
            cursor.execute(query, (child_id,))
            return cursor.fetchone()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении прогресса: {e}")
            return None
    
    def update_child_progress(self, child_id, stage=None, score=None):
        try:
            cursor = self.conn.cursor()
            if stage is not None:
                query = """
                UPDATE ChildProgress 
                SET current_stage = ?, last_activity = GETDATE()
                WHERE child_id = ? AND status = 'active'
                """
                cursor.execute(query, (stage, child_id))
            if score is not None:
                query = """
                UPDATE ChildProgress 
                SET score = score + ?, completed_stages = completed_stages + 1,
                    last_activity = GETDATE()
                WHERE child_id = ? AND status = 'active'
                """
                cursor.execute(query, (score, child_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка при обновлении прогресса: {e}")
            return False
    
    def get_all_quests(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM Quests WHERE is_active = 1 ORDER BY age_category"
            cursor.execute(query)
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении квестов: {e}")
            return []
    
    def create_new_group(self, group_name, age_category, teacher_id):
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT id FROM Quests 
            WHERE age_category = ? AND is_active = 1
            ORDER BY id
            """
            cursor.execute(query, (age_category,))
            quest = cursor.fetchone()
            if quest:
                quest_id = quest[0]
            else:
                cursor.execute("SELECT MIN(id) FROM Quests WHERE is_active = 1")
                quest_id = cursor.fetchone()[0]
            query = """
            INSERT INTO Groups (group_name, age_category, current_quest_id, teacher_id)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (group_name, age_category, quest_id, teacher_id))
            self.conn.commit()
            self.log_action(teacher_id, 'create_group', f'Создана группа {group_name}')
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка при создании группы: {e}")
            return False
    
    def get_system_settings(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT setting_key, setting_value FROM SystemSettings"
            cursor.execute(query)
            return {row[0]: row[1] for row in cursor.fetchall()}
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении настроек: {e}")
            return {}
    
    def log_action(self, user_id, action_type, description):
        try:
            cursor = self.conn.cursor()
            query = """
            INSERT INTO SystemLogs (user_id, action_type, description, ip_address)
            VALUES (?, ?, ?, '127.0.0.1')
            """
            cursor.execute(query, (user_id, action_type, description))
            self.conn.commit()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при логировании: {e}")
    
    def get_achievements(self, child_id):
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT a.achievement_name, a.achievement_type, a.awarded_date,
                   q.quest_name, s.stage_name
            FROM Achievements a
            LEFT JOIN Quests q ON a.quest_id = q.id
            LEFT JOIN QuestStages s ON a.stage_id = s.id
            WHERE a.child_id = ?
            ORDER BY a.awarded_date DESC
            """
            cursor.execute(query, (child_id,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            logger.error(f"Ошибка при получении достижений: {e}")
            return []
    
    def add_achievement(self, child_id, achievement_type, achievement_name, quest_id=None, stage_id=None):
        try:
            cursor = self.conn.cursor()
            query = """
            INSERT INTO Achievements (child_id, achievement_type, achievement_name, quest_id, stage_id)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (child_id, achievement_type, achievement_name, quest_id, stage_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка при добавлении достижения: {e}")
            return False

    # ---------- Игровые методы сохранения (исправлены) ----------
    def save_completed_task(self, child_id: int, task_id: int, score: int,
                            time_spent: int, attempts: int):
        """Сохранить результат мини-игры в ChildAnswers (task_id ссылается на Tasks)"""
        try:
            cursor = self.conn.cursor()
            answer_text = f"completed; attempts={attempts}"
            query = """
                INSERT INTO ChildAnswers (child_id, task_id, answer, score, completion_time, completed_at)
                VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            cursor.execute(query, (child_id, task_id, answer_text, score, time_spent))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка сохранения задания: {e}")
            return False

    def save_found_clue(self, child_id: int, clue_name: str):
        """Сохранить найденную улику как достижение (привязано к quest_id=1 и stage_id)"""
        # Определяем stage_id по названию улики (можно упростить, если не требуется)
        stage_map = {
            "button": 1,       # Игровая комната
            "newspaper": 2,    # Спальня
            "green_paint": 3,  # Столовая
            "screwdriver": 4   # Музыкальный зал
        }
        stage_id = stage_map.get(clue_name, 1)
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO Achievements (child_id, achievement_type, achievement_name, quest_id, stage_id)
                VALUES (?, 'clue', ?, 1, ?)
            """
            cursor.execute(query, (child_id, f'Улика: {clue_name}', stage_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка сохранения улики: {e}")
            return False

    def save_collected_toy(self, child_id: int, toy_name: str):
        """Сохранить собранную игрушку как достижение (привязано к quest_id=1 и stage_id)"""
        toy_stage_map = {
            "duck_toy": 1,
            "bunny_toy": 2,
            "car_toy": 3,
            "doll_toy": 4
        }
        stage_id = toy_stage_map.get(toy_name, 1)
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO Achievements (child_id, achievement_type, achievement_name, quest_id, stage_id)
                VALUES (?, 'toy', ?, 1, ?)
            """
            cursor.execute(query, (child_id, f'Игрушка: {toy_name}', stage_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка сохранения игрушки: {e}")
            return False

    def complete_quest(self, child_id: int, quest_id: int = 1):
        """Завершить квест для ребёнка"""
        try:
            cursor = self.conn.cursor()
            query = """
                UPDATE ChildProgress
                SET status = 'completed', last_activity = GETDATE()
                WHERE child_id = ? AND quest_id = ? AND status = 'active'
            """
            cursor.execute(query, (child_id, quest_id))
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            logger.error(f"Ошибка завершения квеста: {e}")
            return False
    
    def get_group_current_quest_id(self, group_name):
        """Возвращает current_quest_id активной группы по её названию"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT current_quest_id FROM Groups WHERE group_name = ? AND is_active = 1"
            cursor.execute(query, (group_name,))
            row = cursor.fetchone()
            return row[0] if row else None
        except pyodbc.Error as e:
            logger.error(f"Ошибка получения quest_id для группы {group_name}: {e}")
            return None

# Глобальный экземпляр
db_manager = DatabaseManager()