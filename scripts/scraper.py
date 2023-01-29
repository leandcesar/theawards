import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, ResultSet
from tqdm import tqdm
from unidecode import unidecode

NUM_EDITIONS = 95
# from: https://en.wikipedia.org/wiki/Academy_Awards#Awards_of_Merit_categories
CATEGORIES = [
    "Best Animated Feature Film",
    "Best Makeup and Hairstyling",
    "Best Costume Design",
    "Best International Feature Film",
    "Best Documentary Feature Film",
    "Best Documentary Short Film",
    "Best Original Screenplay",
    "Best Visual Effects",
    "Best Supporting Actor",
    "Best Supporting Actress",
    "Best Film Editing",
    "Best Original Score",
    "Best Original Song",
    "Best Live Action Short Film",
    "Best Animated Short Film",
    "Best Sound",
    "Best Picture",
    "Best Director",
    "Best Actor",
    "Best Actress",
    "Best Cinematography",
    "Best Production Design",
    "Best Adapted Screenplay",
    "Best Assistant Director",
    "Best Director, Comedy Picture",
    "Best Director, Dramatic Picture",
    "Best Dance Direction",
    "Best Original Musical or Comedy Score",
    "Best Original Story",
    "Best Short Subject, 1 Reel",
    "Best Short Subject, 2 Reel",
    "Best Short Subject, Color",
    "Best Short Subject, Comedy",
    "Best Short Subject, Novelty",
    "Best Sound Editing",
    "Best Title Writing",
    "Best Unique and Artistic Production",
]
REGEX_DATE = (
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s[0-9]{1,2},"
    r"\s(?:19|20)[0-9]{2}"
)


def to_ordinal(number: int) -> str:
    if str(number)[-1] == "1" and str(number) != "11":
        return f"{number}st"
    if str(number)[-1] == "2" and str(number) != "12":
        return f"{number}nd"
    if str(number)[-1] == "3" and str(number) != "13":
        return f"{number}rd"
    return f"{number}th"


def clean_text(text: str) -> str:
    text = unidecode(text).split("\n")[0]
    text = re.sub(r"\[[0-9a-zA-Z]{1,2}\]", "", text)
    text = text.strip().rstrip("*")
    return text


def get_date(value: str) -> str:
    result = re.search(REGEX_DATE, value, re.IGNORECASE)
    if not result:
        raise ValueError(f"No date was found in {value!r}")
    return datetime.strptime(result.group(0), "%B %d, %Y").date().isoformat()


def get_categories_from_tr(
    table: ResultSet,
) -> list[dict[str, str | list[dict[str, str]]]]:
    trs = table.tbody.find_all("tr")
    data = []
    for tr in trs:
        ths = tr.find_all("th")
        tds = tr.find_all("td")
        for th in ths:
            if th.get_text() and th.get_text() != "\n":
                item = {"name": clean_text(th.get_text())}
                data.append(item)
        for td in tds:
            if hasattr(td, "ul") and td.ul:
                nominees = td.ul.get_text().split("\n")
                item = {"nominees": list(map(clean_text, nominees))}
                data.append(item)
    part_one = data[::2]
    part_two = data[1::2]
    if (len(data) / 2 % 2) != 0:
        part_two = part_two[-1:] + part_two[:-1]
    data = part_one + part_two
    data = [{**data[i], **data[i + 1]} for i in range(0, len(data), 2)]
    return data


def get_categories_from_td(
    table: ResultSet,
) -> list[dict[str, str | list[dict[str, str]]]]:
    tds = table.tbody.find_all("td")
    data = []
    for td in tds:
        item = {}
        if hasattr(td, "div") and td.div:
            item["name"] = clean_text(td.div.get_text())
        if hasattr(td, "ul") and td.ul:
            nominees = td.ul.get_text().split("\n")
            item["nominees"] = list(map(clean_text, nominees))
        if item:
            data.append(item)
    return data


def get_categories_from_table(
    table: ResultSet,
) -> list[dict[str, str | list[dict[str, str]]]]:
    trs = table.tbody.find_all("tr")
    if any(tr.th and tr.th.get_text() != "\n" for tr in trs):
        categories = get_categories_from_tr(table)
    else:
        categories = get_categories_from_td(table)
    for category in categories:
        nominees = []
        for nominee in category["nominees"]:
            if " - " in nominee:
                name, extra = nominee.split(" - ", 1)
            else:
                name, extra = nominee, None
            nominee = {"name": name, "extra": extra}
            nominees.append(nominee)
        category["nominees"] = nominees
        category["winner"] = category["nominees"][0]
    return categories


def get_date_from_table(table: ResultSet) -> str | None:
    for tr in table.find_all("tr"):
        if tr.th and tr.td and tr.th.get_text().lower() == "date":
            value = tr.td.get_text()
            return get_date(value)


def scraper(
    content: str,
) -> dict[str, str | list[dict[str, str | list[dict[str, str]]]]]:
    soup = BeautifulSoup(content, "html.parser")
    title = soup.h1.get_text()

    for table in soup.find_all("table"):
        if "infobox" in table["class"]:
            date = get_date_from_table(table)
        if "wikitable" in table["class"]:
            categories = get_categories_from_table(table)
            break

    return {
        "name": title,
        "date": date,
        "categories": categories,
    }


if __name__ == "__main__":

    with open("app/data.json") as f:
        raw_data = f.read() or "[]"
        datas = json.loads(raw_data)

    init = len(datas) + 1

    for i in tqdm(range(init, NUM_EDITIONS), initial=init):
        edition = to_ordinal(i)
        url = f"https://en.wikipedia.org/wiki/{edition}_Academy_Awards"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = scraper(response.content)
        datas.append(data)

        with open("app/data.json", "w") as f:
            f.write(json.dumps(datas))
