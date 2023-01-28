from flask import url_for


def test_app_index(client) -> None:
    response = client.get(url_for("index"))
    assert response.status_code == 200
    assert response.json == {"message": "Hello, World!"}
