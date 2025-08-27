import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from PIL import Image
import img2pdf

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from BotFather
TOKEN = "7922254969:AAF255dJG6x7VVqjDkXP00gFaNc60ULdA4s"

# Developer information
DEVELOPER = "👨‍💻 Latiful Hassan Zihan 🇵🇸"
NATIONALITY = "Bangladeshi 🇧🇩"
USERNAME = "@alwayszihan"

# Define conversion options
CONVERSION_OPTIONS = {
    "png_to_jpg": {"label": "🖼️ PNG to JPG", "input": "image", "output": "jpg"},
    "jpg_to_png": {"label": "📷 JPG to PNG", "input": "image", "output": "png"},
    "jpg_to_pdf": {"label": "📄 JPG to PDF", "input": "image", "output": "pdf"},
    "png_to_pdf": {"label": "📄 PNG to PDF", "input": "image", "output": "pdf"},
    # Add more conversion options as needed
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with the inline keyboard when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("🖼️ PNG to JPG", callback_data="png_to_jpg")],
        [InlineKeyboardButton("📷 JPG to PNG", callback_data="jpg_to_png")],
        [InlineKeyboardButton("📄 JPG to PDF", callback_data="jpg_to_pdf")],
        [InlineKeyboardButton("📄 PNG to PDF", callback_data="png_to_pdf")],
        [InlineKeyboardButton("👨‍💻 Developer Info", callback_data="developer_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 Welcome to File Converter Bot!\n\n"
        "Please select a conversion option: 👇",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the callback queries from the inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "developer_info":
        await developer_info(update, context)
        return
    
    if query.data in CONVERSION_OPTIONS:
        context.user_data["conversion_type"] = query.data
        option = CONVERSION_OPTIONS[query.data]
        
        await query.edit_message_text(
            text=f"🔄 Selected: {option['label']}\n\n"
                 f"Please send me the file you want to convert. 📎"
        )
    else:
        await query.edit_message_text(text="❌ Invalid option selected.")

async def developer_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show developer information."""
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"🧑‍💻 <b>Developer Information</b>\n\n"
             f"<b>Name:</b> {DEVELOPER}\n"
             f"<b>Nationality:</b> {NATIONALITY}\n"
             f"<b>Username:</b> {USERNAME}\n\n"
             f"Thank you for using this bot! ❤️",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the document to be converted."""
    user = update.message.from_user
    conversion_type = context.user_data.get("conversion_type")
    
    if not conversion_type:
        await update.message.reply_text("❌ Please select a conversion option first!")
        return
    
    # Get file info
    file = await update.message.document.get_file()
    file_extension = update.message.document.file_name.split('.')[-1].lower()
    input_filename = f"input_{user.id}.{file_extension}"
    output_extension = CONVERSION_OPTIONS[conversion_type]["output"]
    output_filename = f"output_{user.id}.{output_extension}"
    
    # Download the file
    await file.download_to_drive(input_filename)
    
    # Process the conversion
    try:
        if conversion_type in ["png_to_jpg", "jpg_to_png"]:
            # Image to image conversion
            with Image.open(input_filename) as img:
                if img.mode in ('RGBA', 'LA'):
                    # Create a white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                img.save(output_filename, format=output_extension.upper())
                
        elif conversion_type in ["jpg_to_pdf", "png_to_pdf"]:
            # Image to PDF conversion
            with open(output_filename, "wb") as f:
                f.write(img2pdf.convert(input_filename))
        
        # Send the converted file back to user
        with open(output_filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ Conversion complete!\n\n"
                        f"Converted using {CONVERSION_OPTIONS[conversion_type]['label']}\n"
                        f"By {DEVELOPER}"
            )
        
        # Clean up files
        os.remove(input_filename)
        os.remove(output_filename)
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        await update.message.reply_text("❌ Error during conversion. Please try again with a different file.")
        
        # Clean up files if they exist
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with information about how to use the bot."""
    await update.message.reply_text(
        "🤖 <b>File Converter Bot Help</b>\n\n"
        "1. Click /start to begin\n"
        "2. Select the conversion type from the menu\n"
        "3. Send the file you want to convert\n"
        "4. Receive your converted file!\n\n"
        "Supported conversions:\n"
        "• 🖼️ PNG to JPG\n"
        "• 📷 JPG to PNG\n"
        "• 📄 JPG to PDF\n"
        "• 📄 PNG to PDF\n\n"
        f"Developer: {DEVELOPER}",
        parse_mode="HTML"
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to the main menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🖼️ PNG to JPG", callback_data="png_to_jpg")],
        [InlineKeyboardButton("📷 JPG to PNG", callback_data="jpg_to_png")],
        [InlineKeyboardButton("📄 JPG to PDF", callback_data="jpg_to_pdf")],
        [InlineKeyboardButton("📄 PNG to PDF", callback_data="png_to_pdf")],
        [InlineKeyboardButton("👨‍💻 Developer Info", callback_data="developer_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🤖 Welcome to File Converter Bot!\n\n"
             "Please select a conversion option: 👇",
        reply_markup=reply_markup
    )

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(png_to_jpg|jpg_to_png|jpg_to_pdf|png_to_pdf|developer_info)$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()