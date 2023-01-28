from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(message="Hello, World!")


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
