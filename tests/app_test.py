from flask import Response, url_for


def test_app_index(client) -> None:
    response: Response = client.get(url_for("index"))
    assert response.status_code == 200
    assert response.data == b"Hello, World!"
