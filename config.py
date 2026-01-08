import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Config:
    """Настройки бота для локального и Railway запуска"""

    # Ключи API (в .env или Railway переменных)
    API_ID = int(os.getenv('API_ID', '34855836'))
    API_HASH = os.getenv('API_HASH', '505884cacfad99610d616c2bc1e200d4')

    # Строковая сессия (ТОЛЬКО для Railway)
    SESSION_STRING = os.getenv('SESSION_STRING', '')

    # Файловая сессия (для локального запуска на ноутбуке)
    SESSION_FILE = os.getenv('SESSION_NAME', 'rotenberg_session')

    # Настройки задержек
    TYPING_DELAY_MIN = 0.5
    TYPING_DELAY_MAX = 4.5

    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Флаг для определения среды
    IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') == 'production'

    @classmethod
    def validate(cls):
        """Проверка конфигурации с учётом среды"""
        errors = []

        # Проверка API_ID
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID не настроен")

        # Проверка API_HASH
        if not cls.API_HASH or cls.API_HASH == '':
            errors.append("API_HASH не настроен")

        # Проверка SESSION_STRING для Railway
        if cls.IS_RAILWAY:
            if not cls.SESSION_STRING or cls.SESSION_STRING == '':
                errors.append("SESSION_STRING не настроен (необходим для Railway)")
        else:
            # Локально используем файловую сессию
            if not cls.SESSION_STRING:
                print("⚠️  SESSION_STRING не настроен, используется файловая сессия 'rotenberg_session'")

        # Если есть ошибки - выводим
        if errors:
            error_msg = "❌ Ошибки конфигурации:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)

        # Вывод информации о конфигурации
        print("✅ Конфигурация валидна")
        print(f"   Режим: {'RAILWAY' if cls.IS_RAILWAY else 'Локальный'}")
        print(f"   API_ID: {'*' * 8}{str(cls.API_ID)[-4:]}")
        print(f"   API_HASH: {'*' * 8}{cls.API_HASH[-4:]}")
        print(f"   Сессия: {'Строковая (Railway)' if cls.SESSION_STRING else f'Файловая ({cls.SESSION_FILE})'}")