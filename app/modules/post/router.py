from fastapi import APIRouter, status

from app.modules.post.dtos import PostCreate, PostResponse
from app.modules.post.services import create_post, get_post, list_posts

router = APIRouter()


@router.get("", response_model=list[PostResponse], summary="List posts")
def get_posts() -> list[PostResponse]:
    return list_posts()


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create post",
)
def create_post_endpoint(payload: PostCreate) -> PostResponse:
    return create_post(payload)


@router.get("/{post_id}", response_model=PostResponse, summary="Get post")
def get_post_by_id(post_id: int) -> PostResponse:
    return get_post(post_id)
