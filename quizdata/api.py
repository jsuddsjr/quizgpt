from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from chatapi.views import get_topic_subtopics
from .models import *
from .schema import *

api = NinjaAPI(
    csrf=True,
    title="QuizData API",
    description="This API is used to update the QuizGPT data models.",
)


@api.post("/ans", auth=django_auth)
def post_answer(request: HttpRequest, data: PostAnswerSchema) -> bool:
    choice = get_object_or_404(Choice, pk=data.cid)

    ## Move question to correct Leitner "box".
    question, _ = QuestionBucket.objects.get_or_create(user_id=request.user.id, question_id=choice.question.id)
    if choice.is_correct:
        question.bucket = min(question.bucket + 1, 7)
    else:
        question.bucket = max(question.bucket - 1, 1)
    question.save()

    ## Track how many times the answer was given.
    answer, _ = AnswerHistory.objects.get_or_create(user_id=request.user.id, choice_id=choice.id)
    answer.is_correct = choice.is_correct
    answer.count = answer.count + 1
    answer.save()

    all_choices = AnswerHistory.objects.filter(question_bucket=question)

    return choice.is_correct


@api.post("/top", auth=django_auth)
def post_topic(request: HttpRequest, data: PostTopicSchema):
    request.GET.append(vars(data))
    subtopics = get_topic_subtopics(request)

    topic = Topic.objects.create(topic_text=data.topic, owner=request.user)
    topic.save()

    for t in subtopics:
        subtopic = Topic.objects.create(
            subtopic_of=topic, topic_text=t.topic, description=t.description, topic_level=t.level
        )
        subtopic.save()


class UserSchema(Schema):
    username: str
    email: str
    first_name: str
    last_name: str


class Error(Schema):
    message: str


@api.get("/me", response={200: UserSchema, 403: Error})
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": "Please sign in first"}
    return request.user
