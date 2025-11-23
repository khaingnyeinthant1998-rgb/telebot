import telebot
import asyncio
import edge_tts
import os
import threading
import time
from flask import Flask

# --- Part 1: Keep-Alive Server for Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Edge TTS Bot is Running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Part 2: Bot Configuration ---
TOKEN = '8528654999:AAG4xEPgWZYvzGqT6nSZNl8oigJrsJXNJEw' # Token ထည့်ပါ
bot = telebot.TeleBot(TOKEN)

# Retry Logic ပါဝင်သော Edge TTS Function
async def generate_voice_with_retry(text, output_file, retries=3):
    # အသံကို Nular (Female) ပြောင်းထားပါတယ်
    voice = "my-MM-NularNeural" 
    
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            return True # အောင်မြင်ရင် function ကထွက်မယ်
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2) # ၂ စက္ကန့်စောင့်ပြီး ပြန်စမ်းမယ်
            else:
                raise e # ၃ ခါလုံးမရမှ Error ပြမယ်

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ... Edge TTS (မိန်းကလေးအသံ) ဖြင့် ဝန်ဆောင်မှုပေးနေပါသည်။")

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    user_text = message.text
    chat_id = message.chat.id
    file_name = f"voice_{chat_id}_{int(time.time())}.mp3"
    
    # Loading Message
    status_msg = bot.reply_to(message, "အသံဖိုင် ထုတ်လုပ်နေသည်... (Edge TTS) 🔄")

    try:
        # Async function ကို Run ခြင်း
        asyncio.run(generate_voice_with_retry(user_text, file_name))

        # အောင်မြင်ရင် ပို့မယ်
        with open(file_name, 'rb') as audio:
            bot.send_audio(
                chat_id, 
                audio, 
                title="Edge TTS Audio",
                caption=f"🗣️: {user_text[:40]}..."
            )
        
        # ဖိုင်ပြန်ဖျက်မယ်
        bot.delete_message(chat_id, status_msg.message_id)
        os.remove(file_name)

    except Exception as e:
        error_text = str(e)
        bot.edit_message_text(f"⚠️ စိတ်မကောင်းပါဘူး၊ Server ချိတ်မရပါ ဖြစ်နေပါတယ်။\nError: {error_text}", chat_id, status_msg.message_id)
        print(f"Final Error: {e}")
        # Error တက်ရင် ဖိုင်ကျန်ခဲ့မှာစိုးလို့ ဖျက်မယ်
        if os.path.exists(file_name):
            os.remove(file_name)

if __name__ == '__main__':
    # Server thread
    t = threading.Thread(target=run_web_server)
    t.start()
    
    print("Bot started with Retry Logic...")
    bot.infinity_polling()
