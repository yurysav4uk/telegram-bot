import requests
import speech_recognition as sr
import logging
from telebot import TeleBot, logger
import soundfile as sf

# Установка токена вашего бота и других настроек
TELEGRAM_KEY = '7304494637:AAFxjsgnSmiMPD0tQKWm3Y27adM1VJurVoQ'
VOICE_LANGUAGE = 'ru-RU'
MAX_MESSAGE_SIZE = 50 * 1024 * 1024  # 50 MB (ограничение Telegram на размер файла)
MAX_MESSAGE_DURATION = 120  # seconds (ограничение Telegram на длительность аудиосообщения)

bot = TeleBot(TELEGRAM_KEY)  # pylint: disable=invalid-name

@bot.message_handler(commands=['start'])
def start_prompt(message):
    reply = ' '.join((
        "Press and hold the microphone button",
        "Say the phrase and release the button"
    ))
    return bot.reply_to(message, reply)

@bot.message_handler(content_types=['voice'])
def echo_voice(message):
    data = message.voice
    if (data.file_size > MAX_MESSAGE_SIZE) or (data.duration > MAX_MESSAGE_DURATION):
        reply = ' '.join((
            "Voice message is too big.",
            "Maximum duration: {} sec.".format(MAX_MESSAGE_DURATION),
            "Try speak shorter."
        ))
        return bot.reply_to(message, reply)

    file_url = "https://api.telegram.org/file/bot{}/{}".format(
        bot.token,
        bot.get_file(data.file_id).file_path
    )

    # Загрузка файла на локальное хранилище
    file_path = download_file(file_url)

    # Преобразование аудиофайла в формат PCM_16
    convert_to_pcm16(file_path)

    # Обработка аудиофайла
    text = process_audio_file("new.wav")

    if not text:
        return bot.reply_to(message, "Не понял вас, пожалуйста, повторите.")

    return bot.reply_to(message, text)

def download_file(file_url):
    file_path = "voice_message.ogg"
    with open(file_path, 'wb') as f:
        response = requests.get(file_url)
        f.write(response.content)
    return file_path

def convert_to_pcm16(file_path):
    data, samplerate = sf.read(file_path)
    sf.write('new.wav', data, samplerate, subtype='PCM_16')

def process_audio_file(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language=VOICE_LANGUAGE)
        return text
    except sr.UnknownValueError:
        return None

logger.setLevel(logging.DEBUG)
bot.delete_webhook()  # на всякий случай
bot.polling()