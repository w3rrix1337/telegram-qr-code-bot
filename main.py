import os
import logging
import qrcode
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n"
        "Я — бот для создания QR-кодов. "
        "Просто **отправь мне любой текст или ссылку**, и я превращу это в QR-код!"
    )

async def generate_qr_code(update: Update, context):
    data_to_encode = update.message.text
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, 
        border=4,
    )
    qr.add_data(data_to_encode)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"qr_code_{update.effective_chat.id}.png"
    img.save(filename)

    try:
        await update.message.reply_photo(
            photo=open(filename, 'rb'),
            caption=f"✅ Ваш QR-код для: `{data_to_encode[:50]}...`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка при отправке: {e}")
    finally:
        os.remove(filename)
        logging.info(f"Временный файл {filename} удален.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr_code))

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
