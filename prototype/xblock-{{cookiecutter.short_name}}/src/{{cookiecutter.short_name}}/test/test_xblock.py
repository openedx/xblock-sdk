import json
from typing import Any
from unittest.mock import MagicMock

from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from xblock.test.toy_runtime import ToyRuntime

from {{cookiecutter.short_name}} import {{cookiecutter.class_name}}


def make_block(**fields: str) -> {{cookiecutter.class_name}}:
    """Build a block with specific fields set."""
    scope_ids = ScopeIds("1", "2", "3", "4")
    return {{cookiecutter.class_name}}(
        ToyRuntime(), scope_ids=scope_ids, field_data=DictFieldData(data=fields)
    )


def mock_handle_request(data: dict[str, Any] | None = None, method: str = "POST"):
    """Return a request object compatible with an xblock_handler."""
    mock_request = MagicMock()
    mock_request.method = method
    mock_request.body = json.dumps(data).encode("utf-8")
    return mock_request


def test_updates_count():
    """Test that we can update the count, provided we have the right code."""
    block = make_block(count=0, code="beep")
    assert block.count == 0
    request = mock_handle_request({"code": "beep"})
    response = block.increment(request)
    assert response.status_code == 200
    assert block.count == 1


def test_rejects_wrong_code():
    """Test that sending a wrong code alongside an increment request fails."""
    block = make_block(count=0, code="beep")
    assert block.count == 0
    request = mock_handle_request({"code": "bork"})
    response = block.increment(request)
    assert response.status_code == 400
    assert block.count == 0
