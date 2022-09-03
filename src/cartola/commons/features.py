from unidecode import unidecode


def compute_slug(nickname: str) -> str:
    return unidecode(nickname.lower().replace(" ", "-"))
