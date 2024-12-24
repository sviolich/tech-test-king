from django.urls import path
from .views import PackageView, EventView, PackageLastInstallView, PackageTotalInstallsView

urlpatterns = [
    path('event', EventView.as_view(), name='event'),
    # todo consider moving the below to a new packages app?
    path('package/<str:package>/', PackageView.as_view(), name='package_detail'),
    path('package/<str:package>/event/install/total', PackageTotalInstallsView.as_view(), name='package_install_total'),
    path('package/<str:package>/event/install/last', PackageLastInstallView.as_view(), name='package_install_last'),
]
