from django.db.models import Count, Max

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .exceptions import ServiceException
from .models import PackageEvent
from .serializers import PackageEventSerializer
from .services import fetch_pypi_package_data

class EventView(APIView):
    def post(self, request):
        serializer = PackageEventSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"message": "Event recorded successfully!"}, status=status.HTTP_201_CREATED)


class PackageView(APIView):
    def get(self, request, package):
        # Fetch PyPI package data
        try:
            pypi_data = fetch_pypi_package_data(package)
        except ServiceException:
            # todo add test for 500
            return Response({"error": "Unable to fetch package data from PyPI."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Aggregate events for the package
        events = PackageEvent.objects.filter(package=package).values('event_type').annotate(
            count=Count('id'),
            last=Max('timestamp')
        )

        event_data = {event['event_type']: {"count": event['count'], "last": event['last']} for event in events}

        # Construct the response
        response_data = {
            "info": pypi_data.get("info", {}),
            "releases": list(pypi_data.get("releases", {}).keys()),
            "events": event_data,
        }

        # todo add test for 200
        return Response(response_data, status=status.HTTP_200_OK)

class PackageTotalInstallsView(APIView):
    def get(self, request, package):
        # Count total installs for the specified package
        total_installs = PackageEvent.objects.filter(package=package, event_type='install').count()
        return Response(total_installs, status=status.HTTP_200_OK)


class PackageLastInstallView(APIView):
    def get(self, request, package):
        # Get the most recent installation timestamp for the specified package
        # todo is this an efficient way to get last?
        last_install = PackageEvent.objects.filter(package=package, event_type='install').aggregate(
            last=Max('timestamp')
        )['last']

        if not last_install:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        return Response(last_install, status=status.HTTP_200_OK)
