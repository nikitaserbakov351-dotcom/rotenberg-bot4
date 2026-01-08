import asyncio
import sys
import os

print("🚀 Бот Ротенберга запускается...")

# Проверка переменных окружения
required_vars = ['API_ID', 'API_HASH', 'SESSION_STRING']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f"❌ Отсутствуют переменные: {missing}")
    sys.exit(1)

print("✅ Все переменные настроены")
print("🤖 Бот готов к работе!")
