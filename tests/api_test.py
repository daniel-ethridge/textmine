import textmine.api as api
import pytest

def test_read_api_key_from_file():
    with pytest.raises(FileNotFoundError):
        api.read_api_key_from_file("")
