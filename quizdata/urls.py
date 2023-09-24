from django.urls import path
from .views import QuestionListView, QuestionDetailView

app_name = "quizdata"
urlpatterns = [
    path("", QuestionListView.as_view(), name="list"),
    path("<slug>", QuestionDetailView.as_view(), name="detail"),
    ## path("<record_slug>/<schedule_slug>/", ScheduleDetailView.as_view(), name="record-detail"),
]
