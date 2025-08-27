import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from PIL import Image
import img2pdf
from io import BytesIO

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from BotFather (replace with your actual token)
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
    "images_to_pdf": {"label": "📚 Multiple Images to PDF", "input": "image", "output": "pdf"},
    "developer_info": {"label": "👨‍💻 Developer Info", "input": "none", "output": "none"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with the inline keyboard when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_jpg"]["label"], callback_data="png_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_png"]["label"], callback_data="jpg_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_pdf"]["label"], callback_data="jpg_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_pdf"]["label"], callback_data="png_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["images_to_pdf"]["label"], callback_data="images_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["developer_info"]["label"], callback_data="developer_info")]
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
    
    if query.data == "main_menu":
        await start_callback(update, context)
        return
    
    if query.data in CONVERSION_OPTIONS:
        context.user_data["conversion_type"] = query.data
        option = CONVERSION_OPTIONS[query.data]
        
        if query.data == "images_to_pdf":
            context.user_data["images_for_pdf"] = []
            await query.edit_message_text(
                text=f"🔄 Selected: {option['label']}\n\n"
                     f"Please send me the images one by one. Send /done when you're finished. 📎"
            )
        else:
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
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_jpg"]["label"], callback_data="png_to_jpg")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_png"]["label"], callback_data="jpg_to_png")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["jpg_to_pdf"]["label"], callback_data="jpg_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["png_to_pdf"]["label"], callback_data="png_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["images_to_pdf"]["label"], callback_data="images_to_pdf")],
        [InlineKeyboardButton(CONVERSION_OPTIONS["developer_info"]["label"], callback_data="developer_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🤖 Welcome to File Converter Bot!\n\n"
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

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the document to be converted."""
    user = update.message.from_user
    conversion_type = context.user_data.get("conversion_type")
    
    if not conversion_type:
        await update.message.reply_text("❌ Please select a conversion option first! Use /start to begin.")
        return
    
    # Get file info
    if update.message.document:
        file = await update.message.document.get_file()
        file_extension = update.message.document.file_name.split('.')[-1].lower()
    elif update.message.photo:
        # Handle photos
        file = await update.message.photo[-1].get_file()
        file_extension = "jpg"
    else:
        await update.message.reply_text("❌ Please send a valid file.")
        return
    
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
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                    else:
                        background.paste(img, mask=img.split()[1])  # 1 is the alpha channel for LA
                    img = background
                
                # Convert and save
                rgb_img = img.convert('RGB')
                rgb_img.save(output_filename, format=output_extension.upper(), quality=95)
                
        elif conversion_type in ["jpg_to_pdf", "png_to_pdf"]:
            # Single image to PDF conversion
            with Image.open(input_filename) as img:
                if img.mode in ('RGBA', 'LA'):
                    # Create a white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img, mask=img.split()[1])
                    img = background
                
                # Convert to RGB and save as PDF
                rgb_img = img.convert('RGB')
                rgb_img.save(output_filename, format='PDF', quality=100)
        
        elif conversion_type == "images_to_pdf":
            # Multiple images to PDF - store the image and wait for more
            if "images_for_pdf" not in context.user_data:
                context.user_data["images_for_pdf"] = []
            
            context.user_data["images_for_pdf"].append(input_filename)
            await update.message.reply_text("✅ Image received. Send another image or /done to create the PDF.")
            return
        
        # Send the converted file back to user
        with open(output_filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ Conversion complete!\n\n"
                        f"Converted using {CONVERSION_OPTIONS[conversion_type]['label']}\n"
                        f"By {DEVELOPER}"
            )
        
        # Clean up files
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        # Reset conversion type
        context.user_data["conversion_type"] = None
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        await update.message.reply_text("❌ Error during conversion. Please try again with a different file.")
        
        # Clean up files if they exist
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /done command for multiple images to PDF."""
    user = update.message.from_user
    conversion_type = context.user_data.get("conversion_type")
    
    if conversion_type != "images_to_pdf" or "images_for_pdf" not in context.user_data:
        await update.message.reply_text("❌ This command is only for finishing multiple images to PDF conversion.")
        return
    
    images = context.user_data["images_for_pdf"]
    if not images:
        await update.message.reply_text("❌ No images received. Please send images first.")
        return
    
    output_filename = f"output_{user.id}.pdf"
    
    try:
        # Prepare images for PDF conversion
        image_list = []
        for img_path in images:
            with Image.open(img_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img, mask=img.split()[1])
                    img = background
                rgb_img = img.convert('RGB')
                image_list.append(rgb_img)
        
        # Save first image as PDF and append others
        if image_list:
            image_list[0].save(output_filename, format='PDF', save_all=True, 
                              append_images=image_list[1:] if len(image_list) > 1 else [])
        
        # Send the converted file back to user
        with open(output_filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ PDF creation complete!\n\n"
                        f"Created from {len(images)} images\n"
                        f"By {DEVELOPER}"
            )
        
        # Clean up files
        for image in images:
            if os.path.exists(image):
                os.remove(image)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        # Reset conversion data
        context.user_data["conversion_type"] = None
        context.user_data["images_for_pdf"] = []
        
    except Exception as e:
        logger.error(f"Error during PDF creation: {e}")
        await update.message.reply_text("❌ Error during PDF creation. Please try again.")
        
        # Clean up files if they exist
        for image in images:
            if os.path.exists(image):
                os.remove(image)
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
        "<b>Supported conversions:</b>\n"
        "• 🖼️ PNG to JPG\n"
        "• 📷 JPG to PNG\n"
        "• 📄 JPG to PDF\n"
        "• 📄 PNG to PDF\n"
        "• 📚 Multiple Images to PDF (send images one by one, then /done)\n\n"
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
    application.add_handler(CommandHandler("done", done_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()