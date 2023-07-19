import pytest

from app.utils import is_integer_num


@pytest.mark.parametrize("input,expected", [
    (1, True),
])
def test_is_integer_num(input, expected):
    is_integer_num(input) == expected
