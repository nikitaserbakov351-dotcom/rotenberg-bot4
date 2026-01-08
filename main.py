#!/usr/bin/env python3
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from brain import RotenbergBrain
from telegram_client import TelegramClientHandler

# Настройка логирования для Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Уменьшаем логи telethon для чистоты
logging.getLogger('telethon').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска"""
    print("=" * 60)
    print("🤖 БОТ РОМАНА РОТЕНБЕРГА - ЗАПУСК")
    print("=" * 60)

    try:
        # 1. Проверяем, что мы на Railway
        is_railway = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
        print(f"🌐 Среда: {'RAILWAY' if is_railway else 'Локальная'}")

        # 2. Инициализируем мозг бота
        print("🧠 Инициализация базы знаний...")
        brain = RotenbergBrain()
        print(f"✅ Загружено фраз: {sum(len(phrases) for phrases in brain.phrases.values())}")

        # 3. Создаем и запускаем клиент
        print("🚀 Запуск Telegram клиента...")
        client = TelegramClientHandler(Config, brain)

        # Обработчик Ctrl+C
        def signal_handler(sig, frame):
            print(f"\n⚠️ Получен сигнал {sig}. Останавливаю бота...")
            asyncio.create_task(client.stop())
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Запуск
        await client.start()

    except ValueError as e:
        print(f"\n❌ ОШИБКА КОНФИГУРАЦИИ:\n{e}")
        print("\n📝 Убедитесь, что в Railway установлены переменные:")
        print("   - API_ID")
        print("   - API_HASH")
        print("   - SESSION_STRING (самая важная!)")
        sys.exit(1)

    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}", exc_info=True)
        print(f"\n💥 Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Настройка asyncio для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Остановлено пользователем")
    except Exception as e:
        print(f"\n💥 Фатальная ошибка: {e}")
        sys.exit(1)