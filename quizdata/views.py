from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Topic


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic

    def __str__(self):
        return "Topic List"


class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic

    def __str__(self):
        return self.object.topic_text
