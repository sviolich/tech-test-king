from datetime import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from events.exceptions import ServiceException
from events.models import PackageEvent

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def valid_event_data():
    return {
        "timestamp": "2024-12-23T12:00:00Z",
        "package": "requests",
        "event_type": "install",
    }

@pytest.fixture
def invalid_event_data():
    return {
        "timestamp": "2024-12-23T12:00:00Z",
        "package": "",  # Missing package name should cause failure
        "event_type": "install",
    }

# Test for successful creation (201 status code)
@pytest.mark.django_db
def test_create_event_success(client, valid_event_data):
    # Send POST request with valid data
    response = client.post('/event', valid_event_data, format='json')

    # Check if the response status code is 201
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Event recorded successfully!"

    # Check if the event was saved in the database
    event = PackageEvent.objects.first()
    assert event is not None
    assert event.package == valid_event_data["package"]
    assert event.event_type == valid_event_data["event_type"]

# Test for failure when data is invalid (400 status code)
def test_create_event_failure(client, invalid_event_data):
    # Send POST request with invalid data
    response = client.post('/event', invalid_event_data, format='json')

    # Check if the response status code is 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "package" in response.data  # Ensure that the package field is included in errors

#####

# Test for successful response (200 status code)
@pytest.mark.django_db
def test_package_detail_success(client, mocker):
    # Mock the `fetch_pypi_package_data` function to return good data
    mock_data = {
        "info": {"name": "requests", "version": "2.25.1"},
        "releases": {
            "2.25.1": {"url": "https://pypi.org/project/requests/2.25.1/"}
        }
    }
    mocker.patch('events.views.fetch_pypi_package_data', return_value=mock_data)

    # Send GET request to the package detail view for 'requests'
    response = client.get('/package/requests/')

    # Check if the response status code is 200
    assert response.status_code == status.HTTP_200_OK

    # Check if the response contains the expected data
    assert response.data["info"] == mock_data["info"]
    assert response.data["releases"] == list(mock_data["releases"].keys())
    assert "events" in response.data
    # todo have some events in there

# Test for failed response (500 status code) due to ServiceException
def test_package_detail_service_failure(client, mocker):
    # Mock the `fetch_pypi_package_data` function to raise a ServiceException
    mocker.patch('events.views.fetch_pypi_package_data', side_effect=ServiceException('mock error'))

    # Send GET request to the package detail view for 'requests'
    response = client.get('/package/requests/')

    # Check if the response status code is 500
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Check if the response contains the expected error message
    assert response.data == {"error": "Unable to fetch package data from PyPI."}

#####

@pytest.fixture
def package_with_installs():
    # Create some installs for a package
    PackageEvent.objects.create(package="requests", event_type="install", timestamp="2024-12-23T12:00:00Z")
    PackageEvent.objects.create(package="requests", event_type="install", timestamp="2024-12-23T13:00:00Z")

@pytest.fixture
def package_without_installs():
    # Create a package with no installs
    PackageEvent.objects.create(package="flask", event_type="uninstall", timestamp="2024-12-23T12:00:00Z")

# Test for successful retrieval of total installs (200 status code)
@pytest.mark.django_db
def test_total_installs_success(client, package_with_installs):
    # Send GET request to fetch total installs for 'requests'
    response = client.get('/package/requests/event/install/total')

    # Check if the response status code is 200
    assert response.status_code == status.HTTP_200_OK
    # Ensure the total installs count is correct (2 installs for 'requests')
    assert response.data == 2

# Test for when there are no installs for a package (0 count)
@pytest.mark.django_db
def test_total_installs_no_installs(client, package_without_installs):
    # Send GET request to fetch total installs for 'flask'
    response = client.get('/package/flask/event/install/total')

    # Check if the response status code is 200
    assert response.status_code == status.HTTP_200_OK
    # Ensure the total installs count is 0 (no installs for 'flask')
    assert response.data == 0

# Test for successful retrieval of most recent install timestamp (200 status code)
@pytest.mark.django_db
def test_last_install_success(client, package_with_installs):
    # Send GET request to fetch the most recent install for 'requests'
    response = client.get('/package/requests/event/install/last')

    # Check if the response status code is 200
    assert response.status_code == status.HTTP_200_OK
    # Ensure the last install timestamp is correct (the later timestamp for 'requests')
    assert response.data == datetime.fromisoformat("2024-12-23T13:00:00Z".replace("Z", "+00:00"))

# Test for when there are no installs for a package (404 status code)
@pytest.mark.django_db
def test_last_install_no_installs(client, package_without_installs):
    # Send GET request to fetch the most recent install for 'flask'
    response = client.get('/package/flask/event/install/last')

    # Check if the response status code is 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # Ensure that the response body is None (or equivalent)
    assert response.data is None