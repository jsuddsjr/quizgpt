from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Topic, Question, Choice


class TopicListView(ListView):
    model = Topic

    def __str__(self):
        return "Topic List"


class TopicDetailView(DetailView):
    model = Topic

    def __str__(self):
        return self.get_object()


# Create your views here.
class QuestionListView(ListView):
    model = Question

    def __str__(self):
        return "Question List"


class QuestionDetailView(DetailView):
    model = Question

    def __str__(self):
        return self.get_object()
