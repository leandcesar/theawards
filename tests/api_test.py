from flask import Response, url_for

from app import data


def test_api_editions(client) -> None:
    response: Response = client.get(url_for("oscars_edition"))
    assert response.status_code == 200
    assert len(response.get_json()) == 94
    assert response.get_json()[0] == {
        "edition": 1,
        "id": 1,
        "name": "1st Academy Awards",
        "year": 1927,
    }


def test_api_editions_by_year(client) -> None:
    response: Response = client.get(
        url_for("oscars_edition"), query_string={"year": 2000}
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0] == {
        "edition": 73,
        "id": 73,
        "name": "73rd Academy Awards",
        "year": 2000,
    }


def test_api_categories(client) -> None:
    response: Response = client.get(url_for("oscars_category", id_edition=22))
    assert response.status_code == 200
    assert len(response.get_json()) == 30
    assert response.get_json()[0] == {"id": 1001, "name": "Actor"}


def test_api_categories_by_name(client) -> None:
    response: Response = client.get(
        url_for("oscars_category", id_edition=22), query_string={"name": "direct"}
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 3
    assert response.get_json()[0] == {
        "id": 1681,
        "name": "Art Direction (Black-And-White)",
    }


def test_api_nominees(client) -> None:
    response: Response = client.get(
        url_for("oscars_nominee", id_edition=41, id_category=1001)
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 5
    assert response.get_json()[0] == {
        "id": 3873,
        "more": 'The Heart Is a Lonely Hunter {"Singer"}',
        "name": "Alan Arkin",
        "note": None,
        "winner": False,
    }


def test_api_nominees_by_name(client) -> None:
    response: Response = client.get(
        url_for("oscars_nominee", id_edition=20, id_category=1001),
        query_string={"name": "a"},
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 4
    assert response.get_json()[0] == {
        "id": 1081,
        "more": 'A Double Life {"Anthony John"}',
        "name": "Ronald Colman",
        "note": None,
        "winner": True,
    }


def test_api_nominees_by_winner(client) -> None:
    response: Response = client.get(
        url_for("oscars_nominee", id_edition=41, id_category=1001),
        query_string={"winner": True},
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0] == {
        "id": 4017,
        "more": 'Charly {"Charly Gordon"}',
        "name": "Cliff Robertson",
        "note": None,
        "winner": True,
    }
