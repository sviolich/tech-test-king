import requests

from django.core.cache import cache

from .exceptions import ServiceException

# todo note i moved this service
# todo add type hints
def fetch_pypi_package_data(package):
    """
    Fetches package data from PyPI and caches it for 1 day.
    :param package: The name of the package to fetch.
    :return: The JSON response from PyPI if successful, or None if an error occurs.
    """
    cache_key = f"pypi_package_{package}"
    pypi_data = cache.get(cache_key)

    # todo proper logging
    # print("cache HIT" if pypi_data else "cache MISS")

    if not pypi_data:
        # Fetch data from PyPI if not cached
        pypi_url = f"https://pypi.python.org/pypi/{package}/json"
        try:
            pypi_response = requests.get(pypi_url)
            pypi_response.raise_for_status()
            pypi_data = pypi_response.json()
            # Cache the response for 1 day (86400 seconds)
            cache.set(cache_key, pypi_data, timeout=86400)
        except requests.RequestException as e:
            raise ServiceException("Failed to fetch package data", inner_exception=e)

    return pypi_data
