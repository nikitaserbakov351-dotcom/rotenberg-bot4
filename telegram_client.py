import asyncio
import logging
import random
import sys
from datetime import datetime
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telethon.errors import FloodWaitError

from config import Config
from brain import RotenbergBrain

logger = logging.getLogger(__name__)


class TelegramClientHandler:
    """Обработчик Telegram-клиента для локального и Railway запуска"""

    def __init__(self, config: Config, brain: RotenbergBrain):
        self.config = config
        self.brain = brain
        self.client: Optional[TelegramClient] = None
        self.me = None
        self.is_connected = False

        # Настройка логирования
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def start(self):
        """Основной метод запуска бота"""
        try:
            print("=" * 60)
            print("🚀 ЗАПУСК БОТА РОТЕНБЕРГА")
            print("=" * 60)

            # 1. Проверяем конфигурацию
            print("🔍 Проверка конфигурации...")
            self.config.validate()

            # 2. Определяем тип сессии
            print("📱 Создание Telegram клиента...")

            # Импортируем здесь, чтобы избежать циклических импортов
            from telethon.sessions import StringSession

            # ВАЖНО: Разная логика для локального и Railway запуска
            if self.config.IS_RAILWAY:
                # Railway: используем СТРОКОВУЮ сессию
                if not self.config.SESSION_STRING:
                    raise ValueError("На Railway требуется SESSION_STRING!")
                session = StringSession(self.config.SESSION_STRING)
                print("✅ Используется строковая сессия (Railway)")
            else:
                # Локальный запуск: используем ФАЙЛОВУЮ сессию
                if self.config.SESSION_STRING:
                    # Если есть строковая сессия, используем её
                    session = StringSession(self.config.SESSION_STRING)
                    print("✅ Используется строковая сессия (из .env)")
                else:
                    # Иначе используем файловую сессию
                    session = self.config.SESSION_FILE
                    print(f"✅ Используется файловая сессия: {session}")

            # 3. Создаём клиента
            self.client = TelegramClient(
                session=session,
                api_id=self.config.API_ID,
                api_hash=self.config.API_HASH,
                device_model="RotenbergBot",
                system_version="Linux",
                app_version="2.0.0",
                lang_code="ru",
                system_lang_code="ru",
                connection_retries=5,
                request_retries=5,
                auto_reconnect=True
            )

            # 4. Подключаемся
            print("📡 Подключение к Telegram...")
            await self.client.connect()

            # 5. Проверяем авторизацию
            print("🔐 Проверка авторизации...")
            if not await self.client.is_user_authorized():
                print("\n🔐 ТРЕБУЕТСЯ АВТОРИЗАЦИЯ")
                print("=" * 40)

                # Локальная авторизация через терминал
                phone = input("Введите номер телефона (например, +79161234567): ").strip()

                await self.client.send_code_request(phone)
                print("✅ Код отправлен в Telegram")

                code = input("Введите код из Telegram: ").strip()

                try:
                    await self.client.sign_in(phone, code)
                    print("✅ Авторизация успешна!")
                except Exception as e:
                    if "two" in str(e).lower():
                        password = input("Включена 2FA. Введите пароль: ")
                        await self.client.sign_in(password=password)
                        print("✅ Авторизация с 2FA успешна!")
                    else:
                        raise
            else:
                print("✅ Уже авторизован")

            # 6. Получаем информацию о себе
            self.me = await self.client.get_me()
            print(f"✅ Авторизован как: {self.me.first_name} (@{self.me.username})")
            print(f"🆔 ID: {self.me.id}")

            # 7. Настраиваем обработчики событий
            self.setup_handlers()

            # 8. Запускаем бота
            print("\n" + "=" * 60)
            print("🎯 БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
            print("👉 Напишите вашему аккаунту в Telegram")
            print("💬 Бот будет отвечать в стиле Романа Ротенберга")
            print("=" * 60 + "\n")

            # 9. Получаем строковую сессию для Railway
            if not self.config.IS_RAILWAY:
                try:
                    # Получаем строковую сессию из текущей сессии
                    if hasattr(self.client.session, 'save'):
                        new_session_string = self.client.session.save()
                        if new_session_string:
                            print(f"\n💡 ДЛЯ RAILWAY СКОПИРУЙТЕ ЭТУ СЕССИЮ:")
                            print("=" * 70)
                            print(new_session_string)
                            print("=" * 70)
                            print("(Сохраните в переменной SESSION_STRING на Railway)")
                    else:
                        print("\n💡 Для получения строковой сессии для Railway:")
                        print("   - Остановите бота (Ctrl+C)")
                        print("   - Запустите: python get_string.py")
                except Exception as e:
                    logger.debug(f"Не удалось получить строковую сессию: {e}")

            # 10. Запускаем прослушивание сообщений
            await self.client.run_until_disconnected()

        except Exception as e:
            logger.error(f"💥 Критическая ошибка запуска: {e}", exc_info=True)

            if "SESSION_STRING" in str(e):
                print("\n" + "=" * 60)
                print("🔧 РЕШЕНИЕ ПРОБЛЕМЫ:")
                print("=" * 60)
                if self.config.IS_RAILWAY:
                    print("1. Получите строковую сессию на ноутбуке:")
                    print("   python get_string.py")
                    print("2. Скопируйте всю строку")
                    print("3. В Railway добавьте переменную SESSION_STRING")
                else:
                    print("1. Запустите бота локально без SESSION_STRING")
                    print("2. Авторизуйтесь через терминал")
                    print("3. Получите строковую сессию для Railway")
                print("=" * 60)

            if self.client:
                await self.client.disconnect()
            raise

    def setup_handlers(self):
        """Настройка обработчиков событий"""

        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            await self.handle_message(event)

        @self.client.on(events.MessageEdited(incoming=True))
        async def edit_handler(event):
            if random.random() < 0.3:  # 30% шанс ответить на правку
                await event.reply("🔄 Вижу, что правишь сообщение...")

    async def handle_message(self, event):
        """Обработка входящих сообщений"""
        try:
            # Пропускаем свои сообщения
            if event.message.out:
                return

            # Пропускаем служебные сообщения
            if not event.message.text:
                return

            sender = await event.get_sender()
            if not sender:
                return

            # Логируем полученное сообщение
            msg_preview = event.message.text[:100] + "..." if len(event.message.text) > 100 else event.message.text
            logger.info(f"📩 От {sender.first_name} (@{sender.username}): {msg_preview}")

            # Имитация печатания (случайная задержка)
            typing_delay = random.uniform(
                self.config.TYPING_DELAY_MIN,
                self.config.TYPING_DELAY_MAX
            )
            await asyncio.sleep(typing_delay)

            # Генерация ответа
            try:
                response = self.brain.get_response(
                    user_message=event.message.text,
                    user_name=sender.first_name or "Друг"
                )
                logger.info(f"🧠 Ответ: {response[:100]}...")
            except Exception as brain_error:
                logger.error(f"Ошибка brain: {brain_error}")
                response = "Сейчас мыслями на тренировке. Повтори вопрос."

            # Отправка ответа
            try:
                await event.reply(response)
                logger.info(f"✅ Ответ отправлен")

                # Ставим реакцию (60% шанс)
                if random.random() < 0.6:
                    await self.send_reaction(event.message)

                # Отмечаем как прочитанное
                await event.message.mark_read()

            except FloodWaitError as e:
                logger.warning(f"⏳ FloodWait: жду {e.seconds} сек")
                await asyncio.sleep(e.seconds)
                await event.reply(response)

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

    async def send_reaction(self, message):
        """Отправка реакции на сообщение"""
        try:
            reactions = [
                ReactionEmoji(emoticon='👍'),
                ReactionEmoji(emoticon='❤️'),
                ReactionEmoji(emoticon='😂'),
                ReactionEmoji(emoticon='😮'),
                ReactionEmoji(emoticon='👏'),
                ReactionEmoji(emoticon='🔥'),
                ReactionEmoji(emoticon='🎯'),
            ]

            await self.client(SendReactionRequest(
                peer=message.peer_id,
                msg_id=message.id,
                reaction=[random.choice(reactions)]
            ))
        except Exception as e:
            logger.debug(f"Не удалось поставить реакцию: {e}")

    async def save_session_string(self):
        """Сохранение обновленной строки сессии (для будущего использования)"""
        try:
            session_string = self.client.session.save()
            logger.info(f"📋 Новая строковая сессия (первые 50 символов): {session_string[:50]}...")

            # Можно сохранить в переменную окружения для будущих запусков
            # Но на Railway это делается через панель управления
            return session_string

        except Exception as e:
            logger.warning(f"Не удалось сохранить сессию: {e}")
            return None

    async def stop(self):
        """Корректная остановка бота"""
        if self.client and self.is_connected:
            logger.info("🛑 Остановка бота...")
            await self.client.disconnect()
            self.is_connected = False
            logger.info("✅ Бот остановлен")