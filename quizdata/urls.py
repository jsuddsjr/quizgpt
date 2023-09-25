from django.urls import path
from .views import TopicDetailView, TopicListView

app_name = "quizdata"
urlpatterns = [
    path("", TopicListView.as_view(), name="topic-list"),
    path("<slug>", TopicDetailView.as_view(), name="topic-detail"),
]
