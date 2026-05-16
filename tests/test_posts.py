from fastapi.testclient import TestClient

from app.main import app
from app.modules.post.services import reset_posts


client = TestClient(app)


def setup_function() -> None:
    reset_posts()


def test_list_posts_starts_empty() -> None:
    response = client.get("/posts")

    assert response.status_code == 200
    assert response.json() == []


def test_create_post() -> None:
    response = client.post(
        "/posts",
        json={"title": "First post", "content": "Hello from memory"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "First post",
        "content": "Hello from memory",
    }


def test_get_post_by_id() -> None:
    created = client.post(
        "/posts",
        json={"title": "Stored post", "content": "Persisted in memory"},
    ).json()

    response = client.get(f"/posts/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_post_by_id_returns_not_found() -> None:
    response = client.get("/posts/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}
