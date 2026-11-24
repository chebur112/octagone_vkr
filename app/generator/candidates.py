import re

from collections.abc import Iterable


def find_candidates(question:str, catalog: Iterable[tuple[str, str]]) -> list[tuple[str,str]]:
    words = question.lower().split()

    ignored_word = {"сколько", "всего", "в", "за", "на"}

    aliases = {
        "продаж": ("продажи",),
        "продали": ("продажи",),
        "денег": ("денежные", "средства"),
        "фот": ("начисления", "удержания")
    }
    search_words = set()

    for word in words:
        word = word.strip(".,!?")
        if not word or word.isdigit() or word in ignored_word:
            continue
        if word in aliases:
            search_words.update(aliases[word])
        else:
            search_words.add(word)

    ranked = []

    for name, synonym in catalog:
        short_name = name.rsplit(".", 1)[-1]
        spaced_name = re.sub(r"(?<=[а-яёa-z])(?=[А-ЯЁA-Z])", " ", short_name)
        name_words = set(spaced_name.lower().split())
        synonym_words = set(synonym.lower().split())
        object_words = name_words | synonym_words
        matches = object_words & search_words

        score = len(matches)

        if score > 0:
            ranked.append((score, name, synonym))


    def sort_key(item: tuple[int, str, str]) -> tuple[int, str]:
        score, name, _ = item
        return -score, name

    ranked.sort(key = sort_key)

    candidates = []
    total_char = 0

    for _, name, synonym in ranked[:40]:
        line = f"{name} — {synonym}"
        line_char = len(line)

        if total_char + line_char > 6000:
            break

        candidates.append((name, synonym))
        total_char += line_char

    return candidates