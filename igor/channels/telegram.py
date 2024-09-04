import os
from igor.channels.base_channel import Channel
from igor.event import Event
from igor.response import Response
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
from igor.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class Telegram(Channel):
    def __init__(self, hub):
        super().__init__(hub)

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token is None:
            error = "TELEGRAM_BOT_TOKEN environment variable not set"
            logger.error(error)
            raise ValueError(error)

        self.application = ApplicationBuilder().token(token).build()

    async def start_listening(self):
        # setup handlers
        start_handler = CommandHandler("start", self.handle_start)
        message_handler = MessageHandler(
            filters.TEXT & (~filters.COMMAND), self.handle_message
        )
        # webapp_handler = MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.handle_webapp_data)

        self.application.add_handler(start_handler)
        self.application.add_handler(message_handler)
        # self.application.add_handler(webapp_handler)

        # start the bot
        await self.application.initialize()
        await self.application.start()

        if self.application.updater is None:
            logger.error("Unable to get application updater")
            return

        await self.application.updater.start_polling()

    async def stop_listening(self):
        await self.application.shutdown()

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat is None:
            logger.error("effective_chat is None in handle_start")
            return

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        event = self.channel_event_to_igor_event(update)
        setattr(event, "context", context.args)
        await self.hub.process_event(event)

    def channel_event_to_igor_event(self, event):
        # for now we're just handling commands and text messages
        update_type = self.get_update_type(event)

        content = ""
        if update_type == "message":
            content = event.message.text if event.message and event.message.text else ""
        elif update_type == "command":
            content = " ".join(event.context)

        event = Event(
            event_type=update_type or "unknown",
            content=content,
            channel="telegram",
            extra={"chat_id": event.effective_chat.id},
        )
        return event

    def get_update_type(self, update):
        """
        Determine the type of the update based on its content
        """
        if update.message:
            if update.message.text:
                if update.message.text.startswith("/"):
                    return "command"
                else:
                    return "message"
            elif update.message.photo:
                return "photo"
            elif update.message.voice:
                return "voice"
            else:
                return "other_message"

    async def send_response(self, event: Event, response: Response):
        # no response.content
        res = await self.application.bot.send_message(
            chat_id=event.extra["chat_id"], text=response.content
        )
