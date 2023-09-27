from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth
from .models import Choice, ChoiceAnswer

api = NinjaAPI(
    csrf=True,
    urls_namespace="quizdata",
    title="QuizData API",
    description="This API is used to update the QuizGPT data models.",
)


class CidSchema(Schema):
    cid: str


@api.post("/ans", auth=django_auth)
def post_answer(request, data: CidSchema):
    choice = get_object_or_404(Choice, pk=data.cid)
    last_answer = ChoiceAnswer.objects.filter(choice=choice).latest()

    ## Create a record of this selection, along with current bucket.
    answer = ChoiceAnswer(user=request.user, choice=choice)
    if choice.is_correct:
        answer.is_correct = True
        answer.bucket = min(last_answer.bucket + 1, 7)
    else:
        answer.bucket = max(last_answer.bucket - 1, 1)

    answer.save()
    return 204


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
