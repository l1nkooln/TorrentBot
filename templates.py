torrent_list_template="""<b>{id}</b> {name} {percentage}%
"""

torrent_data_template="""{name}
<b>{error}</b>
<b>Статус</b>: {status}
<b>Завантажено</b>: {percentage}%
<b>Залишилось</b>: {eta}
<b>Швидкість</b>: ⬇️{download_speed} - {upload_speed}⬆️

<b>Дирикторія</b>: {download_dir}
<b>Піри</b>: {peers_connected} з {peers_count}
"""

remove_torrent_template="""{name}
<b>Справді видалити?</b>

Виберіть метод
"""

torrent_add_template="""<b>Додано {id}</b>
{name}
"""

torrent_changed_template="""<b>Змінено {id}</b>
{name}
<b>{error}</b>
<b>Статус</b>: {status}
"""