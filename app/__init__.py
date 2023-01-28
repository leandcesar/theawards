from flask import Flask, Response, jsonify

app = Flask(__name__)


@app.route("/")
def index() -> Response:
    return jsonify(message="Hello, World!")


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
