import requests
import instaloader
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.token import TokenValidationError

# Replace with your bot token from BotFather
API_TOKEN = "7272014149:AAGEfyn8xeV9mL65P9N0z-xvjMyHMNJS8Hk"
CHANNEL_1 = "@cryptomirra"  # Replace with your actual channel username
CHANNEL_2 = "@factologiat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для проверки, является ли пользователь участником обоих каналов
async def is_user_member(user_id: int) -> bool:
    try:
        chat_member_1 = await bot.get_chat_member(CHANNEL_1, user_id)
        chat_member_2 = await bot.get_chat_member(CHANNEL_2, user_id)

        # Проверяем, является ли пользователь участником (участник, администратор или создатель)
        allowed_status = ["member", "administrator", "creator"]
        return chat_member_1.status in allowed_status and chat_member_2.status in allowed_status
    except Exception as e:
        print(f"Ошибка проверки членства: {e}")  # Отладка
        return False  # Возвращаем False в случае ошибки

def fetch_instagram_url(url):
    loader = instaloader.Instaloader()
    shortcode = url.split("/")[-2]  # Извлекаем shortcode из URL
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    media_urls = {
        'photo': None,
        'video': None
    }

    # Проверяем, фото это или видео, затем получаем URL
    if post.is_video:
        media_urls['video'] = post.video_url  # Получаем URL видео
    else:
        media_urls['photo'] = post.url  # Получаем URL фото

    return media_urls

# Функция для загрузки видео с TikTok
def download_tiktok_video(video_url: str) -> str | None:
    """
    Получает URL видео с TikTok без водяного знака через сторонний API.
    """
    api_url = f"https://api.tiklydown.eu.org/api/download?url={video_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        video_data = response.json()
        return video_data['video']['noWatermark']
    return None

# Команда: /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Присоединиться к Каналу 1", url=f"https://t.me/{CHANNEL_1[1:]}")],
        [InlineKeyboardButton(text="📢 Присоединиться к Каналу 2", url=f"https://t.me/{CHANNEL_2[1:]}")],
        [InlineKeyboardButton(text="✅ Проверить", callback_data="check_membership")]
    ])
    await message.answer("👋 Добро пожаловать! Пожалуйста, вступите в оба канала, чтобы продолжить.", reply_markup=keyboard)

# Обработка ссылок на TikTok и Instagram, только если пользователь проверен
@dp.message()
async def handle_url(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, является ли пользователь участником обоих каналов
    if not await is_user_member(user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Присоединиться к Каналу 1", url=f"https://t.me/{CHANNEL_1[1:]}")],
            [InlineKeyboardButton(text="📢 Присоединиться к Каналу 2", url=f"https://t.me/{CHANNEL_2[1:]}")],
            [InlineKeyboardButton(text="✅ Проверить", callback_data="check_membership")]
        ])
        await message.answer("❌ Вы должны вступить в оба канала, прежде чем использовать бота.", reply_markup=keyboard)
        return  # Останавливаем дальнейшую обработку, если не проверено

    url = message.text
    if "tiktok.com" in url:
        # Получаем URL видео
        video_url = download_tiktok_video(url)
        if video_url:
            await message.answer("⬇️ Загружаю ваше видео...")
            try:
                video_file = URLInputFile(video_url)
                await message.answer_video(video_file)
            except Exception as e:
                await message.answer(f"❌ Не удалось отправить видео. Ошибка: {e}")
        else:
            await message.answer("❌ Извините, не удалось скачать видео. Проверьте ссылку и попробуйте снова.")
    elif "instagram.com/p/" in url or "instagram.com/reel/" in url:
        await message.answer("Извлекаю медиа... ⏳")
        try:
            media_urls = fetch_instagram_url(url)
            if media_urls['video']:
                await bot.send_video(message.chat.id, media_urls['video'])
                print(f"Отправляю видео из URL: {media_urls['video']}")
            elif media_urls['photo']:
                await bot.send_photo(message.chat.id, media_urls['photo'])
                print(f"Отправляю фото из URL: {media_urls['photo']}")
            await message.answer("Медиа отправлено! ✅")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    else:
        await message.answer("⚠️ Пожалуйста, отправьте корректную ссылку на видео из Instagram или TikTok.")

# Обработка кнопки проверки
@dp.callback_query(lambda c: c.data == "check_membership")
async def check_membership(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_member(user_id):
        await callback_query.answer("Проверка...")
        await callback_query.message.answer("✅ Вы успешно проверены! Отправьте мне ссылку на видео из Instagram или TikTok.")
    else:
        await callback_query.answer("Проверка...")
        await callback_query.message.answer("❌ Вы должны вступить в оба канала, прежде чем использовать бота. Попробуйте снова.")

# Основная функция для запуска бота
async def main():
    try:
        await dp.start_polling(bot)
    except TokenValidationError:
        print("Неверный токен бота. Пожалуйста, проверьте API_TOKEN.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        import asyncio
        print("Бот запущен...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")

