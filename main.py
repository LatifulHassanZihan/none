import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from PIL import Image
from io import BytesIO
import time

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from BotFather (replace with your actual token)
TOKEN = "7922254969:AAF255dJG6x7VVqjDkXP00gFaNc60ULdA4s"

# API Keys (replace with your actual API keys)
REMOVE_BG_API_KEY = "tubgF1Th7KYswjvZoHjTgQKH"
CONVERT_API_SECRET = "a96cEUVfOnozhOibqUI5espOcVdKyQzv"

# Developer information
DEVELOPER = "👨‍💻 Latiful Hassan Zihan 🇵🇸"
NATIONALITY = "Bangladeshi 🇧🇩"
USERNAME = "@alwayszihan"

# Define conversion options
CONVERSION_OPTIONS = {
    "remove_bg": {"label": "✨ Remove Background", "input": "image", "output": "png"},
    "png_to_jpg": {"label": "🖼️ PNG to JPG", "input": "image", "output": "jpg"},
    "jpg_to_png": {"label": "📷 JPG to PNG", "input": "image", "output": "png"},
    "img_to_pdf": {"label": "📄 Image to PDF", "input": "image", "output": "pdf"},
    "pdf_to_img": {"label": "📄 PDF to Image", "input": "document", "output": "jpg"},
    "webp_to_png": {"label": "🖼️ WEBP to PNG", "input": "image", "output": "png"},
    "webp_to_jpg": {"label": "📷 WEBP to JPG", "input": "image", "output": "jpg"},
    "compress_image": {"label": "📦 Compress Image", "input": "image", "output": "jpg"},
    "developer_info": {"label": "👨‍💻 Developer Info", "input": "none", "output": "none"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with the inline keyboard when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton(CONVERSION_OPTIONS["remove_bg"]["label"], callback_data="remove_bg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_jpg"]["label"], callback_data="png_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_png"]["label"], callback_data="jpg_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["img_to_pdf"]["label"], callback_data="img_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["pdf_to_img"]["label"], callback_data="pdf_to_img")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["webp_to_png"]["label"], callback_data="webp_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["webp_to_jpg"]["label"], callback_data="webp_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["compress_image"]["label"], callback_data="compress_image")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["developer_info"]["label"], callback_data="developer_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 Welcome to Advanced File Converter Bot!\n\n"
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
    
    if query.data == "main_menu":
        await start_callback(update, context)
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

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command from callback."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(CONVERSION_OPTIONS["remove_bg"]["label"], callback_data="remove_bg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_jpg"]["label"], callback_data="png_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_png"]["label"], callback_data="jpg_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["img_to_pdf"]["label"], callback_data="img_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["pdf_to_img"]["label"], callback_data="pdf_to_img")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["webp_to_png"]["label"], callback_data="webp_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["webp_to_jpg"]["label"], callback_data="webp_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["compress_image"]["label"], callback_data="compress_image")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["developer_info"]["label"], callback_data="developer_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🤖 Welcome to Advanced File Converter Bot!\n\n"
             "Please select a conversion option: 👇",
        reply_markup=reply_markup
    )

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

def remove_background(image_data):
    """Remove background from image using Remove.bg API"""
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_data},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVE_BG_API_KEY},
        )
        
        if response.status_code == requests.codes.ok:
            return BytesIO(response.content)
        else:
            logger.error(f"Remove.bg API Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error in remove_background: {e}")
        return None

def convert_with_convertapi(input_file, conversion_type, filename):
    """Convert files using ConvertAPI"""
    try:
        # Map conversion types to ConvertAPI endpoints
        conversion_endpoints = {
            "png_to_jpg": "png/to/jpg",
            "jpg_to_png": "jpg/to/png",
            "img_to_pdf": "image/to/pdf",
            "pdf_to_img": "pdf/to/jpg",
            "webp_to_png": "webp/to/png",
            "webp_to_jpg": "webp/to/jpg",
            "compress_image": "optimize"
        }
        
        endpoint = conversion_endpoints.get(conversion_type)
        if not endpoint:
            return None
        
        # Prepare the request
        files = {'File': (filename, input_file.getvalue())}
        params = {'Secret': CONVERT_API_SECRET}
        
        # Send conversion request
        response = requests.post(
            f"https://v2.convertapi.com/convert/{endpoint}",
            files=files,
            data=params
        )
        
        if response.status_code == 200:
            # Get the download URL from response
            result = response.json()
            if 'Files' in result and len(result['Files']) > 0:
                download_url = result['Files'][0]['Url']
                # Download the converted file
                converted_file = requests.get(download_url)
                if converted_file.status_code == 200:
                    return BytesIO(converted_file.content)
        
        logger.error(f"ConvertAPI Error: {response.status_code}, {response.text}")
        return None
        
    except Exception as e:
        logger.error(f"Error in convert_with_convertapi: {e}")
        return None

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the document to be converted."""
    user = update.message.from_user
    conversion_type = context.user_data.get("conversion_type")
    
    if not conversion_type:
        await update.message.reply_text("❌ Please select a conversion option first! Use /start to begin.")
        return
    
    # Send waiting message
    processing_msg = await update.message.reply_text("⏳ Processing your file, please wait...")
    
    # Get file info
    try:
        if update.message.document:
            file = await update.message.document.get_file()
            file_extension = update.message.document.file_name.split('.')[-1].lower()
            filename = update.message.document.file_name
        elif update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_extension = "jpg"
            filename = f"photo_{user.id}.jpg"
        else:
            await update.message.reply_text("❌ Please send a valid file.")
            await processing_msg.delete()
            return
        
        # Download the file
        file_data = BytesIO()
        await file.download_to_memory(file_data)
        file_data.seek(0)
        
        # Process the conversion
        output_extension = CONVERSION_OPTIONS[conversion_type]["output"]
        output_filename = f"converted_{user.id}.{output_extension}"
        
        if conversion_type == "remove_bg":
            # Use Remove.bg API for background removal
            converted_data = remove_background(file_data)
            if not converted_data:
                await processing_msg.edit_text("❌ Failed to remove background. Please try again with a different image.")
                return
                
        else:
            # Use ConvertAPI for other conversions
            converted_data = convert_with_convertapi(
                file_data, 
                conversion_type,
                filename
            )
            
            if not converted_data:
                await processing_msg.edit_text("❌ Conversion failed. Please try again with a different file.")
                return
        
        # Send the converted file back to user
        converted_data.seek(0)
        await update.message.reply_document(
            document=converted_data,
            filename=output_filename,
            caption=f"✅ Conversion complete!\n\n"
                    f"Converted using {CONVERSION_OPTIONS[conversion_type]['label']}\n"
                    f"By {DEVELOPER}"
        )
        
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        try:
            await processing_msg.edit_text("❌ Error during conversion. Please try again with a different file.")
        except:
            await update.message.reply_text("❌ Error during conversion. Please try again with a different file.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with information about how to use the bot."""
    await update.message.reply_text(
        "🤖 <b>Advanced File Converter Bot Help</b>\n\n"
        "1. Click /start to begin\n"
        "2. Select the conversion type from the menu\n"
        "3. Send the file you want to convert\n"
        "4. Receive your converted file!\n\n"
        "<b>Supported conversions:</b>\n"
        "• ✨ Remove Background (using Remove.bg API)\n"
        "• 🖼️ PNG to JPG\n"
        "• 📷 JPG to PNG\n"
        "• 📄 Image to PDF\n"
        "• 📄 PDF to Image\n"
        "• 🖼️ WEBP to PNG\n"
        "• 📷 WEBP to JPG\n"
        "• 📦 Compress Image\n\n"
        "<b>Note:</b> This bot uses external APIs for conversion\n\n"
        f"<b>Developer:</b> {DEVELOPER}",
        parse_mode="HTML"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and send a message to the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()