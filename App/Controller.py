# -*- coding: utf-8 -*-
# @Time： 2023/3/12 10:40 
# @FileName: Controller.py
# @Software： PyCharm
# @GitHub: KimmyXYC
import asyncio
import telebot
from App import Event
from loguru import logger
from telebot import util
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage


class BotRunner(object):
    def __init__(self, config):
        self.bot = config.bot
        self.proxy = config.proxy

    def botcreate(self):
        bot = AsyncTeleBot(self.bot.botToken, state_storage=StateMemoryStorage())
        return bot, self.bot

    def run(self):
        # print(self.bot)
        logger.success("Bot Start")
        bot, _config = self.botcreate()
        if self.proxy.status:
            from telebot import asyncio_helper
            asyncio_helper.proxy = self.proxy.url
            logger.success("Proxy Set")

        @bot.message_handler(commands=["start", "help"])
        async def handle_command(message):
            user_id = message.chat.id
            if user_id in self.bot.master:
                await Event.help_info(bot, message, True)
            else:
                await Event.help_info(bot, message, False)

        @bot.message_handler(commands=["short"])
        async def handle_command(message):
            command_args = message.text.split()
            if len(command_args) == 1:
                await bot.reply_to(message, "格式错误, 格式应为 /short [URL] (short)")
            elif len(command_args) == 2:
                url = command_args[1]
                await Event.shorten_url(bot, message, url)
            elif len(command_args) == 3:
                url = command_args[1]
                short = command_args[2]
                await Event.shorten_url(bot, message, url, short)
            else:
                await bot.reply_to(message, "格式错误, 格式应为 /short [URL] (short)")

        @bot.message_handler(commands=["set"])
        async def handle_command(message):
            command_args = message.text.split()
            if len(command_args) == 1:
                await bot.reply_to(message, "格式错误, 格式应为 /set [URL]")
            elif len(command_args) == 2:
                url = command_args[1]
                await Event.set_url(bot, message, url)
            else:
                await bot.reply_to(message, "格式错误, 格式应为 /set [URL]")

        @bot.message_handler(commands=["setdefault"])
        async def handle_command(message):
            user_id = message.chat.id
            if user_id in self.bot.master:
                command_args = message.text.split()
                if len(command_args) == 1:
                    await bot.reply_to(message, "格式错误, 格式应为 /setdefault [URL]")
                elif len(command_args) == 2:
                    url = command_args[1]
                    await Event.set_url(bot, message, url, is_admin=True)
                else:
                    await bot.reply_to(message, "格式错误, 格式应为 /setdefault [URL]")
            else:
                await bot.reply_to(message, "你不是管理员哦")

        from telebot import asyncio_filters
        bot.add_custom_filter(asyncio_filters.IsAdminFilter(bot))
        bot.add_custom_filter(asyncio_filters.ChatFilter())
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))

        async def main():
            await asyncio.gather(bot.polling(non_stop=True, allowed_updates=util.update_types))

        asyncio.run(main())
