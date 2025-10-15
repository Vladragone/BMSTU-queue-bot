# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
import os

from config import QUEUE_LIFETIME_HOURS
from queues import QueueManager
from scheduler import setup_scheduler


# === Настройка окружения ===
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
queues = QueueManager()


# === Основная логика ===
async def announce_queue(chat_id: int, subjects: list[str]):
    """Открывает новую очередь и публикует сообщение"""
    queues.open(subjects)
    msg = await bot.send_message(chat_id, queues.format_text(), parse_mode="Markdown")
    queues.message_id = msg.message_id

    asyncio.create_task(close_queue(chat_id, delay=QUEUE_LIFETIME_HOURS * 3600))


async def update_message():
    """Обновляет сообщение с очередью"""
    if queues.message_id:
        await bot.edit_message_text(
            chat_id=CHAT_ID,
            message_id=queues.message_id,
            text=queues.format_text(),
            parse_mode="Markdown"
        )


async def close_queue(chat_id: int, delay: int):
    """Закрывает очередь по таймеру"""
    await asyncio.sleep(delay)
    queues.close()
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=queues.message_id,
        text="❌ Очередь закрыта!\n\n" + queues.format_text(),
        parse_mode="Markdown"
    )


# === Обработка записей пользователей ===
@dp.message(F.text.regexp(r"^!"))
async def handle_signup(message: types.Message):
    """Обработка сообщений пользователей (!веб, !тестирование и т.д.)"""
    if not queues.active:
        return

    # Приводим текст к нижнему регистру
    subject = message.text.lstrip("!").strip().lower()
    user_name = message.from_user.full_name.strip()

    # Список активных предметов в нижнем регистре
    active_subjects_lower = [s.lower() for s in queues.active_subjects]

    if subject not in active_subjects_lower:
        await message.delete()
        return

    # Оригинальное имя предмета
    original_subject = queues.active_subjects[active_subjects_lower.index(subject)]

    if queues.add_user(original_subject, user_name):
        await update_message()
        await message.delete()
        await bot.send_message(
            CHAT_ID,
            f"👤 {user_name} занял(а) место в очереди на *{original_subject}*.",
            parse_mode="Markdown"
        )
    else:
        await message.delete()
        await message.answer(
            f"⚠️ {user_name}, вы уже записаны на {original_subject}.",
            reply=False
        )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start — подтверждение запуска"""
    await message.answer("✅ Бот запущен. Очереди будут открываться по расписанию.")


# === Точка входа ===
async def main():
    setup_scheduler(announce_queue, CHAT_ID)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
