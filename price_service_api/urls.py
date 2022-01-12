from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from price_service_api import views

app_name = "price_service_api"
urlpatterns = [
    path(
        "quotes/",
        views.PriceList.as_view(),
        name="list-prices",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
