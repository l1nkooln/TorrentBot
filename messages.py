import io
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from transmission_rpc import Torrent

from config import ADMINS
from templates import torrent_list_template, torrent_data_template, remove_torrent_template, torrent_add_template, \
    torrent_changed_template
from torrent import get_torrents_list, get_torrent, stop_torrent, start_torrent, remove_torrent, add_torrent_bytes, \
    add_torrent_url
from utils import chunk_array

async def handle_auth(chat_id: int, bot: Bot) -> bool:
    if chat_id not in ADMINS:
        logging.warning(f"Unauthorised {chat_id}")
        await bot.send_message(chat_id, "Unauthorised")
        for admins in ADMINS:
            await bot.send_message(admins, f"Unauthorised {chat_id}")
        return False
    return True

async def torrents_list_msg(chat_id: int, bot: Bot) -> None:
    torrents_data = get_torrents_list()

    response = []
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Оновити", callback_data=f"list"), width=1)



    for torrent_data_element in torrents_data:
        response.append(torrent_list_template.format(**torrent_data_element))

    for part, is_last in chunk_array(response, 40):
        if is_last:
            msg = await bot.send_message(
                chat_id=chat_id,
                text="".join(part))

            for torrent_data_element in torrents_data:
                builder.button(text=f"{torrent_data_element["id"]}",
                               callback_data=f"select:{torrent_data_element["id"]}")

            builder.adjust(1, 4)

            await bot.edit_message_reply_markup(message_id=msg.message_id, chat_id=msg.chat.id,
                                                reply_markup=builder.as_markup())
            return
        await bot.send_message(
            chat_id=chat_id,
            text="".join(part))


async def torrent_msg(torrent_id: int, message_id: int, chat_id: int, bot: Bot) -> None:
    await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text="Завантажуєм...")
    torrent = get_torrent(torrent_id)

    response = torrent_data_template.format(**torrent)
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Оновити", callback_data=f"select:{torrent_id}"))
    builder.row(InlineKeyboardButton(text="Запустити", callback_data=f"start:{torrent_id}"))
    builder.row(InlineKeyboardButton(text="Зупинити", callback_data=f"stop:{torrent_id}"))
    builder.row(InlineKeyboardButton(text="Видалити", callback_data=f"remove:{torrent_id}"))
    builder.row(InlineKeyboardButton(text="Список", callback_data=f"list"))

    builder.adjust(1,2,1,1)

    await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=response, reply_markup=builder.as_markup())


async def stop_torrent_msg(torrent_id: int, query_id: str, bot: Bot) -> None:
    try:
        stop_torrent(torrent_id)
        await bot.answer_callback_query(query_id, text="Зупинено успішно")
    except Exception as e:
        await bot.answer_callback_query(query_id, text=f"Невдача {e}")

async def start_torrent_msg(torrent_id: int, query_id: str, bot: Bot) -> None:
    try:
        start_torrent(torrent_id)
        await bot.answer_callback_query(query_id, text="Запущено успішно")
    except Exception as e:
        await bot.answer_callback_query(query_id, text=f"Невдача {e}")

async def remove_torrent_msg(torrent_id: int, message_id: int, chat_id: int, bot: Bot) -> None:
    torrent = get_torrent(torrent_id)

    response = remove_torrent_template.format(**torrent)
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"select:{torrent_id}"))
    builder.row(InlineKeyboardButton(text="З даними", callback_data=f"remove_with_data:{torrent_id}"),InlineKeyboardButton(text="Без даних", callback_data=f"remove_without_data:{torrent_id}"))
    await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=response, reply_markup=builder.as_markup())

async def remove_torrent_callback_msg(torrent_id: int, query_id: str, bot: Bot, with_data: bool) -> None:
    try:
        remove_torrent(torrent_id, with_data)
        await bot.answer_callback_query(query_id, text="Видалено успішно")
    except Exception as e:
        await bot.answer_callback_query(query_id, text=f"Невдача {e}")

async def add_torrent_msg(message: Message, bot: Bot) -> None:
    torrent: Torrent | None = None
    if message.document:
        try:
            if message.document.mime_type == "application/x-bittorrent":
                torrent_bytes: io.BytesIO | None = await bot.download(message.document.file_id)
                if torrent_bytes:
                    try:
                        torrent = add_torrent_bytes(torrent_bytes)
                    except Exception as e:
                        logging.error(e)
                        await bot.send_message(message.chat.id, "Помилка додавання")
                        return
            else:
                await bot.send_message(message.chat.id, "Не .torrent файл")
        except Exception as e:
            logging.error(e)
            await bot.send_message(message.chat.id, "Помилка додавання")

    if message.text:
        if message.text.startswith("http") or message.text.startswith("magnet"):
            try:
                torrent = add_torrent_url(message.text)
            except Exception as e:
                logging.error(e)
                await bot.send_message(message.chat.id, "Помилка додавання")
                return
        else:
            await bot.send_message(message.chat.id, "Це повідомлення не є http чи magnet посиланям")
            return

    if torrent:
        response = torrent_add_template.format(name=torrent.name, id=torrent.id)

        builder = InlineKeyboardBuilder()
        builder.button(text="Переглянути", callback_data=f"select:{torrent.id}")
        builder.button(text="Список", callback_data=f"list")
        builder.adjust(1,1)

        await bot.send_message(message.chat.id, response, reply_markup=builder.as_markup())

async def torrent_changed_msg(torrent_id: int, chat_id: int, bot: Bot) -> None:
    torrent = get_torrent(torrent_id)

    response = torrent_changed_template.format(**torrent)

    builder = InlineKeyboardBuilder()
    builder.button(text="Переглянути", callback_data=f"select:{torrent["id"]}")
    builder.button(text="Список", callback_data=f"list")
    builder.adjust(1, 1)

    await bot.send_message(chat_id, response, reply_markup=builder.as_markup())
