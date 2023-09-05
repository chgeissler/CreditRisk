from unidecode import unidecode


def remove_accents(text: str) -> str:
    """
    Remove accents from text
    :param
        text: str to remove accents from
    :return:
        str without accents
    """
    if text is None:
        return None
    else:
        return unidecode(text)


def compactify(text: str) -> str:
    """
    Remove spaces and newlines from text
    :param
        text: str to remove spaces and newlines from
    :return:
        str without spaces and newlines
    """
    if text is None:
        return None
    else:
        return text.replace(" ", "").replace("\n", "")


def normalize(text: str) -> str:
    """
    Remove spaces and newlines from text
    :param
        text: str to remove spaces and newlines from
    :return:
        str without spaces and newlines
    """
    if text is None:
        return None
    else:
        return compactify(remove_accents(text)).upper()
