from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import NinjaAPI
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
def post_answer(request: HttpRequest, data: PostAnswerSchema) -> PostAnswerResponseSchema:
    choice = get_object_or_404(Choice, pk=data.cid)

    ## Move question to correct Leitner "box".
    question, _ = QuestionBucket.objects.get_or_create(user=request.user, question=choice.question)
    if choice.is_correct:
        question.bucket = min(question.bucket + 1, 7)
    else:
        question.bucket = max(question.bucket - 1, 1)
    question.save()

    ## Track how many times the answer was given.
    answer, _ = AnswerHistory.objects.get_or_create(user=request.user, choice=choice, question_bucket=question)
    answer.is_correct = choice.is_correct
    answer.count = answer.count + 1
    answer.save()

    history = AnswerHistory.objects.filter(question_bucket=question)
    return PostAnswerResponseSchema(correct=choice.is_correct, bucket=question, history=history)


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


@api.get("/me", response={200: UserSchema, 403: ErrorSchema})
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": "Please sign in first"}
    return request.user
