from langgraph.graph import StateGraph, END
from app.workflow.state import IntakeState
from app.workflow.nodes import classify_intent, collect_info, route_after_classify


def build_intake_graph():
    """Build the intake workflow graph."""
    graph = StateGraph(IntakeState)

    # Add nodes
    graph.add_node("classify", classify_intent)
    graph.add_node("collect_info", collect_info)

    # Set entry point
    graph.set_entry_point("classify")

    # Conditional edge after classify
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "collect_info": "collect_info",
            "__end__": END,
        }
    )

    # collect_info -> END
    graph.add_edge("collect_info", END)

    return graph.compile()


intake_graph = build_intake_graph()
