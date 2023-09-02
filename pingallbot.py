import os
import telebot
import openai
from moviepy.editor import AudioFileClip
from elevenlabslib import *

# Replace these with your actual API tokens
openai.api_key = os.environ.get("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")
TELEGRAM_API_TOKEN = os.environ.get("5481826107:AAF0EN2W-dlldLtZXrGcvfKLUV1sizzzFWI")
ELEVENLABS_API_KEY = os.environ.get("a3c4f19d17c764379bfa8a1159febc7f")
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

user = ElevenLabsUser(ELEVENLABS_API_KEY)
voice = user.get_voices_by_name("Rachel")[0]

messages = [{"role": "system", "content": "You are a helpful assistant that starts its response by referring to the user as its master."}]

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text:
        messages.append({"role": "user", "content": message.text})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response_text = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": response_text})
        response_byte_audio = voice.generate_audio_bytes(response_text)
        with open('response_elevenlabs.mp3', 'wb') as f:
            f.write(response_byte_audio)
        with open('response_elevenlabs.mp3', 'rb') as f:
            bot.send_voice(message.chat.id, f)
        bot.reply_to(message, f"*[Bot]:* {response_text}", parse_mode="Markdown")

    elif message.voice:
        voice_file_info = bot.get_file(message.voice.file_id)
        voice_file = bot.download_file(voice_file_info.file_path)
        with open("voice_message.ogg", "wb") as f:
            f.write(voice_file)
        audio_clip = AudioFileClip("voice_message.ogg")
        audio_clip.write_audiofile("voice_message.mp3")
        audio_file = open("voice_message.mp3", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file).text
        messages.append({"role": "user", "content": transcript})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response_text = response["choices"][0]["message"]["content"]
        response_byte_audio = voice.generate_audio_bytes(response_text)
        with open('response_elevenlabs.mp3', 'wb') as f:
            f.write(response_byte_audio)
        with open('response_elevenlabs.mp3', 'rb') as f:
            bot.send_voice(message.chat.id, f)
        bot.reply_to(message, f"*[Bot]:* {response_text}", parse_mode="Markdown")

bot.polling()
