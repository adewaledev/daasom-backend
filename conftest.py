import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """Reset throttle (and all cache) state between tests."""
    cache.clear()
    yield
    cache.clear()
