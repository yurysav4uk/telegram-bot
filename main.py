from imports import *

# Установка токена бота и других настроек
TELEGRAM_KEY = '7304494637:AAFxjsgnSmiMPD0tQKWm3Y27adM1VJurVoQ'
VOICE_LANGUAGE = 'ru-RU'
MAX_MESSAGE_SIZE = 50 * 1024 * 1024  # 50 MB (ограничение Telegram на размер файла)
MAX_MESSAGE_DURATION = 120  # seconds (ограничение Telegram на длительность аудиосообщения)

bot = TeleBot(TELEGRAM_KEY)

spell = SpellChecker()

greeted_users = set()

@bot.message_handler(commands=['start'])
def start_prompt(message):
    greeted_users.add(message.chat.id)
    user_name = message.from_user.first_name
    reply = ("Hello, {user_name}! I can transform your voice message into a text.\n"
             "<b> limit is 2 min!</b>").format(user_name=user_name)
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="🟠Dev", url="https://t.me/t1pokrutoy")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, reply, parse_mode="HTML", reply_markup=keyboard)

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    received_message = bot.reply_to(message, "Wait")
    asyncio.run(remove_message(received_message, 4))
    process_audio_message(message)

@bot.message_handler(content_types=['video_note'])
def handle_video_message(message):
    received_message = bot.reply_to(message, "video received, wait")
    asyncio.run(remove_message(received_message, 4))
    process_video_message(message)

async def remove_message(message, delay):
    await asyncio.sleep(delay)
    bot.delete_message(message.chat.id, message.message_id)

def add_punctuation(text):
    corrected_text = spell.correction(text)
    if corrected_text is None:
        return text

    if not corrected_text.endswith('.'):
        corrected_text += '.'
    return corrected_text

def process_audio_file(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language=VOICE_LANGUAGE)
        return text
    except sr.UnknownValueError:
        return None

def process_video_message(message):
    data = message.video_note
    if (data.file_size > MAX_MESSAGE_SIZE):
        reply = f"Video is too long. Maximum size: {MAX_MESSAGE_SIZE} bytes."
        return bot.reply_to(message, reply)

    file_url = "https://api.telegram.org/file/bot{}/{}".format(
        bot.token,
        bot.get_file(data.file_id).file_path
    )

    file_path = download_video(file_url)
    convert_to_ogg(file_path)
    convert_to_wav("new.ogg")
    text = process_audio_file("new.wav")

    if not text:
        return bot.reply_to(message, "Sorry, message is not recognized!.")

    text_with_punctuation = add_punctuation(text)
    bot.reply_to(message, f"Video to text: {text_with_punctuation}")
    cleanup_files(["new.ogg", "new.wav"])

def process_audio_message(message):
    data = message.voice
    if (data.file_size > MAX_MESSAGE_SIZE) or (data.duration > MAX_MESSAGE_DURATION):
        reply = f"Voice message is too long. Maximum size: {MAX_MESSAGE_DURATION} sec."
        return bot.reply_to(message, reply)

    file_url = "https://api.telegram.org/file/bot{}/{}".format(
        bot.token,
        bot.get_file(data.file_id).file_path
    )

    file_path = download_file(file_url)
    convert_to_pcm16(file_path)
    text = process_audio_file("new.wav")

    if not text:
        return bot.reply_to(message, "Message is not recognized!.")

    text_with_punctuation = add_punctuation(text)
    bot.reply_to(message, f"voice to text: {text_with_punctuation}")
    cleanup_files(["new.wav", "voice_message.ogg"])
def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

bot.polling()