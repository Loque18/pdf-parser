from itertools import count

from fastapi import HTTPException, status

from app.modules.post.dtos import PostCreate, PostResponse

_post_id_sequence = count(1)
_posts: dict[int, PostResponse] = {}


def list_posts() -> list[PostResponse]:
    return list(_posts.values())


def create_post(payload: PostCreate) -> PostResponse:
    post = PostResponse(
        id=next(_post_id_sequence),
        title=payload.title,
        content=payload.content,
    )
    _posts[post.id] = post
    return post


def get_post(post_id: int) -> PostResponse:
    post = _posts.get(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


def reset_posts() -> None:
    global _post_id_sequence
    _posts.clear()
    _post_id_sequence = count(1)
