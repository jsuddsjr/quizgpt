from django.urls import path
from .views import QuestionReviewView, TopicDetailView, TopicListView
from .api import api

app_name = "quizdata"
urlpatterns = [
    path("api/", api.urls),
    path("topics/", TopicListView.as_view(), name="topic-list"),
    path("<slug>", TopicDetailView.as_view(), name="topic-questions"),
    path("", QuestionReviewView.as_view(), name="question-review"),
]
