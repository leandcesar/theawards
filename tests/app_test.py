from flask import Response, url_for


def test_app_ping(client) -> None:
    response: Response = client.get(url_for("ping"))
    assert response.status_code == 200
    assert response.data == b"Pong!"
