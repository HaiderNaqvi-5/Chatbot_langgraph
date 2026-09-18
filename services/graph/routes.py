from services.graph.state import ChatState


def route_loan_flow(state: ChatState) -> str:
    data = state.get("extracted_data")

    # 0. Check for off-topic chatter FIRST
    if data.is_loan_related is False:
        return "off_topic"

    # 1. Check Name
    if not data.name:
        return "ask_name"

    # 2. Check Gender
    if not data.gender:
        return "ask_gender"
    if data.gender.lower() == "others":
        return "other_dept"

    # 3. Check Age
    if data.age is None:
        return "ask_age"
    if data.age < 18:
        return "reject"
    if data.age >= 61:
        return "calculate_loan"

    # 4. Age 18 to 20
    if 18 <= data.age <= 20:
        if not data.employment_status:
            return "ask_employment"
        return "calculate_loan"

    # 5. Age 21 to 60
    if not data.marital_status:
        return "ask_marital_status"

    marital = data.marital_status.lower()
    if marital == "single":
        if not data.employment_status:
            return "ask_employment"
        return "calculate_loan"

    if marital in ["married", "divorced"]:
        if marital == "married" and not data.employment_status:
            return "ask_employment"
        if data.has_child is None:
            return "ask_child"
        return "calculate_loan"

    return "ask_gender"
