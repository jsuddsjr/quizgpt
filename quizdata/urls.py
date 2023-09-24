from django.urls import path
from .views import TopicDetailView, TopicListView, QuestionListView, QuestionDetailView

app_name = "quizdata"
urlpatterns = [
    path("", TopicListView.as_view(), name="topic-list"),
    path("<slug>", TopicDetailView.as_view(), name="topic-detail"),
    ## path("<record_slug>/<schedule_slug>/", ScheduleDetailView.as_view(), name="record-detail"),
]
