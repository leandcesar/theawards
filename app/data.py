import itertools
import json
from typing import List, Optional

from dataclasses import asdict, dataclass

generator_id = itertools.count(start=1001, step=1)
mapping_id: dict[str, int] = {}


def generate_id(seed: str) -> int:
    if seed not in mapping_id:
        mapping_id[seed] = next(generator_id)
    return mapping_id[seed]


@dataclass
class Nominee:
    name: str
    more: str
    note: str
    winner: bool
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.id is None:
            self.id = generate_id(self.name)

    def as_dict(self, *, fields: Optional[List[str]] = None) -> dict:
        if fields:
            return {
                field: value for field, value in asdict(self).items() if field in fields
            }
        return asdict(self)


@dataclass
class Category:
    name: str
    nominees: List[Nominee]
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.id is None:
            self.id = generate_id(self.name)
        self.nominees = [Nominee(**nominee) for nominee in self.nominees]

    def get_nominee(self, id_nominee: int) -> Optional[Nominee]:
        return next(
            (nominee for nominee in self.nominees if nominee.id == id_nominee), None
        )

    def as_dict(self, *, fields: Optional[List[str]] = None) -> dict:
        if fields:
            return {
                field: value for field, value in asdict(self).items() if field in fields
            }
        return asdict(self)


@dataclass
class Edition:
    categories: List[Category]
    edition: int
    name: str
    year: int
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.id is None:
            self.id = self.edition
        self.categories = [Category(**category) for category in self.categories]

    def get_category(self, id_category: int) -> Optional[Category]:
        return next(
            (category for category in self.categories if category.id == id_category),
            None,
        )

    def as_dict(self, *, fields: Optional[List[str]] = None) -> dict:
        if fields:
            return {
                field: value for field, value in asdict(self).items() if field in fields
            }
        return asdict(self)


@dataclass
class Data:
    editions: Optional[List[Edition]] = None

    def get_edition(self, id_edition: int) -> Optional[Edition]:
        return next(
            (edition for edition in self.editions if edition.id == id_edition), None
        )

    def from_json(self, editions: List[dict]) -> None:
        self.editions = [Edition(**edition) for edition in editions]

    def from_file(self, filename: str) -> None:
        with open(filename, encoding="UTF-8") as f:
            raw_data = f.read()
        editions = json.loads(raw_data)
        self.from_json(editions)


data = Data()
