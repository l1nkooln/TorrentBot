import asyncio
import io
from typing import Any

from aiogram import Dispatcher, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
import logging


from config import TOKEN
from messages import torrents_list_msg, torrent_msg, stop_torrent_msg, start_torrent_msg, remove_torrent_msg, \
    remove_torrent_callback_msg, handle_auth, add_torrent_msg
from messanger import check_torrent_status, renew_status

dp = Dispatcher()

@dp.message()
async def handle_message(message: Message, bot: Bot) -> None:
    if not await handle_auth(message.chat.id, bot): return
    if message.text == "/list":
        await torrents_list_msg(message.chat.id, bot)
        return
    await add_torrent_msg(message, bot)

@dp.callback_query()
async def callback_query_handler(callback_query: types.CallbackQuery, bot: Bot) -> Any:
    data = callback_query.data.split(":") #state, data

    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id

    if not await handle_auth(chat_id, bot):
        return

    try:
        if data[0] == "select":
            await bot.answer_callback_query(callback_query.id, show_alert=False)
            await torrent_msg(int(data[1]), message_id, chat_id, bot)

        elif data[0] == "list":
            await bot.answer_callback_query(callback_query.id, show_alert=False)
            await bot.delete_message(chat_id, message_id)
            await torrents_list_msg(chat_id, bot)

        elif data[0] == "stop":
            await stop_torrent_msg(int(data[1]), callback_query.id, bot)
            renew_status()
            await torrent_msg(int(data[1]), message_id, chat_id, bot)

        elif data[0] == "start":
            await start_torrent_msg(int(data[1]), callback_query.id, bot)
            renew_status()
            await torrent_msg(int(data[1]), message_id, chat_id, bot)

        elif data[0] == "remove":
            await bot.answer_callback_query(callback_query.id, show_alert=False)
            await remove_torrent_msg(int(data[1]), message_id, chat_id, bot)

        elif data[0] == "remove_with_data":
            await remove_torrent_callback_msg(int(data[1]), callback_query.id, bot, True)
            await bot.delete_message(chat_id, message_id)
            await torrents_list_msg(chat_id, bot)

        elif data[0] == "remove_without_data":
            await remove_torrent_callback_msg(int(data[1]), callback_query.id, bot, False)
            await bot.edit_message_text("виникла помилка",chat_id=chat_id, message_id=message_id)
            await torrents_list_msg(chat_id, bot)

    except Exception as e:
        print(e)
        await bot.delete_message(chat_id, message_id)
        await bot.answer_callback_query(callback_query.id, text="Помилка", show_alert=True)

async def check_status(bot: Bot) -> None:
    try:
        while True:
            await check_torrent_status(bot)
            await asyncio.sleep(120)
    except asyncio.CancelledError:
        logging.info("Cancelled checking task")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    renew_status()
    task = asyncio.create_task(check_status(bot))
    await dp.start_polling(bot)
    task.cancel()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    asyncio.run(main())