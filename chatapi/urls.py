from django.urls import path
from .views import get_topic_subtopics, get_topic_questions

app_name = "chatapi"
urlpatterns = [
    path("", get_topic_subtopics, name="topic-subtopic"),
    path("<slug>/", get_topic_questions, name="topic_questions"),
]
