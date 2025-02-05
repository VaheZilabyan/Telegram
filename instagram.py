import os
import shutil
import instaloader
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile  # ✅ Use FSInputFile instead of InputFile
from aiogram.filters import Command

BOT_TOKEN = '7272014149:AAGEfyn8xeV9mL65P9N0z-xvjMyHMNJS8Hk'

# Initialize bot and dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Function to download Instagram post
def download_instagram(url):
    loader = instaloader.Instaloader()
    shortcode = url.split("/")[-2]  # Extract shortcode from URL
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    loader.download_post(post, target=download_folder)
    return download_folder

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Send me an Instagram post link, and I'll download it for you!")

@dp.message()
async def download_handler(message: Message):
    url = message.text
    if "instagram.com/p/" in url or "instagram.com/reel/" in url:
        await message.answer("Downloading... ⏳")
        try:
            folder = download_instagram(url)
            files = os.listdir(folder)

            for file in files:
                file_path = os.path.join(folder, file)

                if file.endswith(".mp4"):
                    media = FSInputFile(file_path)
                    print(f"Sending video: {file}")
                    await bot.send_video(message.chat.id, media)

                elif file.endswith(".jpg"):
                    media = FSInputFile(file_path)
                    print(f"Sending photo: {file}")
                    await bot.send_photo(message.chat.id, media)

            shutil.rmtree(folder)  # Cleanup
            await message.answer("Download complete! ✅")

        except Exception as e:
            await message.answer(f"❌ Error: {e}")
    else:
        await message.answer("⚠️ Please send a valid Instagram post link.")

# Run the bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("Running...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot end.")
