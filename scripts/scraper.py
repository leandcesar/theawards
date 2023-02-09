import json
import re
from enum import Enum

REGEX_YEAR_EDITION = re.compile(
    r"^((?:19|20)[0-9]{2})(?:\/[0-9]{2})? \(([0-9]{1,2})(?:st|nd|rd|th)\)$"
)
REGEX_NOTE = re.compile(r"^\[NOTE\: (.+)\]$")
REGEX_CATEGORY = re.compile(r"^[A-Z ?]{4,}(?:\([A-Za-z- ]+\))?$")


def to_ordinal(number: int) -> str:
    if 11 <= number <= 13:
        return f"{number}th"
    elif str(number)[-1] == "1":
        return f"{number}st"
    elif str(number)[-1] == "2":
        return f"{number}nd"
    elif str(number)[-1] == "3":
        return f"{number}rd"
    return f"{number}th"


def read_file(filename: str) -> list[str]:
    with open(filename, encoding="UTF-8") as f:
        return f.readlines()


def write_file(filename: str, data: list[str]) -> None:
    with open(filename, "w", encoding="UTF-8") as f:
        f.write(json.dumps(data))


def find_category(value: str) -> re.Match | None:
    return REGEX_CATEGORY.match(value)


def find_note(value: str) -> re.Match | None:
    return REGEX_NOTE.match(value)


def find_year_and_edition(value: str) -> re.Match | None:
    return REGEX_YEAR_EDITION.match(value)


def new_edition(year_edition: re.Match) -> dict[str, str]:
    return {
        "name": f"{to_ordinal(int(year_edition.group(2)))} Academy Awards",
        "year": year_edition.group(1),
        "edition": int(year_edition.group(2)),
        "categories": [],
    }


def new_category(category: re.Match) -> dict[str, str]:
    return {
        "name": category.group(0).title(),
        "nominees": [],
    }


def new_nominee(value: str) -> dict[str, str]:
    if " -- " in value:
        name, more = value.split(" -- ", maxsplit=1)
    else:
        name, more = value, None
    return {"name": name, "more": more, "note": None, "winner": False}


def raw_data_to_json(raw_data: list[str]) -> list[dict]:
    data: list[dict] = []
    edition = category = nominee = {}
    for line in raw_data:
        line = line.strip(" \n")
        _year_edition = find_year_and_edition(line)
        if _year_edition:
            edition = new_edition(_year_edition)
            data.append(edition)
            continue
        _category = find_category(line)
        if _category:
            category = new_category(_category)
            edition["categories"].append(category)
            continue
        _note = find_note(line)
        if _note:
            nominee["note"] = _note.group(1)
            continue
        nominee = new_nominee(line)
        category["nominees"].append(nominee)
    return data


def merge_jsons(*, base: list[dict], append: list[dict]) -> list[dict]:
    new_data = base.copy()
    for i, edition in enumerate(append):
        for j, category in enumerate(edition["categories"]):
            nominee = category["nominees"][0]
            for n in base[i]["categories"][j]["nominees"]:
                if nominee["name"] == n["name"]:
                    n["winner"] = True
    return new_data


if __name__ == "__main__":
    raw_data_nominees = read_file("scripts/raw_data_nominees.txt")
    nominees = raw_data_to_json(raw_data_nominees)
    raw_data_winners = read_file("scripts/raw_data_winners.txt")
    winners = raw_data_to_json(raw_data_winners)
    merged_data = merge_jsons(base=nominees, append=winners)
    write_file("app/data.json", merged_data)
