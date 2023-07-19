import pytest

from app.utils import get_minutes_from_ts


@pytest.mark.parametrize("data,expected", [
    (1, 1),
    (1, 1)
])
def test_group_by_segments_per_parameter_type(data, expected):
    result = get_minutes_from_ts(data)
    result == expected
