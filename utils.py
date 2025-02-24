def chunk_array(array, chunk_size):
    for i in range(0, len(array), chunk_size):
        chunk = array[i:i + chunk_size]
        is_last = (i + chunk_size) >= len(array)
        yield chunk, is_last

def format_data_units(bytes_value):
    units = ["Б", "Кб", "Мб", "Гб", "Тб", "Пб"]
    size = float(bytes_value)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} Пб"

def format_speed_units(speed_bps):
    units = ["Б/с", "Кб/с", "Мб/с", "Гб/с", "Тб/с", "Пб/с"]
    speed = float(speed_bps)
    for unit in units:
        if speed < 1024:
            return f"{speed:.2f} {unit}"
        speed /= 1024
    return f"{speed:.2f} Пб/с"

def translate_status(status):
    translations = {
        "stopped": "зупинено",
        "check pending": "очікує перевірки",
        "checking": "перевіряється",
        "download pending": "очікує завантаження",
        "downloading": "завантажується",
        "seed pending": "очікує роздачі",
        "seeding": "роздається",
    }
    return translations.get(status.lower(), "невідомий статус")
