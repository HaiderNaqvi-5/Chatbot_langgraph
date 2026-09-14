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
    
    # Node mapping for strategy nodes
    strategy_nodes = {
        "off_topic": off_topic_node,
        "ask_name": ask_name_node,
        "ask_gender": ask_gender_node,
        "ask_age": ask_age_node,
        "ask_marital_status": ask_marital_status_node,
        "ask_employment": ask_employment_node,
        "ask_child": ask_child_node,
        "reject": reject_node,
        "other_dept": other_dept_node,
        "calculate_loan": calculate_loan_node,
    }

    # 2. Add Strategy Nodes
    for name, node_func in strategy_nodes.items():
        graph.add_node(name, node_func)

    # 3. Add Generation Node
    graph.add_node("generate_reply", generate_reply_node)

    # 4. Standard Flow
    graph.add_edge(START, "load_history")
    graph.add_edge("load_history", "extract_data")
    
    # 5. Conditional Routing
    graph.add_conditional_edges(
        "extract_data", 
        route_loan_flow,
        {name: name for name in strategy_nodes.keys()}
    )

    # 6. The Hybrid Pipeline: ALL strategy nodes funnel into generate_reply
    for name in strategy_nodes.keys():
        graph.add_edge(name, "generate_reply")

    # 7. Generate text, then save to DB, then end
    graph.add_edge("generate_reply", "persist_turn")
    graph.add_edge("persist_turn", END)

    return graph.compile()

chat_graph = build_chat_graph()