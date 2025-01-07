import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import requests
from PIL import Image
import io
import random
import logging
import sqlite3
import atexit
from Tokens import Telegram_Bot, AI
# Initialize the Bot
bot = telebot.TeleBot(Telegram_Bot)

# Database Setup
db_connection = sqlite3.connect("users.db", check_same_thread=False)
db_cursor = db_connection.cursor()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    telegram_id INTEGER UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""") # Creating table users with Username and telegram_id keys
db_connection.commit()
@atexit.register
def close_db_connection():
    db_connection.close()
    logging.info("Database connection closed.")

# API Details
IMAGE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
headers = {"Authorization": f"Bearer {AI}"}
# These variables will play a huge role in stylization
extra_prompt = "" # Style of the image
last_user_prompt = "" # Actual prompt
selected_style = "" # last_user_prompt + extra_prompt
# Multidimensional dictionary for language content.
LANGUAGE_CONTENT = {
    "english": {
        "choose_language": "Welcome! Please select your preferred language below to get started. 🌍",
        "selected_language": (
            "Great! You've set your language to English.\n\n"
            "Now, simply send me a detailed description of what you'd like me to generate as an image. "
            "For example, 'a futuristic city at sunset with flying cars' or 'a serene lake surrounded by mountains.'\n"
            "Get creative and let me bring your imagination to life! 🎨✨"
        ),
        "generating": (
            "Hang tight! I'm generating beautiful images based on your description: '{prompt}'. "
            "This may take a few moments, but I promise it'll be worth the wait. ⏳💡"
        ),
        "feedback_prompt": "What do you think about this result",
        "btn_good": "This is Amazing! ✅",
        "btn_regenerate": "Try Again 🔄",
        "btn_stylize": "Stylize 🎨",
        "good": (
            "Awesome! 🎉 If you want another image, feel free to write a new description. "
            "I'm ready to create more magic whenever you are! 🌟"
        ),
        "regenerate": (
            "Sure thing! I'm working on regenerating the last image based on your prompt. "
            "Give me a moment, and I'll deliver something equally amazing! 🔄⏳"
        ),
        "stylize_prompt": "Choose a style to apply to your next image:",
        "styles": ["Futuristic🤖✨", "LEGO🧱🎮", "Black/White⚫⚪", "Abstract🎨🔺"],
        "styled_image": f"Here is your {selected_style}-styled image! You can give another prompt if you want for me to generate a new picture.",
        "error": (
            "Oops! Something went wrong on my end. 😔\n\nError details: {error}\n\n"
            "Please try again or adjust your prompt to see if that helps!"
        ),
    },
    "russian": {
        "choose_language": "Добро пожаловать! Пожалуйста, выберите язык ниже, чтобы начать. 🌍",
        "selected_language": (
            "Отлично! Вы выбрали русский язык.\n\n"
            "Теперь отправьте мне подробное описание того, что вы хотите, чтобы я сгенерировал. "
            "Например, 'футуристический город на закате с летающими машинами' или 'спокойное озеро, окруженное горами.'\n"
            "Дайте волю фантазии, и я воплощу ваши идеи в жизнь! 🎨✨"
        ),
        "generating": (
            "Подождите немного! Создаю изображения по вашему описанию: '{prompt}'. "
            "Это может занять немного времени, но результат вас приятно удивит. ⏳💡"
        ),
        "feedback_prompt": "Что вы думаете об этом результате?",
        "btn_good": "Это потрясающе! ✅",
        "btn_regenerate": "Попробовать снова 🔄",
        "btn_stylize": "Стилизация 🎨",
        "good": (
            "Отлично! 🎉 Если хотите другое изображение, просто отправьте новое описание. "
            "Я готов создать еще больше волшебства! 🌟"
        ),
        "regenerate": (
            "С удовольствием! Я пересоздаю изображение по вашему запросу. "
            "Пожалуйста, подождите немного! 🔄⏳"
        ),
        "stylize_prompt": "Выберите стиль для следующего изображения:",
        "styles": ["Футуристический🤖✨", "LEGO🧱🎮", "Черно-белое⚫⚪", "Абстракция🎨🔺"],
    "styled_image": f"Вот ваше изображение в стиле {selected_style}! Вы можете написать новый запрос, если хотите, чтобы я создал другое изображение."

,
        "error": (
            "Упс! Что-то пошло не так. 😔\n\nДетали ошибки: {error}\n\n"
            "Попробуйте снова или измените описание!"
        ),
    },
    "azerbaijani": {
        "choose_language": "Xoş gəlmisiniz! Başlamaq üçün aşağıdakı dildən birini seçin. 🌍",
        "selected_language": (
            "Möhtəşəm! Dilinizi Azərbaycan dili olaraq seçdiniz.\n\n"
            "İndi mənə yaratmaq istədiyiniz təsvirin ətraflı məlumatını göndərin. "
            "Məsələn, 'gün batımında uçan maşınlarla futuristik bir şəhər' və ya 'dağlarla əhatə olunmuş sakit bir göl.'\n"
            "Xəyal gücünüzdən istifadə edin, mən isə onu gerçəkliyə çevirim! 🎨✨"
        ),
        "generating": (
            "Bir az gözləyin! Təsvirinizə əsasən şəkil yaradıram: '{prompt}'. "
            "Bu bir az vaxt ala bilər, amma nəticə gözəl olacaq. ⏳💡"
        ),
        "feedback_prompt": "Bu nəticədən barədə nə fikirləşirsiz?",
        "btn_good": "Bu möhtəşəmdir! ✅",
        "btn_regenerate": "Yenidən Yarat 🔄",
        "btn_stylize": "Stilizasiya 🎨",
        "good": (
            "Əla! 🎉 Başqa bir şəkil istəyirsinizsə, sadəcə yeni təsvir göndərin. "
            "Həmişə sizin üçün hazıram! 🌟"
        ),
        "regenerate": (
            "Məmnuniyyətlə! Mən təsviri yenidən yaradacağam. "
            "Bir az gözləyin! 🔄⏳"
        ),
        "stylize_prompt": "Növbəti şəkil üçün bir üslub seçin:",
        "styles": ["Futuristik🤖✨", "LEGO🧱🎮", "Qara/Ağ⚫⚪", "Abstraksiya🎨🔺"],
        "styled_image": "Budur sizin {selected_style}-stilindəki təsviriniz! Başqa bir şəkil yaratmağımı istəyirsinizsə, yeni bir təsvir göndərə bilərsiniz.",
        "error": (
            "Vay! Nəsə səhv getdi. 😔\n\nXəta təfərrüatı: {error}\n\n"
            "Zəhmət olmasa yenidən cəhd edin və ya təsviri dəyişdirin!"
        ),
    },
}

user_data = {}

# /start Command
@bot.message_handler(commands=["start"])
def starting_message(message):
    #Some important variables for chat and user data
    username = message.chat.username
    chat_id = message.chat.id

    # Default language is English
    user_data[chat_id] = {"language": "english"}
    content = LANGUAGE_CONTENT["english"]
    print(username)
    welcome_text = content["choose_language"]
    bot.send_message(chat_id, welcome_text)

    # Language selection buttons
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_english"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_russian"),
        InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="lang_azerbaijani"),
    )
    bot.send_message(chat_id, "Choose your language:", reply_markup=markup)

    # Insert user data into the database
    try:
        db_cursor.execute(
            "INSERT OR IGNORE INTO users (username, telegram_id) VALUES (?, ?)",
            (username, chat_id),
        )
        db_connection.commit() # Saving changes of database
        logging.info(f"User {username} (ID: {chat_id}) added to the database.")
    except Exception as e:
        logging.error(f"Error inserting user into database: {e}")


# Language Selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    selected_language = call.data.split("_")[1]
    # Selecting language
    if selected_language in LANGUAGE_CONTENT:
        user_data[chat_id]["language"] = selected_language
        content = LANGUAGE_CONTENT[selected_language]
        bot.send_message(chat_id, content["selected_language"])
    else:
        bot.send_message(chat_id, "Invalid selection. Please try again.")


#  Generating image
def query_image(prompt):
    # Combine prompt with style
    styled_prompt = f"{extra_prompt} {prompt}".strip()

    payload = {"inputs": styled_prompt, "seed": random.randint(0, 2 ** 32 - 1)}
    try:
        response = requests.post(IMAGE_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.content  # Return image bytes
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying image API: {e}")
        return None
# --- Generate Images ---
@bot.message_handler(func=lambda message: True)
def generate_images(message):
    chat_id = message.chat.id
    user_input = message.text.strip()

    # Check if user exists and store their last prompt
    if chat_id not in user_data:
        bot.reply_to(message, "Please select a language first using /start.")
        return

    user_data[chat_id]["last_prompt"] = user_input  # Store last user prompt

    # Generate images as before, using user-specific last prompt
    language = user_data[chat_id]["language"]
    content = LANGUAGE_CONTENT[language]

    bot.send_message(chat_id, content["generating"].format(prompt=user_input))

    images = []
    try:
        for _ in range(3): #Bruh. In Python you can create _, __, ___ variables.
            image_bytes = query_image(user_input)
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                bio.seek(0)
                images.append(bio)
            else:
                logging.warning(f"Failed to generate image for prompt: {user_input}")

        if images:
            # Send images as a group. In 1 message basically
            media_group = [InputMediaPhoto(image) for image in images]
            bot.send_media_group(chat_id, media_group)

            # Send feedback buttons
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(content["btn_good"], callback_data="good"),
                InlineKeyboardButton(content["btn_regenerate"], callback_data="regenerate"),
                InlineKeyboardButton(content["btn_stylize"], callback_data="stylize"),
            )
            bot.send_message(chat_id, content["feedback_prompt"], reply_markup=markup)
        else:
            bot.send_message(chat_id, content["error"].format(error="Image generation failed."))
    except Exception as e:
        logging.error(f"Error in image generation: {e}")
        bot.send_message(chat_id, content["error"].format(error=str(e)))
# --- Handle Buttons ---
@bot.callback_query_handler(func=lambda call: call.data in ["good", "regenerate", "stylize"])
def handle_button_click(call):
    #Some necessary variables
    chat_id = call.message.chat.id
    language = user_data.get(chat_id, {}).get("language", "english")
    content = LANGUAGE_CONTENT[language]
    #Checking clicked button
    if call.data == "good":
        bot.send_message(chat_id, content["good"])
    elif call.data == "regenerate":
        bot.send_message(chat_id, content["regenerate"])
        if chat_id in last_user_prompt:
            query_image(last_user_prompt)  # Use stored prompt
        else:
            bot.send_message(chat_id, content["error"].format(error="No prompt to regenerate."))
    elif call.data == "stylize":
        bot.send_message(chat_id, content["stylize_prompt"])
        # Provide style selection buttons
        markup = InlineKeyboardMarkup()
        #creates buttons for styles
        for style in content["styles"]:
            markup.add(InlineKeyboardButton(style, callback_data=f"style_{style}"))
        bot.send_message(chat_id, "Choose a style:", reply_markup=markup)


# Apply style callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("style_"))
def apply_style(call):
    chat_id = call.message.chat.id
    language = user_data.get(chat_id, {}).get("language", "english")
    content = LANGUAGE_CONTENT[language]
    selected_style = call.data.split("_")[1]

    if chat_id not in user_data or "last_prompt" not in user_data[chat_id]:
        bot.send_message(chat_id, "Please provide a prompt first!")
        return

    # Update user-specific extra_prompt
    user_data[chat_id]["extra_prompt"] = selected_style

    # Combine prompt and style
    last_prompt = user_data[chat_id]["last_prompt"]
    extra_prompt = user_data[chat_id]["extra_prompt"]
    styled_prompt = f"{extra_prompt} {last_prompt}".strip()

    bot.send_message(chat_id, f"Applying style: {selected_style}. Please wait...")

    # Generate styled image
    image_bytes = query_image(styled_prompt)
    # Sending this file to the chat
    if image_bytes:
        image = Image.open(io.BytesIO(image_bytes))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        bio.seek(0)
        bot.send_photo(chat_id, bio, caption=content["styled_image"])
    else:
        bot.send_message(chat_id, "Sorry, I couldn't generate the image. Please try again later.")


# Runs bot infinitely until program is stopped.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.infinity_polling()
