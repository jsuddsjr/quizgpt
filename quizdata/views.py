from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Topic, Question, Choice


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic

    def __str__(self):
        return "Topic List"


class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic

    def __str__(self):
        return self.object.topic_text
