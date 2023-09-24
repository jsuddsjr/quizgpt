from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Question, Choice


# Create your views here.
class QuestionListView(ListView):
    model = Question

    def __str__(self):
        return "Question List"


class QuestionDetailView(DetailView):
    model = Question

    def __str__(self):
        return "Question Detail"
