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

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Function to check if a user is a member of both channels
async def is_user_member(user_id: int) -> bool:
    try:
        chat_member_1 = await bot.get_chat_member(CHANNEL_1, user_id)
        chat_member_2 = await bot.get_chat_member(CHANNEL_2, user_id)

        # Check if the user is a member (member, admin, or creator)
        allowed_status = ["member", "administrator", "creator"]
        return chat_member_1.status in allowed_status and chat_member_2.status in allowed_status

    except Exception as e:
        print(f"Error checking membership: {e}")  # Debugging
        return False  # Return False if an error occurs

def fetch_instagram_url(url):
    loader = instaloader.Instaloader()
    shortcode = url.split("/")[-2]  # Extract shortcode from URL
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    media_urls = {
        'photo': None,
        'video': None
    }

    # Check if it's a photo or video, then get the URL
    if post.is_video:
        media_urls['video'] = post.video_url  # Get video URL
    else:
        media_urls['photo'] = post.url  # Get photo URL

    return media_urls

# Function to download TikTok video
def download_tiktok_video(video_url: str) -> str | None:
    """
    Fetches the TikTok video URL without a watermark using a third-party API.
    """
    api_url = f"https://api.tiklydown.eu.org/api/download?url={video_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        video_data = response.json()
        return video_data['video']['noWatermark']
    return None

# Command: /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Create inline buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel 1", url=f"https://t.me/{CHANNEL_1[1:]}")],
        [InlineKeyboardButton(text="📢 Join Channel 2", url=f"https://t.me/{CHANNEL_2[1:]}")],
        [InlineKeyboardButton(text="✅ Check", callback_data="check_membership")]
    ])

    await message.answer("👋 Welcome! Please join both channels to continue.", reply_markup=keyboard)


# Handle TikTok and Instagram links only if the user is verified
@dp.message()
async def handle_url(message: types.Message):
    user_id = message.from_user.id

    # Check if the user is a member of both channels
    if not await is_user_member(user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel 1", url=f"https://t.me/{CHANNEL_1[1:]}")],
            [InlineKeyboardButton(text="📢 Join Channel 2", url=f"https://t.me/{CHANNEL_2[1:]}")],
            [InlineKeyboardButton(text="✅ Check", callback_data="check_membership")]
        ])
        await message.answer("❌ You must join both channels before using the bot.", reply_markup=keyboard)
        return  # Stop further processing if not verified

    url = message.text
    if "tiktok.com" in url:
        # Fetch the video URL
        video_url = download_tiktok_video(url)
        if video_url:
            await message.answer("⬇️ Downloading your video...")
            try:
                video_file = URLInputFile(video_url)
                await message.answer_video(video_file)
            except Exception as e:
                await message.answer(f"❌ Failed to send the video. Error: {e}")
        else:
            await message.answer("❌ Sorry, I couldn't download the video. Please check the link and try again.")

    elif "instagram.com/p/" in url or "instagram.com/reel/" in url:
        await message.answer("Fetching media... ⏳")
        try:
            media_urls = fetch_instagram_url(url)

            if media_urls['video']:
                await bot.send_video(message.chat.id, media_urls['video'])
                print(f"Sending video from URL: {media_urls['video']}")

            elif media_urls['photo']:
                await bot.send_photo(message.chat.id, media_urls['photo'])
                print(f"Sending photo from URL: {media_urls['photo']}")

            await message.answer("Media sent! ✅")

        except Exception as e:
            await message.answer(f"❌ Error: {e}")

    else:
        await message.answer("⚠️ Please send a valid Instagram or TikTok video link.")

# Handle the check button
@dp.callback_query(lambda c: c.data == "check_membership")
async def check_membership(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_member(user_id):
        await callback_query.answer("Checking...")
        await callback_query.message.answer("✅ You are now verified! Send me an Instagram or TikTok link.")
    else:
        await callback_query.answer("Checking...")
        await callback_query.message.answer("❌ You must join both channels before using the bot. Try again.")


# Main function to start the bot
async def main():
    try:
        await dp.start_polling(bot)
    except TokenValidationError:
        print("Invalid bot token. Please check your API_TOKEN.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        # logging.basicConfig(level=logging.INFO)
        import asyncio

        print("Running...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot end.")
