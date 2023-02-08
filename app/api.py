# -*- coding: utf-8 -*-
from flask_restx import Api, Resource, abort, fields, inputs, reqparse

from app.data import data

api = Api(
    version="1.0",
    title="Academy Awards",
    description=(
        "The Academy Awards REST API contains the record of past Academy Award "
        "winners and nominees. The data is complete through the 2021 (94th) "
        "Academy Awards, presented on March 27, 2022."
    ),
    validate=True,
    doc="/docs",
    prefix="/api",
    license="Apache License 2.0",
    license_url="https://github.com/leandcesar/theawards/blob/main/LICENSE",
)
ns = api.namespace("oscars", description="Oscars winners and nominees")

edition = ns.model(
    "Edition",
    {
        "id": fields.Integer(required=True, example=45),
        "name": fields.String(required=True, example="45th Academy Awards"),
        "edition": fields.Integer(required=True, example=45),
        "year": fields.Integer(required=True, example=1972),
    },
)
edition_parser = reqparse.RequestParser()
edition_parser.add_argument("year", type=int)

category = ns.model(
    "Category",
    {
        "id": fields.Integer(required=True, example=1001),
        "name": fields.String(required=True, example="Actor"),
    },
)
category_parser = reqparse.RequestParser()
category_parser.add_argument("name", type=str)

nominee = ns.model(
    "Nominee",
    {
        "id": fields.Integer(required=True, example=2740),
        "name": fields.String(
            required=True,
            description="Typically, a movie or an artist",
            example="Marlon Brando",
        ),
        "more": fields.String(
            description="A complement to the nominee's name",
            example='The Godfather {"Don Vito Corleone"}',
        ),
        "note": fields.String(
            description="Important observation about the nominee (usually empty)",
            example="Mr. Brando refused the award.",
        ),
        "winner": fields.Boolean(required=True, example=True),
    },
)
nominee_parser = reqparse.RequestParser()
nominee_parser.add_argument("name", type=str)
nominee_parser.add_argument("winner", type=inputs.boolean)


@ns.route("/editions")
class Edition(Resource):
    @ns.doc("list_editions")
    @ns.expect(edition_parser)
    @ns.marshal_list_with(edition, code=200)
    def get(self):
        editions = [x.as_dict(fields=edition.keys()) for x in data.editions]
        args = edition_parser.parse_args()
        if args.get("year") is not None:
            editions = [x for x in editions if args["year"] == x["year"]]
        return editions, 200


@ns.route("/editions/<int:id_edition>/categories")
@ns.response(400, "Invalid ID supplied")
@ns.response(404, "Category not found")
class Category(Resource):
    @ns.doc("list_categories")
    @ns.expect(category_parser)
    @ns.marshal_list_with(category, code=200)
    def get(self, id_edition: int):
        item = data.get_edition(id_edition) or abort(404)
        categories = [x.as_dict(fields=category.keys()) for x in item.categories]
        args = category_parser.parse_args()
        if args.get("name") is not None:
            categories = [x for x in categories if args["name"].lower() in x["name"].lower()]
        return categories, 200


@ns.route("/editions/<int:id_edition>/categories/<int:id_category>/nominees")
@ns.response(400, "Invalid ID supplied")
@ns.response(404, "Nominee not found")
class Nominee(Resource):
    @ns.doc("list_nominees")
    @ns.expect(nominee_parser)
    @ns.marshal_list_with(nominee, code=200)
    def get(self, id_edition: int, id_category: int):
        item = data.get_edition(id_edition) or abort(404)
        subitem = item.get_category(id_category) or abort(404)
        nominees = [x.as_dict(fields=nominee.keys()) for x in subitem.nominees]
        args = nominee_parser.parse_args()
        if args.get("name") is not None:
            nominees = [x for x in nominees if args["name"].lower() in x["name"].lower()]
        if args.get("winner") is not None:
            nominees = [x for x in nominees if args["winner"] == x["winner"]]
        return nominees, 200
