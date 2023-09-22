from django.views.generic import RedirectView
from django.urls import path

appName = "openai"
urlpatterns = [
    path("", RedirectView.as_view(url="catalog/", permanent=True)),
]
