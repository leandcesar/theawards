import pytest

from app import Flask, create_app


@pytest.fixture
def app() -> Flask:
    return create_app()
