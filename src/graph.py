"""LangGraph supervisor with specialist knowledge, support, analytics, and general nodes."""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from src.config import llm
from src.prompts import ROUTER_PROMPT, GENERAL_PROMPT
from src.schemas import RouteDecision, TicketInfo
from src.rag_chain import answer_from_documents
from src.tools import all_tools
from src.database import create_ticket
from src.analytics import analyze_csv

class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    question: str
    route: str
    answer: str
    csv_path: str | None
    analytics_table: str | None

def supervisor_node(state: State):
    question = state["question"]
    # Explicit identifiers and ticket-intent keywords provide deterministic routing.
    upper = question.upper()
    if "ORD-" in upper or "TKT-" in upper or any(x in question.lower() for x in ["create a ticket", "raise a ticket", "escalate", "complaint", "support ticket"]):
        return {"route": "support"}
    if state.get("csv_path") and any(x in question.lower() for x in ["csv", "dataset", "column", "average", "total", "highest", "lowest", "sales", "revenue", "correlation", "top ", "analyse", "analyze"]):
        return {"route": "analytics"}
    try:
        decision: RouteDecision = (ROUTER_PROMPT | llm.with_structured_output(RouteDecision)).invoke({"question": question})
        return {"route": decision.route}
    except Exception:
        return {"route": "knowledge"}

def knowledge_agent(state: State):
    try:
        result = answer_from_documents(state["question"])
        answer = result["answer"]
        if result["sources"]:
            answer += "\n\nSources:\n" + "\n".join(f"- {s}" for s in result["sources"])
    except FileNotFoundError as exc:
        answer = str(exc)
    except Exception as exc:
        answer = f"Document search failed: {exc}"
    return {"answer": answer, "messages": [AIMessage(content=answer)]}

def support_agent(state: State):
    question = state["question"]
    upper = question.upper()
    if "ORD-" in upper or "TKT-" in upper:
        tools_by_name = {tool.name: tool for tool in all_tools}
        selected = []
        if "ORD-" in upper:
            import re
            ids = re.findall(r"ORD-\d+", upper)
            selected = [tools_by_name["get_order_status"].invoke({"order_id": x}) for x in ids]
        if "TKT-" in upper:
            import re
            ids = re.findall(r"TKT-\d+", upper)
            selected = [tools_by_name["get_ticket_status"].invoke({"ticket_id": x}) for x in ids]
        answer = "\n".join(selected) if selected else "Please provide a valid order or ticket ID."
    else:
        conversation = "\n".join(str(m.content) for m in state.get("messages", []) if hasattr(m, "content"))
        ticket: TicketInfo = llm.with_structured_output(TicketInfo).invoke(
            "Extract a support ticket from this conversation. Do not invent the name; use Unknown.\n" + conversation
        )
        ticket_id = create_ticket(ticket.name, ticket.issue, ticket.priority)
        answer = (f"Support ticket created successfully.\nTicket ID: TKT-LOCAL-{ticket_id:04d}"
                  f"\nName: {ticket.name}\nIssue: {ticket.issue}\nPriority: {ticket.priority}"
                  "\nStatus: Open")
    return {"answer": answer, "messages": [AIMessage(content=answer)]}

def analytics_agent(state: State):
    path = state.get("csv_path")
    if not path:
        answer = "Upload a CSV file in the Data Analyst section first."
    else:
        try:
            answer, table = analyze_csv(path, state["question"], llm)
            table_text = table.to_string() if table is not None else None
            return {"answer": answer, "analytics_table": table_text, "messages": [AIMessage(content=answer)]}
        except Exception as exc:
            answer = f"CSV analysis failed: {exc}"
    return {"answer": answer, "messages": [AIMessage(content=answer)]}

def general_agent(state: State):
    answer = (GENERAL_PROMPT | llm).invoke({"question": state["question"]}).content
    if not isinstance(answer, str):
        answer = str(answer)
    return {"answer": answer, "messages": [AIMessage(content=answer)]}

def choose_agent(state: State) -> Literal["knowledge", "support", "analytics", "general"]:
    route = state.get("route", "knowledge")
    return route if route in {"knowledge", "support", "analytics", "general"} else "knowledge"

def build_graph():
    workflow = StateGraph(State)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("knowledge", knowledge_agent)
    workflow.add_node("support", support_agent)
    workflow.add_node("analytics", analytics_agent)
    workflow.add_node("general", general_agent)
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges("supervisor", choose_agent, {
        "knowledge": "knowledge", "support": "support",
        "analytics": "analytics", "general": "general"
    })
    for node in ["knowledge", "support", "analytics", "general"]:
        workflow.add_edge(node, END)
    return workflow.compile(checkpointer=MemorySaver())

app = build_graph()

def ask(question: str, thread_id: str = "default", csv_path: str | None = None):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({
        "messages": [HumanMessage(content=question)],
        "question": question,
        "route": "",
        "answer": "",
        "csv_path": csv_path,
        "analytics_table": None,
    }, config=config)
    return result
