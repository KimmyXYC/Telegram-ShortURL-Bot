# -*- coding: utf-8 -*-
# @Time： 2023/3/12 10:40 
# @FileName: Event.py
# @Software： PyCharm
# @GitHub: KimmyXYC
import telebot
import aiohttp
import json
from loguru import logger
from utils.Parameter import get_parameter, save_config, save_default_config


async def help_info(bot, message, is_admin):
    _info = "短链接Bot, 中括号为必填参数，小括号为可选参数"
    _use = "/short [URL] (short)  缩短链接\n/set [URL] 设置后端地址"
    _admin = "/setdefault [URL] 设置默认后端 (管理员)"
    _url = "https://github.com/KimmyXYC/Telegram-ShortURL-Bot"
    if is_admin:
        _message = f"{_info}\n\n{_use}\n{_admin}\n\n开源地址: {_url}"
    else:
        _message = f"{_info}\n\n{_use}\n\n开源地址: {_url}"

    await bot.reply_to(
        message,
        _message,
        disable_web_page_preview=True,
    )


async def shorten_url(bot, message, url, short=""):
    server = get_parameter("user", message.chat.id, "URL")
    if server == "":
        logger.error(f"User ID: {message.chat.id}  Backend Address Not Set")
        await bot.reply_to(
            message,
            f"生成失败, 后端地址未设置",
            disable_web_page_preview=True,
        )
    else:
        if short:
            params = {'url': url, 'short': short, 'encode': 'json'}
        else:
            params = {'url': url, 'short': short, 'encode': 'json'}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(server, params=params) as response:
                    if 'application/json' in response.headers['content-type']:
                        json_data = await response.json()
                    else:
                        text_data = await response.text()
                        json_data = json.loads(text_data)
                    _info = "短链接: "
                    if json_data["code"] == 0:
                        logger.success(f"User ID: {message.chat.id}  Get Short URL: {json_data['url']}")
                        await bot.reply_to(
                            message,
                            f"{_info}{json_data['url']}",
                            disable_web_page_preview=True,
                        )
                    else:
                        logger.error(f"User ID: {message.chat.id}  Can't Get Short URL: {json_data['msg']}")
                        await bot.reply_to(
                            message,
                            f"生成失败: {json_data['msg']}",
                            disable_web_page_preview=True,
                        )
        except Exception as e:
            logger.error(f"User ID: {message.chat.id}  Can't Get Short URL: {e}")
            await bot.reply_to(
                message,
                f"生成失败, 请检查后端地址是否有效: {e}",
                disable_web_page_preview=True,
            )


async def set_url(bot, message, url, is_admin=False):
    url = format_url(url)
    if is_admin:
        try:
            save_default_config(url)
            logger.success(f"Global Backend Setup Success: {url}")
            await bot.reply_to(
                message,
                f"全局后端设置成功: {url}",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Global Backend Setup Failed: {e}")
            await bot.reply_to(
                message,
                f"全局后端设置失败: {e}",
                disable_web_page_preview=True,
            )

    else:
        try:
            save_config(url, str(message.chat.id))
            logger.success(f"Personal Backend Setup Success: {url}")
            await bot.reply_to(
                message,
                f"个人后端设置成功: {url}",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Personal Backend Setup Failed: {e}")
            await bot.reply_to(
                message,
                f"个人后端设置失败: {e}",
                disable_web_page_preview=True,
            )


def format_url(url):
    if not url.startswith("http") and not url.startswith("https"):
        url = "http://" + url
    if url.endswith("/"):
        url = url[:-1]
    if url.endswith("/api/url"):
        return url
    else:
        return url + "/api/url"
