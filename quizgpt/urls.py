"""
URL configuration for quizgpt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

# from django.views import debug

from paper.views import PaperQuestionReorder
from quizdata.views import QuestionReviewView

from .api import api

admin.autodiscover()
urlpatterns = [
    ## path("", debug.default_urlconf),
    path("__debug__/", include("debug_toolbar.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("change-password/", auth_views.PasswordChangeView.as_view(), name="change-password"),
    path("paper/", PaperQuestionReorder.as_view()),
    path("quizdata/", include("quizdata.urls")),
    path("", QuestionReviewView.as_view(), name="question-review"),
]
