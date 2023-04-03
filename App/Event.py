# -*- coding: utf-8 -*-
# @Time： 2023/3/12 10:40 
# @FileName: Event.py
# @Software： PyCharm
# @GitHub: KimmyXYC
import telebot
import aiohttp
import json
from loguru import logger
from utils.Parameter import get_parameter, save_config, save_default_config, get_type_parameter


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
    backend_type = get_type_parameter("user", message.chat.id, "type")
    if server == "":
        logger.error(f"User ID: {message.chat.id}  Backend Address Not Set")
        await bot.reply_to(
            message,
            f"生成失败, 后端地址未设置",
            disable_web_page_preview=True,
        )
    else:
        if url.startswith("https://") or url.startswith("http://"):
            if short:
                params = {'url': url, 'short': short, 'encode': 'json'}
            else:
                params = {'url': url, 'encode': 'json'}
            if backend_type == "Url-Shorten-Worker":
                params = {'url': url}
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                if backend_type == "Url-Shorten-Worker":
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(server, json=params) as response:
                            if 'application/json' in response.headers['content-type']:
                                json_data = await response.json()
                            else:
                                text_data = await response.text()
                                json_data = json.loads(text_data)
                else:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(server, params=params) as response:
                            if 'application/json' in response.headers['content-type']:
                                json_data = await response.json()
                            else:
                                text_data = await response.text()
                                json_data = json.loads(text_data)
                _info = "短链接: "
                if backend_type == "UrlShorter":
                    if json_data["code"] == 0:
                        _url = json_data['url']
                        _status = True
                    else:
                        _url = json_data['msg']
                        _status = False
                elif backend_type == "Url-Shorten-Worker":
                    if json_data["status"] == 200:
                        _url = server + json_data['key']
                        _status = True
                    else:
                        _url = ""
                        _status = False
                else:
                    _url = ""
                    _status = False
                    logger.error(f"User ID: {message.chat.id}  Not Effective Backend")
                if _status:
                    logger.success(f"User ID: {message.chat.id}  Get Short URL: {_url}")
                    await bot.reply_to(
                        message,
                        f"{_info}`{_url}`",
                        disable_web_page_preview=True,
                        parse_mode="Markdown",
                    )
                else:
                    logger.error(f"User ID: {message.chat.id}  Can't Get Short URL: {_url}")
                    await bot.reply_to(
                        message,
                        f"生成失败: {_url}",
                        disable_web_page_preview=True,
                    )
            except Exception as e:
                logger.error(f"User ID: {message.chat.id}  Can't Get Short URL: {e}")
                await bot.reply_to(
                    message,
                    f"生成失败, 请检查后端地址是否有效: {e}",
                    disable_web_page_preview=True,
                )
        else:
            logger.error(f"User ID: {message.chat.id}  Not Effective URL")
            await bot.reply_to(
                message,
                f"非法的网址",
                disable_web_page_preview=True,
            )


async def set_url(bot, call, url, backend, is_admin=False):
    url = format_url(url, backend)
    if is_admin:
        save_default_config(url, backend)
        logger.success(f"Global Backend Setup Success: {url}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"全局后端设置成功: {url}",
            disable_web_page_preview=True,
        )

    else:
        save_config(url, str(call.message.chat.id), backend)
        logger.success(f"Personal Backend Setup Success: {url}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"个人后端设置成功: {url}",
            disable_web_page_preview=True,
        )


async def choose_url(bot, message, url):
    save_config(url, str(message.chat.id), "")
    markup = telebot.types.InlineKeyboardMarkup()
    btn_url_shorter = telebot.types.InlineKeyboardButton(
        text='UrlShorter', callback_data='UrlShorter')
    btn_url_shorten_worker = telebot.types.InlineKeyboardButton(
        text='Url-Shorten-Worker', callback_data='Url-Shorten-Worker')
    markup.add(btn_url_shorter, btn_url_shorten_worker)
    await bot.send_message(message.chat.id, '请选择后端类型', reply_markup=markup)


async def choose_default_url(bot, message, url):
    save_default_config(url, "")
    markup = telebot.types.InlineKeyboardMarkup()
    btn_url_shorter = telebot.types.InlineKeyboardButton(
        text='UrlShorter', callback_data='UrlShorter')
    btn_url_shorten_worker = telebot.types.InlineKeyboardButton(
        text='Url-Shorten-Worker', callback_data='Url-Shorten-Worker')
    markup.add(btn_url_shorter, btn_url_shorten_worker)
    await bot.send_message(message.chat.id, '请选择默认后端类型', reply_markup=markup)


def format_url(url, back_end):
    if not url.startswith("http") and not url.startswith("https"):
        url = "http://" + url
    if url.endswith("/"):
        url = url[:-1]
    if back_end == "UrlShorter":
        if url.endswith("/api/url"):
            return url
        else:
            return url + "/api/url"
    else:
        return url
