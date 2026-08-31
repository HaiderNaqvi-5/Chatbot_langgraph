from langgraph.graph import END, START, StateGraph

from services.graph.state import ChatState
from services.graph.routes import route_loan_flow
from services.graph.nodes import (
    load_history_node,
    extract_data_node,
    ask_name_node,
    ask_gender_node,
    ask_age_node,
    ask_marital_status_node,
    ask_employment_node,
    ask_child_node,
    reject_node,
    other_dept_node,
    calculate_loan_node,
    generate_reply_node,
    persist_turn_node,
    off_topic_node,         # <-- ADDED: Import the new node
)

def build_chat_graph():
    graph = StateGraph(ChatState)
    
    # 1. Add Data & Persistence Nodes
    graph.add_node("load_history", load_history_node)
    graph.add_node("extract_data", extract_data_node)
    graph.add_node("persist_turn", persist_turn_node)
    
    # 2. Add Strategy Nodes
    graph.add_node("off_topic", off_topic_node)         # <-- ADDED: Register the node
    graph.add_node("ask_name", ask_name_node)
    graph.add_node("ask_gender", ask_gender_node)
    graph.add_node("ask_age", ask_age_node)
    graph.add_node("ask_marital_status", ask_marital_status_node)
    graph.add_node("ask_employment", ask_employment_node)
    graph.add_node("ask_child", ask_child_node)
    graph.add_node("reject", reject_node)
    graph.add_node("other_dept", other_dept_node)
    graph.add_node("calculate_loan", calculate_loan_node)

    # 3. Add Generation Node
    graph.add_node("generate_reply", generate_reply_node)

    # 4. Standard Flow
    graph.add_edge(START, "load_history")
    graph.add_edge("load_history", "extract_data")
    
    # 5. Conditional Routing
    graph.add_conditional_edges(
        "extract_data", 
        route_loan_flow,
        {
            "off_topic": "off_topic",                   # <-- ADDED: Map the route
            "ask_name": "ask_name",
            "ask_gender": "ask_gender",
            "ask_age": "ask_age",
            "ask_marital_status": "ask_marital_status",
            "ask_employment": "ask_employment",
            "ask_child": "ask_child",
            "reject": "reject",
            "other_dept": "other_dept",
            "calculate_loan": "calculate_loan"
        }
    )

    # 6. The Hybrid Pipeline: ALL strategy nodes funnel into generate_reply
    strategy_nodes = [
        "off_topic",                                    # <-- ADDED: Connect to generator
        "ask_name", "ask_gender", "ask_age", "ask_marital_status", 
        "ask_employment", "ask_child", "reject", 
        "other_dept", "calculate_loan"
    ]
    
    for node in strategy_nodes:
        graph.add_edge(node, "generate_reply")

    # 7. Generate text, then save to DB, then end
    graph.add_edge("generate_reply", "persist_turn")
    graph.add_edge("persist_turn", END)

    return graph.compile()

chat_graph = build_chat_graph()