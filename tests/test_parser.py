import pytest
from app.parser import parse_with_regex

@pytest.mark.parametrize("text, expected", [
    (
        "MerchantName\nDate: 2025-05-24\nItem A\nTotal: $123.45", 
        {"merchant": "MerchantName", "date": "2025-05-24", "total": "123.45"}
    ),
    (
        "コンビニエンスストア\n2025/05/24\nTotal ¥987.65", 
        {"merchant": "コンビニエンスストア", "date": "2025/05/24", "total": "987.65"}
    ),
    (
        "Receipt Corp\n04-24-2025\nSomething\ntotal 50.00", 
        {"merchant": "Receipt Corp", "date": None, "total": "50.00"}
    ),
    (
        "\n\nUnknown\nLine2\nTotal:100.00\n", 
        {"merchant": "Unknown", "date": None, "total": "100.00"}
    ),
    (
        "", {"merchant": None, "date": None, "total": None}
    ),
])
def test_parse_with_regex(text, expected):
    result = parse_with_regex(text)
    assert result == expected
