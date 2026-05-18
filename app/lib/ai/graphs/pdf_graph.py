from typing import TypedDict

from langchain.agents import create_agent

from app.lib.ai.pdf_tools import extract_pdf_text
from app.lib.ai.llm.openai_client import get_openai_client
from app.lib.ai.llm_tools import ParserLlmToolManager
from app.lib.ai.prompts.parser import PARSER_PROMPT, START_PROMPT


class PdfGraphState(TypedDict, total=False):
    pdf_path: str


    pdf_bytes: bytes
    extracted_text: str
    extracted_data: dict
    normalized_data: list[dict]
    error: str


async def parse_pdf_node(state: PdfGraphState) -> PdfGraphState:
    pdf_path = state.get("pdf_path", "")

    extracted_text = await extract_pdf_text(pdf_path)

    return {        
        "extracted_text": extracted_text,
    }


async def extract_data_node(state: PdfGraphState) -> PdfGraphState:
    extracted_text = state.get("extracted_text", "")

    # get llm client
    llm = get_openai_client()

    # get tools
    tool_manager = ParserLlmToolManager()
    tools = tool_manager.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=PARSER_PROMPT,
    )

    await agent.ainvoke({
        "messages": [{"role": "user", "content": START_PROMPT.format(pdf_content=extracted_text)}]
    })

    extracted_data = tool_manager.get_output()

    print("llm extracted data:", extracted_data)

    return {
        "extracted_data": extracted_data,
    }


async def normalize_node(state: PdfGraphState) -> PdfGraphState:
    extracted_data = state.get("extracted_data", {})

    return {
        "normalized_data": extracted_data
    }


def build_pdf_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "langgraph is not installed. Add it to the project dependencies to build the PDF graph."
        ) from exc

    graph = StateGraph(PdfGraphState)
    graph.add_node("parse_pdf", parse_pdf_node)
    graph.add_node("extract_data", extract_data_node)
    graph.add_node("normalize", normalize_node)

    graph.add_edge(START, "parse_pdf")
    graph.add_edge("parse_pdf", "extract_data")
    graph.add_edge("extract_data", "normalize")
    graph.add_edge("normalize", END)

    return graph.compile()
