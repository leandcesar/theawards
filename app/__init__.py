from flask import Flask, Response, render_template
from flask_caching import Cache
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from app.api import api
from app.data import data
from app.graphql import schema

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.url_map.strict_slashes = False
cache = Cache(app)
cors = CORS(app)
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True),
)
api.init_app(app)


@app.route("/ping")
@limiter.exempt
def ping() -> Response:
    return Response("Pong!")


@app.route("/")
@limiter.exempt
def index() -> str:
    return render_template("index.html")


@app.before_first_request
def create_data() -> None:
    data.from_file("app/data.json")


if __name__ == "__main__":
    app.run()
