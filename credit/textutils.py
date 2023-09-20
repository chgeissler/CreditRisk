from typing import Optional, Tuple

import numpy as np
from unidecode import unidecode
import re


def remove_accents(text: Optional[str]) -> Optional[str]:
    """
    Remove accents from text
    :param
        text: str, string to remove accents from
    :return:
        text without accents
    """
    if text is None:
        return None
    else:
        return unidecode(text)


def compactify(text: Optional[str]) -> Optional[str]:
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


def normalize(text: Optional[str],
              compactform: bool = False) -> Optional[str]:
    """
    Remove spaces and newlines from text
    :param compactform: boolean; if True, compactify text
    :param text: str to remove spaces and newlines from
    :return: str without spaces and newlines
    """
    if text is None:
        return None
    else:
        res = remove_accents(text).lower()
        if compactform:
            res = compactify(res)
        return res




def currency_to_float(text: str, curr: str) -> float:
    """
    Convert a currency string to a float
    :param text: string to convert
    :param curr: currency
    :return: float
    """
    coeff = 1.0
    amount = 0
    text = text.replace(" ", "").lower()
    text = text.split(curr)[0]
    if text[-1] == "k":
        coeff = 1000.0
        text = text[:-1]
    elif text[-1] == "m":
        coeff = 1000000.0
        text = text[:-1]
    try:
        amount = float(text)
    except ValueError:
        amount = np.nan
    return amount * coeff


def zip_list_of_chars(list_of_chars: list) -> str:
    """
    Zip a list of chars into a string
    :param list_of_chars:
    :return:
    """
    return "".join(list_of_chars)


def search_for_tag(tag: str,
                   text: str,
                   do_normalize: bool = True,
                   space_sensitive: bool = True,
                   max_spaces_number: int = 1) -> Tuple[int, str]:
    """
    Search for a tag in a text: returns the position of the first occurrence of the tag in the text
    :param tag: tag to search for
    :param text: text to search in
    :param do_normalize: if True, normalize tag and text (remove accents, upper case)
    :param space_sensitive: if false: looks for tag with possible spaces in between
    :param max_spaces_number: maximum number of spaces between characters of tag
    :return: the start index of the first match of tag if any (-1 else),
             the matching string if any ('' else)
    """
    if do_normalize:
        tag = normalize(tag)
        text = normalize(text)
    if len(text) < len(tag):
        return -1, ""
    if not space_sensitive:
        if max_spaces_number == 1:
            tag = "".join([f"{c}\\s?" for c in tag])
        else:
            lbrace = "{"
            rbrace = "}"
            tag = "".join([f"{c}\\s{lbrace}0,{max_spaces_number}{rbrace}" for c in tag])
        tag += "\\s*:?"
        res = re.search(tag, text)
        if res is None:
            return -1, ""
        else:
            istart, iend = res.span()
            return istart, res.string[istart:iend]
    else:
        return text.find(tag), tag


def field_between_tags(line: str,
                       tag: str,
                       ending_tags=[],
                       do_normalize: bool = True,
                       search_for_shortest: bool = True
                       ) -> str:
    """
    Returns the right section of a line after a tag
    :param ending_tags:
    :param line:
    :param tag:
    :param do_normalize:
    :param search_for_shortest: if True, search for the shortest section between tag and ending tag
    :return:
    """
    if do_normalize:
        line = normalize(line)
        tag = normalize(tag)
    field = line.split(tag)[-1]
    if ending_tags is []:
        ending_tags.append(":")
        ending_tags.append('\\n')  # default
    endposition = 1000000
    bestendposition = endposition
    for ending_tag in ending_tags:
        endposition, _ = search_for_tag(ending_tag, field, do_normalize=do_normalize)
        if endposition >= 0:
            if endposition < bestendposition:
                bestendposition = endposition
                field = field[:bestendposition]
            if not search_for_shortest:
                break
    field = field.lstrip().rstrip()
    return field
