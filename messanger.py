from aiogram import Bot

from config import ADMINS
from messages import torrent_changed_msg
from torrent import get_torrents_list

last_status = {}

async def check_torrent_status(bot: Bot):
    global last_status
    torrents = get_torrents_list()
    for torrent in torrents:
        if torrent["hash"] in last_status.keys():
            if torrent["status"] != last_status[torrent["hash"]] or torrent["error"] != "":
                for admin in ADMINS:
                    await torrent_changed_msg(torrent["id"], admin, bot)
        else:
            for admin in ADMINS:
                await torrent_changed_msg(torrent["id"], admin, bot)

    last_status = {}

    for torrent in torrents:
        last_status[torrent["hash"]] = torrent["status"]

def renew_status():
    global last_status
    last_status = {}
    torrents = get_torrents_list()
    for torrent in torrents:
        last_status[torrent["hash"]] = torrent["status"]