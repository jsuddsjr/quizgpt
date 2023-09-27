from django.urls import path
from .views import TopicDetailView, TopicListView
from .api import api

app_name = "quizdata"
urlpatterns = [
    path("api/", api.urls),
    path("<slug>/", TopicDetailView.as_view(), name="topic-detail"),
    path("", TopicListView.as_view(), name="topic-list"),
]
