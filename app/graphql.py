from typing import Any

import graphene

from app.data import data


def resolver(x: Any, attr: str, value: Any) -> bool:
    if isinstance(getattr(x, attr), str):
        return value.lower() in getattr(x, attr).lower()
    return getattr(x, attr) == value


class Nominee(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True, description="Typically, a movie or an artist")
    more = graphene.String(description="A complement to the nominee's name")
    note = graphene.String(
        description="Important observation about the nominee (usually empty)"
    )
    winner = graphene.Boolean(required=True)


class Category(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    nominees = graphene.List(
        Nominee,
        id=graphene.Int(),
        name=graphene.String(),
        more=graphene.String(),
        note=graphene.String(),
        winner=graphene.Boolean(),
    )

    def resolve_nominees(self, info, **options) -> list[Nominee]:
        return [
            x
            for x in self.nominees
            if all(resolver(x, attr, value) for attr, value in options.items())
        ]


class Edition(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    edition = graphene.Int()
    year = graphene.Int()
    categories = graphene.List(
        Category,
        id=graphene.Int(),
        name=graphene.String(),
    )

    def resolve_categories(self, info, **options) -> list[Category]:
        return [
            x
            for x in self.categories
            if all(resolver(x, attr, value) for attr, value in options.items())
        ]


class Query(graphene.ObjectType):
    editions = graphene.List(
        Edition,
        id=graphene.Int(),
        edition=graphene.Int(),
        name=graphene.String(),
        year=graphene.Int(),
    )

    def resolve_editions(self, info, **options) -> list[Edition]:
        return [
            x
            for x in data.editions
            if all(resolver(x, attr, value) for attr, value in options.items())
        ]


schema = graphene.Schema(query=Query)
