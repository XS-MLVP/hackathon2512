import pytest

# Autouse fixture – now only used to keep a consistent hook point without forcing failures
@pytest.fixture(autouse=True)
def template_not_implemented(request):
    yield
