from django.urls import path
from django.views.generic import RedirectView

from .views import QuestionReviewView, TopicDetailView, TopicListView

app_name = "quizdata"
urlpatterns = [
    path("topics/", TopicListView.as_view(), name="topic_list"),
    path("topics/<slug>", TopicDetailView.as_view(), name="topic_questions"),
    path("review/", QuestionReviewView.as_view(), name="question_review"),
    path("", RedirectView.as_view(url="review/"), name="index"),
]
