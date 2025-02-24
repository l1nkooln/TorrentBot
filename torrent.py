import io
import logging
import time

from transmission_rpc import Client, Torrent

from config import RPC_HOST, RPC_PORT
from utils import format_speed_units, translate_status

while True:
    try:
        client = Client(host=RPC_HOST, port=RPC_PORT)
        break
    except:
        logging.error("Failed connecting to transmission. Another try after 1 minute")
        time.sleep(60)


def get_torrents_list() -> list[dict[str, int | str | float]]:
    response = []
    torrents = client.get_torrents()
    for torrent in torrents:
        data = {"id": torrent.id, "hash": torrent.hashString, "status": torrent.status, "error": torrent.error_string}
        if len(torrent.name) <= 20:
            data["name"] = torrent.name
        else:
            data["name"] = f"{torrent.name[:10]}...{torrent.name[-10:]}"
        data["percentage"] = torrent.progress
        response.append(data)
    return response


def get_torrent(torrent_id: int) -> dict:
    torrent = client.get_torrent(torrent_id)

    data = {
        "id": torrent_id,
        "percentage": torrent.progress,
        "status": translate_status(torrent.status),
        "download_dir": torrent.download_dir,
        "eta": torrent.format_eta(),
        "error": torrent.error_string,
        "peers_connected": torrent.peers_connected,
        "download_speed": format_speed_units(torrent.rate_download),
        "upload_speed": format_speed_units(torrent.rate_upload)
    }

    if len(torrent.name) <= 40:
        data["name"] = torrent.name
    else:
        data["name"] = f"{torrent.name[:20]}...{torrent.name[-20:]}"

    peers_count = 0
    for peer in torrent.peers_from.values():
        peers_count += peer

    data["peers_count"] = peers_count

    return data

def stop_torrent(torrent_id: int):
    client.stop_torrent(torrent_id)

def start_torrent(torrent_id: int):
    client.start_torrent(torrent_id)

def remove_torrent(torrent_id: int, delete_data: bool):
    client.remove_torrent(torrent_id, delete_data=delete_data)

def add_torrent_bytes(torrent_bytes: io.BytesIO)-> Torrent:
    return client.add_torrent(torrent_bytes)

def add_torrent_url(url: str)-> Torrent:
    return client.add_torrent(url)