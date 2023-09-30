from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView
from .models import QuestionBucket, Topic


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    paginate_by = 9

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(user=self.request.user, is_hidden=False, subtopic_of__isnull=False)


class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic


class QuestionReviewView(LoginRequiredMixin, ListView):
    model = QuestionBucket

    def get_queryset(self):
        return QuestionBucket.get_review_questions(self.request.user)
