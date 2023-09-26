from django.urls import path
from .views import get_topic_subtopics, get_topic_questions

app_name = "api"
urlpatterns = [
    path("", get_topic_subtopics, name="subtopic"),
    path("<slug>", get_topic_questions, name="topic-detail"),
]