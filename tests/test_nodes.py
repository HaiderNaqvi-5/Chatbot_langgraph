import pytest
from services.graph.nodes import calculate_loan_node
from services.graph.state import ChatState, LoanStateExtraction

pytestmark = pytest.mark.anyio

@pytest.mark.parametrize(
    "name, age, marital_status, employment_status, has_child, expected_amount, expected_interest",
    [
        # Age >= 61
        ("Alice", 65, "married", "employed", False, 1000000, 0),
        ("Bob", 61, "single", "unemployed", True, 1000000, 0),

        # 18 <= age <= 20 or marital == "single"
        # 18 <= age <= 20, studying vs not studying
        ("Charlie", 19, "married", "studying", False, 500000, 0),
        ("Dave", 20, "married", "employed", False, 600000, 30),
        # marital == "single", studying vs not studying
        ("Eve", 30, "single", "studying", False, 500000, 0),
        ("Frank", 40, "single", "employed", False, 600000, 30),
        ("Grace", 25, "single", "unemployed", False, 600000, 30),

        # marital == "married"
        # employed vs unemployed, has_child vs no_child
        ("Heidi", 40, "married", "employed", True, 800000, 10),
        ("Ivan", 40, "married", "employed", False, 800000, 20),
        ("Judy", 40, "married", "unemployed", True, 600000, 10),
        ("Kevin", 40, "married", "unemployed", False, 600000, 20),

        # marital == "divorced"
        # has_child vs no_child
        ("Mallory", 45, "divorced", "employed", True, 900000, 0),
        ("Niaj", 45, "divorced", "unemployed", False, 700000, 0),
    ]
)
async def test_calculate_loan_node(
    name, age, marital_status, employment_status, has_child, expected_amount, expected_interest
):
    extracted_data = LoanStateExtraction(
        name=name,
        age=age,
        marital_status=marital_status,
        employment_status=employment_status,
        has_child=has_child,
    )
    state = ChatState(extracted_data=extracted_data)

    result = await calculate_loan_node(state)

    directive = result["directive"]

    assert f"Congratulate {name}." in directive
    assert f"Approve a loan of {expected_amount // 100000} lacs (Rs. {expected_amount:,})" in directive
    assert f"interest rate of {expected_interest}%" in directive
