import asyncio
from pathlib import Path

from app.lib.config import settings

from llama_cloud import AsyncLlamaCloud


def _document_to_text(document: object) -> str:
    text = getattr(document, "text", None)
    if isinstance(text, str):
        return text

    get_content = getattr(document, "get_content", None)
    if callable(get_content):
        content = get_content()
        if isinstance(content, str):
            return content

    return str(document)


async def extract_pdf_text(pdf_path: str) -> str:
    if not settings.llama_api_key:
        raise RuntimeError(
            "LLAMA_CLOUD_API_KEY is not configured. Set it in the environment or .env file."
        )
    
    client = AsyncLlamaCloud(api_key=settings.llama_api_key)

    # upload
    file_obj = await client.files.create(file=pdf_path, purpose="parse")

    # parse
    result = await client.parsing.parse(
        file_id=file_obj.id, 
        tier="agentic", 
        version="latest", 
        expand=["markdown_full", "text_full"]
    )

    

    return result.text_full