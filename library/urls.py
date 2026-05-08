from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet, basename="book")

urlpatterns = [path("", include(router.urls))]


app_name = "library"
