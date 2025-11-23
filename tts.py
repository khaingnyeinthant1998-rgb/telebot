import telebot
import asyncio
import edge_tts
import os
import threading
from flask import Flask

# --- Part 1: Dummy Web Server for Render (မဖြစ်မနေ ထည့်ရမည့်အပိုင်း) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running..."

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Part 2: Bot Logic ---
# Token အသစ်ပြန်ထုတ်ပြီးမှ ဒီမှာလာထည့်ပါ
TOKEN = '8528654999:AAG4xEPgWZYvzGqT6nSZNl8oigJrsJXNJEw' 
bot = telebot.TeleBot(TOKEN)

# Edge TTS Function
async def generate_voice(text, output_file):
    communicate = edge_tts.Communicate(text, "my-MM-ThihaNeural")
    await communicate.save(output_file)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ... မြန်မာ/English ကြိုက်သလို ရောရေးပို့နိုင်ပါပြီ။ 🎙️")

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    try:
        user_text = message.text
        
        # Loading msg
        msg = bot.reply_to(message, "အသံဖိုင် ပြောင်းနေပါသည်... 🔄")
        
        file_name = f"voice_{message.chat.id}.mp3"

        # Async loop run
        asyncio.run(generate_voice(user_text, file_name))

        # Send Audio
        with open(file_name, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                title="Mixed Language Audio", 
                caption=f"📝: {user_text[:50]}..."
            )

        # Cleanup
        os.remove(file_name)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
        print(f"Error: {e}")

if __name__ == '__main__':
    # Web Server ကို သီးသန့် Thread နဲ့ run ပါမယ်
    t = threading.Thread(target=run_web_server)
    t.start()

    print("Bot is running with Edge-TTS on Render...")
    bot.infinity_polling()
