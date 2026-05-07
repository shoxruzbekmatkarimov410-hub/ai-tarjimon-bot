import telebot
from telebot import types
import pytesseract
from PIL import Image
import os
import requests
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = '8017343871:AAFagBzBdvTr7f7SxhqEv6BOpGSlCuWu2Do'
bot = telebot.TeleBot(TOKEN)

app = Flask('')
@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def translate_text(text, to_lang):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to_lang}&dt=t&q={text}"
        response = requests.get(url, timeout=10)
        return response.json()[0][0][0]
    except:
        return "Tarjimada xatolik yuz berdi."

def tillar_menusi():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data='uz'),
        types.InlineKeyboardButton("🇺🇸 English", callback_data='en'),
        types.InlineKeyboardButton("🇷🇺 Ruscha", callback_data='ru'),
        types.InlineKeyboardButton("🇹🇷 Turkcha", callback_data='tr')
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men Render serveridaman. Matn yoki rasm yuboring. 🚀")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    msg = bot.reply_to(message, "Rasm tahlil qilinmoqda... 🔍")
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("temp.jpg", 'wb') as f:
        f.write(downloaded_file)
    try:
        text = pytesseract.image_to_string(Image.open("temp.jpg"))
        if text.strip():
            bot.edit_message_text(f"Topilgan matn:\n\n`{text.strip()}`\n\nTilni tanlang:", 
                                 message.chat.id, msg.message_id, parse_mode="Markdown", reply_markup=tillar_menusi())
        else:
            bot.edit_message_text("Rasmda matn topilmadi.", message.chat.id, msg.message_id)
    finally:
        if os.path.exists("temp.jpg"): os.remove("temp.jpg")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.reply_to(message, "Matn qabul qilindi. Tilni tanlang:", reply_markup=tillar_menusi())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    til = call.data
    text = ""
    if call.message.text and "Topilgan matn:" in call.message.text:
        text = call.message.text.split("\n\n")[1].replace("Tilni tanlang:", "").strip()
    elif call.message.reply_to_message:
        text = call.message.reply_to_message.text
    
    if text:
        natija = translate_text(text, til)
        bot.edit_message_text(f"✅ Tarjima:\n\n`{natija}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.polling(none_stop=True)
