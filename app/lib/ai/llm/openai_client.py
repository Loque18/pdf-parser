from langchain_openai import ChatOpenAI

from app.lib.config import settings


def get_openai_client() -> ChatOpenAI:
    if not settings.llm_api_key:
        raise RuntimeError(
            "LLM_API_KEY is not configured. Set it in the environment or .env file."
        )
    if not settings.llm_model:
        raise RuntimeError(
            "LLM_MODEL is not configured. Set it in the environment or .env file."
        )

    client = ChatOpenAI(
        api_key=settings.llm_api_key,
        model=settings.llm_model
    )
    return client


