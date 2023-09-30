from django.http import HttpRequest
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from ninja import Router
from ninja.security import django_auth

from chatapi.api import TopicQuestionsResponseSchema, _get_topic_subtopics, _get_topic_questions

from .models import *
from .schema import *

import json

router = Router()


@router.post(
    "/ans",
    auth=django_auth,
    tags=["quizdata"],
    summary="Record an answer in the database",
    response={200: PostAnswerResponseSchema},
)
@transaction.atomic
def post_answer(request: HttpRequest, data: PostAnswerSchema) -> PostAnswerResponseSchema:
    choice = get_object_or_404(Choice, pk=data.cid)

    ## Move question to correct Leitner "box".
    question, _ = QuestionBucket.objects.get_or_create(user=request.user, question=choice.question)
    if choice.is_correct:
        question.bucket = min(question.bucket + 1, 7)
    else:
        question.bucket = max(question.bucket - 1, 0)
    question.save()

    ## Track how many times the answer was given.
    answer, _ = AnswerHistory.objects.get_or_create(user=request.user, choice=choice, question_bucket=question)
    answer.is_correct = choice.is_correct
    answer.count = answer.count + 1
    answer.save()

    history = AnswerHistory.objects.filter(question_bucket=question)
    return PostAnswerResponseSchema(correct=choice.is_correct, bucket=question, history=history)


@router.post(
    "/top",
    auth=django_auth,
    tags=["quizdata"],
    summary="Request new subtopics for the specified topic",
    response={200: PostTopicResponseSchema, 400: ErrorMessage},
)
@transaction.atomic
def post_topic(request: HttpRequest, data: PostTopicSchema) -> PostTopicResponseSchema:
    slug = data.slug or (slugify(data.topic) + "-" + request.user.username)
    topic, _ = Topic.objects.get_or_create(slug=slug, user=request.user)
    topic.slug = slug
    topic.topic_text = data.topic
    topic.topic_level = data.level
    topic.save()

    json_str = _get_topic_subtopics(data.topic)
    records = json.loads(json_str)

    try:
        for entry in records:
            subtopic = Topic.objects.create(
                topic_text=entry["topic"],
                subtopic_of=topic,
                user=request.user,
                description=entry["description"],
                topic_level=entry["topic_level"],
            )
            subtopic.save()
        response = PostTopicResponseSchema(topic=topic, subtopics=Topic.objects.filter(subtopic_of=topic))
        return response
    except Exception as e:
        return 400, ErrorMessage(error=str(e), data=json_str)


@router.post(
    "/top/{slug}/qst",
    auth=django_auth,
    tags=["quizdata"],
    summary="Request new questions for a subtopic",
    response={200: PostQuestionResponseSchema, 400: ErrorMessage},
)
def post_question(request: HttpRequest, slug: str, data: PostQuestionSchema):
    topic = get_object_or_404(Topic, slug=slug)

    if topic.user and topic.user != request.user:
        return 400, ErrorMessage(error=_("Topic does not belong to you."))
    if topic.subtopic_of is None:
        return 400, ErrorMessage(error=_("Topic is not a subtopic."))

    json_str = _get_topic_questions(topic.subtopic_of.topic_text, topic.topic_text, topic.topic_level, data.count)

    try:
        records = json.loads(json_str)
        question_ids = list(map(lambda row: _process_question(topic, request.user, row), records))
        return PostQuestionResponseSchema(topic_id=topic.id, questions=question_ids)
    except Exception as e:
        return 400, ErrorMessage(error=str(e), data=json_str)


@transaction.atomic
def _process_question(topic: Topic, user: User, data: dict) -> int:
    question = Question.objects.create(question_text=data["question"], question_type="M", topic=topic)
    question.save()

    bucket = QuestionBucket.objects.create(user=user, question=question, bucket=0)
    bucket.save()

    answer_index = dict["answer_index"]
    for index, ans in enumerate(data["answers"]):
        choice = Choice.objects.create(
            choice_text=ans,
            question=question,
            order=index,
        )
        if index == answer_index:
            choice.is_correct = True
        choice.save()

    return question.id
