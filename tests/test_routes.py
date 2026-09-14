import pytest
from services.graph.routes import route_loan_flow
from services.graph.state import ChatState, LoanStateExtraction

def _create_state(**kwargs):
    # Use model_construct to bypass Pydantic validation for testing routing logic
    # Default values for required path
    default_kwargs = {
        'is_loan_related': True,
        'name': "John Doe",
        'gender': "male",
        'age': 30,
        'marital_status': "single",
        'employment_status': "employed",
        'has_child': False
    }
    default_kwargs.update(kwargs)
    data = LoanStateExtraction.model_construct(**default_kwargs)
    return ChatState(extracted_data=data)

def test_route_loan_flow_off_topic():
    state = _create_state(is_loan_related=False)
    assert route_loan_flow(state) == "off_topic"

def test_route_loan_flow_ask_name():
    state = _create_state(name=None)
    assert route_loan_flow(state) == "ask_name"

def test_route_loan_flow_ask_gender():
    state = _create_state(gender=None)
    assert route_loan_flow(state) == "ask_gender"

def test_route_loan_flow_other_dept():
    state = _create_state(gender="others")
    assert route_loan_flow(state) == "other_dept"

def test_route_loan_flow_ask_age():
    state = _create_state(age=None)
    assert route_loan_flow(state) == "ask_age"

def test_route_loan_flow_reject_underage():
    state = _create_state(age=17)
    assert route_loan_flow(state) == "reject"

def test_route_loan_flow_calculate_loan_senior():
    state = _create_state(age=61)
    assert route_loan_flow(state) == "calculate_loan"

def test_route_loan_flow_age_18_20_ask_employment():
    state = _create_state(age=19, employment_status=None)
    assert route_loan_flow(state) == "ask_employment"

def test_route_loan_flow_age_18_20_calculate_loan():
    state = _create_state(age=19, employment_status="studying")
    assert route_loan_flow(state) == "calculate_loan"

def test_route_loan_flow_age_21_60_ask_marital_status():
    state = _create_state(age=30, marital_status=None)
    assert route_loan_flow(state) == "ask_marital_status"

def test_route_loan_flow_age_21_60_single_ask_employment():
    state = _create_state(age=30, marital_status="single", employment_status=None)
    assert route_loan_flow(state) == "ask_employment"

def test_route_loan_flow_age_21_60_single_calculate_loan():
    state = _create_state(age=30, marital_status="single", employment_status="employed")
    assert route_loan_flow(state) == "calculate_loan"

def test_route_loan_flow_age_21_60_married_ask_employment():
    state = _create_state(age=30, marital_status="married", employment_status=None)
    assert route_loan_flow(state) == "ask_employment"

def test_route_loan_flow_age_21_60_married_ask_child():
    state = _create_state(age=30, marital_status="married", employment_status="employed", has_child=None)
    assert route_loan_flow(state) == "ask_child"

def test_route_loan_flow_age_21_60_married_calculate_loan():
    state = _create_state(age=30, marital_status="married", employment_status="employed", has_child=True)
    assert route_loan_flow(state) == "calculate_loan"

def test_route_loan_flow_age_21_60_divorced_ask_child():
    state = _create_state(age=30, marital_status="divorced", employment_status=None, has_child=None)
    assert route_loan_flow(state) == "ask_child"

def test_route_loan_flow_age_21_60_divorced_calculate_loan():
    state = _create_state(age=30, marital_status="divorced", employment_status=None, has_child=False)
    assert route_loan_flow(state) == "calculate_loan"

def test_route_loan_flow_age_21_60_unknown_marital_status_fallback():
    state = _create_state(age=30, marital_status="unknown")
    assert route_loan_flow(state) == "ask_gender"
