from langgraph.graph import StateGraph, END
from nodes.fetch_gmail import fetch_gmail
from nodes.read_pdfs import read_pdfs
from nodes.read_reminders import read_reminders
from nodes.normalize import normalize_items
from nodes.dedupe import dedupe_items
from nodes.classify_tag import classify_and_tag
from nodes.extract_due_date import extract_due_date_node
from nodes.summarize import summarize_digest
from nodes.publish import publish_digest

def build_graph():
    g = StateGraph(dict)
    g.add_node("fetch_gmail", fetch_gmail)
    g.add_node("read_pdfs", read_pdfs)
    g.add_node("read_reminders", read_reminders)
    g.add_node("normalize", normalize_items)
    g.add_node("dedupe", dedupe_items)
    g.add_node("classify_tag", classify_and_tag)
    g.add_node("extract_due_date", extract_due_date_node)
    g.add_node("summarize", summarize_digest)
    g.add_node("publish", publish_digest)

    g.set_entry_point("fetch_gmail")
    g.add_edge("fetch_gmail", "read_pdfs")
    g.add_edge("read_pdfs", "read_reminders")
    g.add_edge("read_reminders", "normalize")
    g.add_edge("normalize", "dedupe")
    g.add_edge("dedupe", "classify_tag")
    g.add_edge("classify_tag", "extract_due_date")
    g.add_edge("extract_due_date", "summarize")
    g.add_edge("summarize", "publish")
    g.add_edge("publish", END)
    return g.compile()
