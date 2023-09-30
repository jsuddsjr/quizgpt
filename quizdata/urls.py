from django.urls import path
from .views import QuestionReviewView, TopicDetailView, TopicListView

app_name = "quizdata"
urlpatterns = [
    path("topics/", TopicListView.as_view(), name="topic_list"),
    path("topics/<slug>", TopicDetailView.as_view(), name="topic_questions"),
    path("", QuestionReviewView.as_view(), name="question_review"),
]
