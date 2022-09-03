from unidecode import unidecode


def compute_slug(nickname: str):
    return unidecode(nickname.lower().replace(" ", "-"))
