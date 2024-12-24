import pytest
from unittest.mock import MagicMock

import requests

from events.services import fetch_pypi_package_data
from events.exceptions import ServiceException


@pytest.mark.django_db
def test_fetch_pypi_package_data_success(mocker):
    # Mock cache.get to simulate a cache miss
    mocker.patch('events.services.cache.get', return_value=None)
    mock_cache_set = mocker.patch('events.services.cache.set')

    # Mock requests.get to return mock pypi data
    mock_pypi_data = {
        "info": {"name": "requests", "version": "2.25.0"},
        "releases": {"2.25.0": {}},
    }
    mock_response = MagicMock()
    mock_response.json.return_value = mock_pypi_data
    mocker.patch('events.services.requests.get', return_value=mock_response)

    # Call our function
    result = fetch_pypi_package_data('requests')

    # Check mock pypi data returned, and cache updated
    assert result == mock_pypi_data
    mock_cache_set.assert_called_once_with("pypi_package_requests", mock_pypi_data, timeout=86400)


def test_fetch_pypi_package_data_service_failure(mocker):
    # Mock cache.get to simulate a cache miss
    mocker.patch('events.services.cache.get', return_value=None)
    mock_cache_set = mocker.patch('events.services.cache.set')

    # Mock requests.get call to raise an error
    mocker.patch('events.services.requests.get', side_effect=requests.RequestException)

    # Call our function, check it raises our error
    with pytest.raises(ServiceException):
        fetch_pypi_package_data("flask")

    # Check cache not updated
    mock_cache_set.assert_not_called()
