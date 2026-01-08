import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """Получение строковой сессии для Railway"""
    print("=" * 60)
    print("🔐 ГЕНЕРАТОР СТРОКОВОЙ СЕССИИ ДЛЯ RAILWAY")
    print("=" * 60)
    print("\n⚠️  ВАЖНО: Этот скрипт нужно запускать на НОУТБУКЕ!")
    print("   Там, где бот уже авторизован через файловую сессию.")
    print()

    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        # Используем ваши данные
        API_ID = 34855836
        API_HASH = "505884cacfad99610d616c2bc1e200d4"
        SESSION_FILE = "rotenberg_session"

        print("🔍 Подключаюсь к существующей сессии...")

        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            print("❌ Сессия не авторизована!")
            print("\nСначала запустите бота и авторизуйтесь:")
            print("   1. python main.py")
            print("   2. Введите номер телефона и код")
            print("   3. Остановите бот (Ctrl+C)")
            print("   4. Запустите этот скрипт снова")
            await client.disconnect()
            return

        me = await client.get_me()
        print(f"✅ Подключен как: {me.first_name} (@{me.username})")

        # Получаем строковую сессию
        string_session = StringSession.save(client.session)

        print("\n" + "=" * 70)
        print("✅ СТРОКОВАЯ СЕССИЯ ДЛЯ RAILWAY:")
        print("=" * 70)
        print(string_session)
        print("=" * 70)

        # Сохраняем в файл
        with open("RAILWAY_SESSION.txt", "w", encoding="utf-8") as f:
            f.write(string_session)

        print("\n💾 Сессия сохранена в RAILWAY_SESSION.txt")
        print("\n📋 КОПИРУЙТЕ ВЕСЬ ТЕКСТ ВЫШЕ (всю длинную строку)")
        print("   и вставьте в Railway как переменную SESSION_STRING")
        print("\n🚀 Как добавить в Railway:")
        print("   1. В Railway Dashboard → Settings → Variables")
        print("   2. Добавьте переменную: SESSION_STRING")
        print("   3. Вставьте скопированную строку")
        print("   4. Сохраните")

        await client.disconnect()

    except FileNotFoundError:
        print("❌ Файл сессии 'rotenberg_session' не найден!")
        print("\nСначала запустите бота локально:")
        print("   1. Убедитесь, что есть файл .env с API_ID и API_HASH")
        print("   2. Запустите: python main.py")
        print("   3. Авторизуйтесь (введите номер и код)")
        print("   4. Остановите бот (Ctrl+C)")
        print("   5. Запустите этот скрипт снова")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())