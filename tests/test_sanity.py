import pytest


@pytest.mark.integration
def test_sanity():
    assert 1 + 1 == 2
