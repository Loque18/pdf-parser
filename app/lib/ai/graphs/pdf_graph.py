from typing import TypedDict


class PdfGraphState(TypedDict, total=False):
    pdf_path: str
    pdf_bytes: bytes
    extracted_text: str
    extracted_data: dict
    normalized_data: dict
    error: str


def load_pdf_node(state: PdfGraphState) -> PdfGraphState:
    pdf_path = state.get("pdf_path", "")
    return {
        "pdf_path": pdf_path,
        "pdf_bytes": b"%PDF-mock-content",
    }


def extract_data_node(state: PdfGraphState) -> PdfGraphState:
    pdf_path = state.get("pdf_path", "")
    return {
        "extracted_text": f"Mock extracted text from {pdf_path or 'pdf'}",
        "extracted_data": {
            "title": "Mock PDF Title",
            "pages": 1,
            "source": pdf_path,
        },
    }


def normalize_node(state: PdfGraphState) -> PdfGraphState:
    extracted_data = state.get("extracted_data", {})
    return {
        "normalized_data": {
            "document_title": extracted_data.get("title", ""),
            "page_count": extracted_data.get("pages", 0),
            "source_file": extracted_data.get("source", ""),
        }
    }


def build_pdf_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "langgraph is not installed. Add it to the project dependencies to build the PDF graph."
        ) from exc

    graph = StateGraph(PdfGraphState)
    graph.add_node("load_pdf", load_pdf_node)
    graph.add_node("extract_data", extract_data_node)
    graph.add_node("normalize", normalize_node)

    graph.add_edge(START, "load_pdf")
    graph.add_edge("load_pdf", "extract_data")
    graph.add_edge("extract_data", "normalize")
    graph.add_edge("normalize", END)

    return graph.compile()
