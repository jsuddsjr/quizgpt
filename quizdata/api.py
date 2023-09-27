from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ninja import NinjaAPI, Schema
from ninja.security import django_auth
from .models import Choice, ChoiceAnswer

api = NinjaAPI(
    csrf=True,
    title="QuizData API",
    description="This API is used to update the QuizGPT data models.",
)


class CidSchema(Schema):
    cid: str


@api.post("/ans", auth=django_auth)
def post_answer(request, data: CidSchema) -> bool:
    choice = get_object_or_404(Choice, pk=data.cid)

    question, _ = ChoiceAnswer.objects.get_or_create(
        user_id=request.user.id, question_id=choice.question.id, choice__isnull=True
    )

    ## Move question to Leitner "box".
    if choice.is_correct:
        question.bucket = min(question.bucket + 1, 7)
    else:
        question.bucket = max(question.bucket - 1, 1)

    answer, _ = ChoiceAnswer.objects.get_or_create(
        user_id=request.user.id, question_id=choice.question.id, choice_id=choice.id
    )

    answer.is_correct = choice.is_correct
    answer.count = answer.count + 1

    question.save()
    answer.save()

    return choice.is_correct


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
