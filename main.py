import logging
import os
import time

from pydub import AudioSegment
from pytube import YouTube
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "7006568131:AAG4yYSVDicVB7ilXNYox8IEvjQ72LPvRKE"
DOWNLOAD_FOLDER = './'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

CHOOSING, TYPING_REPLY = range(2)

def start(update: Update, context: CallbackContext) -> int:
    user_name = update.message.from_user.first_name
    update.message.reply_text(f"Hello mr {user_name}! 🎵 Send me a YouTube link and choose the format (MP3 or MP4) "
                              "you want to download. If you need help, type /help.\n"
                              "/commands - List all available commands\n\n")
    return CHOOSING

def help(update: Update, context: CallbackContext) -> None:
    help_message = "How to use:\n\n" \
      "1. Send the /start command to initiate the conversation.\n" \
      "2. Send the YouTube link you want to convert and choose MP3 or MP4.\n" \
      "3. Wait for the download and conversion to complete.\n" \
      "4. Use the /help command to display this help message.\n" \
      "5. Use the /donate command to support this bot.\n\n" \
      "Enjoy converting your favorite YouTube videos! 🎵"
    update.message.reply_text(help_message)

def download_audio(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    youtube_url = update.message.text

    try:
        # Download the YouTube video
        yt = YouTube(youtube_url)
        video_title = yt.title
        video_thumbnail = yt.thumbnail_url

        # Ask user for confirmation
        context.user_data['youtube_url'] = youtube_url
        context.user_data['video_title'] = video_title
        context.user_data['video_thumbnail'] = video_thumbnail

        # Send confirmation message with thumbnail and buttons
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Yes')], [KeyboardButton('No')]], one_time_keyboard=True)
        update.message.reply_photo(photo=video_thumbnail,
                                    caption=f"Are you sure you want to download:\n\n{video_title}?\n\n",
                                    reply_markup=reply_markup)
        return CHOOSING

    except Exception as e:
        logging.error(f"Error processing YouTube link: {e}")
        update.message.reply_text("Error processing YouTube link. Please try again. 💔")
        return ConversationHandler.END

def confirm_download(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.lower()
    if user_input == 'yes':
        # Ask user for format choice
        update.message.reply_text("Choose the format you want :", 
                                  reply_markup=ReplyKeyboardMarkup([['MP3', 'MP4']], one_time_keyboard=True))
        return TYPING_REPLY
    else:
        update.message.reply_text("Download canceled. If you need help, type /help.")
        return ConversationHandler.END

def choose_format(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.lower()
    if user_input == 'mp3':
        return download_mp3(update, context)
    elif user_input == 'mp4':
        return download_mp4(update, context)
    else:
        update.message.reply_text("Invalid format choice. Please choose MP3 or MP4.")
        return TYPING_REPLY

def download_mp3(update: Update, context: CallbackContext) -> int:
    try:
        message = update.message.reply_text('Downloading... Please wait. ❤')
        time.sleep(1)
        youtube_url = context.user_data.get('youtube_url')
        video_title = context.user_data.get('video_title')

        # Download the YouTube video
        yt = YouTube(youtube_url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_stream.download(DOWNLOAD_FOLDER)
        message.edit_text("Converting ... ❤")
        time.sleep(1)
        # Convert MP4 to MP3
        audio = AudioSegment.from_file(video_stream.default_filename)
        mp3_file_path = os.path.join(DOWNLOAD_FOLDER, f"{video_title}.mp3")
        audio.export(mp3_file_path, format="mp3", bitrate="320k")
        message.edit_text("Uploading ... ❤")
        time.sleep(1)
        # Send the converted audio file
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(mp3_file_path, 'rb'))
        message.edit_text("Done ... ❤")
        time.sleep(1)
        # Clean up: delete the downloaded video and converted MP3
        os.remove(video_stream.default_filename)
        os.remove(mp3_file_path)

        update.message.reply_text("Download complete! If you like it, donate to support us: /donate ❤")
        return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error downloading or converting file: {e}")
        update.message.reply_text("Error downloading or converting file. Please try again. 💔")
        return ConversationHandler.END

def download_mp4(update: Update, context: CallbackContext) -> int:
    try:
        message = update.message.reply_text('Downloading... Please wait. ❤')
        time.sleep(1)
        youtube_url = context.user_data.get('youtube_url')
        video_title = context.user_data.get('video_title')

        # Download the YouTube video
        yt = YouTube(youtube_url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_stream.download(DOWNLOAD_FOLDER)
        message.edit_text("Uploading ... ❤")
        time.sleep(1)
        # Send the MP4 video file
        context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_stream.default_filename, 'rb'))
        message.edit_text("Done ... ❤")
        time.sleep(1)
        # Clean up: delete the downloaded video
        os.remove(video_stream.default_filename)

        update.message.reply_text("Download complete! If you like it, donate to support us: /donate ❤")
        return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        update.message.reply_text("Error downloading file. Please try again. 💔")
        return ConversationHandler.END

def donate(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('If you would like to support this bot, you can donate to \n \n '
                              '[THbrJSW4keFSbWHJGfPataZ9G8sHNCNqPD] USDT-TRC20.\n \n'
                              'Thank You So Much!  you can use the bot without any problem. '
                              'Send /start to start the bot')

def commands_list(update: Update, context: CallbackContext) -> None:
    commands = "/start - Start the bot\n" \
               "/help - Display this help message\n" \
               "/donate - Support this bot\n" \
               "/commands - List all available commands"
    update.message.reply_text(commands)

def odownload(update: Update, context: CallbackContext) -> int:
    # Clear user data
    context.user_data.clear()
    # Restart the conversation handler
    return start(update, context)

def main() -> None:
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command and message handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("donate", donate))
    dp.add_handler(CommandHandler("commands", commands_list))
    dp.add_handler(CommandHandler("odownload", odownload))  # New command for downloading other video

    # Add conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, download_audio)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Yes|No)$'), confirm_download)],
            TYPING_REPLY: [MessageHandler(Filters.regex('^(MP3|MP4)$'), choose_format)],
        },
        fallbacks=[],
    )
    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
