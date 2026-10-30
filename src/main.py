"""CLI entry point."""
import uuid
from langchain_core.messages import HumanMessage
from src.graph import app

def main():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    print("=" * 58)
    print(" Nexora AI — Smart Company Assistant")
    print(" Type 'quit' to exit.")
    print("=" * 58)
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break
        if not question:
            continue
        result = app.invoke({
            "messages": [HumanMessage(content=question)],
            "question": question, "route": "", "answer": "",
            "csv_path": None, "analytics_table": None,
        }, config=config)
        print("\nNexora:", result.get("answer", "No response."))

if __name__ == "__main__":
    main()
