"""
Сервис для работы с email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from database import db_manager

class EmailService:
    """Сервис отправки email"""
    
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из БД"""
        settings = db_manager.get_system_settings()
        
        self.smtp_server = settings.get('smtp_server', '')
        self.smtp_port = int(settings.get('smtp_port', 587))
        self.smtp_user = settings.get('email_from', '')
        
        # Пароль должен храниться в зашифрованном виде
        # В демо-версии используем простой текст
        self.smtp_password = 'demo_password'
    
    def send_email(self, to_email, subject, body):
        """Отправка email"""
        if not all([self.smtp_server, self.smtp_port, self.smtp_user]):
            return False, "Настройки SMTP не заданы"
        
        try:
            # Создаём сообщение
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Текст сообщения
            msg.attach(MIMEText(body, 'plain'))
            
            # Создаём безопасное соединение
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email отправлен успешно"
            
        except Exception as e:
            return False, f"Ошибка отправки email: {str(e)}"
    
    def send_template(self, template_name, to_email, template_vars):
        """Отправка email по шаблону"""
        try:
            # Получаем шаблон из БД
            cursor = db_manager.conn.cursor()
            query = """
            SELECT subject, body_text 
            FROM EmailTemplates 
            WHERE template_name = ? AND is_active = 1
            """
            cursor.execute(query, (template_name,))
            template = cursor.fetchone()
            
            if not template:
                return False, "Шаблон не найден"
            
            subject, body = template
            
            # Заменяем переменные в шаблоне
            for key, value in template_vars.items():
                placeholder = f"{{{key}}}"
                subject = subject.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))
            
            # Отправляем email
            return self.send_email(to_email, subject, body)
            
        except Exception as e:
            return False, f"Ошибка отправки шаблона: {str(e)}"
    
    def test_connection(self):
        """Тестирование подключения к SMTP"""
        if not all([self.smtp_server, self.smtp_port, self.smtp_user]):
            return False, "Настройки SMTP не заданы"
        
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.quit()
            
            return True, "Подключение к SMTP успешно"
            
        except Exception as e:
            return False, f"Ошибка подключения к SMTP: {str(e)}"