from typing import List

from django.http import HttpRequest
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from ninja import Router
from ninja.security import django_auth

from chatapi.api import _get_topic_subtopics, _get_topic_questions

from .models import *
from .schema import *

import json

router = Router()


## Errors
def TOPIC_DOES_NOT_BELONG_TO_YOU() -> ErrorMessage:
    ErrorMessage(error=_("Topic does not belong to you."))


def LEVEL_MUST_BE_BETWEEN_1_AND_5() -> ErrorMessage:
    ErrorMessage(error=_("Level must be between 1 and 5."))


def TOPIC_IS_NOT_A_SUBTOPIC() -> ErrorMessage:
    ErrorMessage(error=_("Topic is not a subtopic."))


####################
## Topics
####################


@router.get(
    "/",
    auth=django_auth,
    tags=["topic"],
    summary=_("Get all root topics, even hidden ones"),
    response={200: List[TopicSchema]},
)
def get_topics(request: HttpRequest) -> List[TopicSchema]:
    return Topic.objects.filter(user=request.user, subtopic_of=None)


@router.get(
    "/suggest",
    auth=django_auth,
    tags=["topic"],
    summary=_("Suggestions for new topics to study"),
    response={200: List[TopicSchema]},
)
def get_suggested_topics(request: HttpRequest, data: SuggestTopicQuerySchema):
    return Topic.objects.filter(user=None, subtopic_of=None, is_hidden=False)


@router.get(
    "/{slug}",
    auth=django_auth,
    tags=["topic"],
    summary=_("Get all subtopics for the specified topic and (optional) level"),
    response={200: List[TopicSchema], 404: None, 400: ErrorMessage},
)
def get_subtopics(request: HttpRequest, slug: str, level: int = 0):
    topic = get_object_or_404(Topic, slug=slug)
    if topic.user and topic.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    if level:
        if level < 1 or level > 5:
            return 400, LEVEL_MUST_BE_BETWEEN_1_AND_5()
        return Topic.objects.filter(user=request.user, subtopic_of=topic, topic_level=level, is_hidden=False)
    else:
        return Topic.objects.filter(user=request.user, subtopic_of=topic, is_hidden=False)


@router.post(
    "/{slug}/suggest",
    auth=django_auth,
    tags=["topic"],
    summary="Request new subtopics for the specified topic",
    response={200: PostTopicResponseSchema, 400: ErrorMessage},
)
@transaction.atomic
def post_topic(request: HttpRequest, slug: str, data: SuggestTopicQuerySchema):
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


@router.put(
    "/{slug}",
    auth=django_auth,
    tags=["topic"],
    summary=_("Update the specified topic"),
    response={200: TopicSchema, 400: ErrorMessage},
)
def update_topic(request: HttpRequest, slug: str, data: TopicSchemaUpdate):
    topic = get_object_or_404(Topic, slug=slug)
    if topic.user and topic.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    if data.user and data.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    topic.topic_text = data.topic_text
    topic.description = data.description
    topic.topic_level = data.topic_level
    topic.is_hidden = data.is_hidden
    topic.save()
    return topic


@router.get(
    "/{slug}/{subslug}",
    auth=django_auth,
    tags=["topic"],
    summary=_("Get all questions for the specified topic and (optional) level"),
    response={200: List[QuestionSchema], 404: None, 400: ErrorMessage},
)
def get_questions(request: HttpRequest, slug: str, subslug: str):
    topic = get_object_or_404(Topic, slug=subslug, subtopic_of__slug=slug)
    if topic.user and topic.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    if topic.subtopic_of is None:
        return 400, TOPIC_IS_NOT_A_SUBTOPIC()
    return topic.question_set.filter(is_suppressed=False)


@router.put(
    "/{slug}/{subslug}",
    auth=django_auth,
    tags=["topic"],
    summary=_("Add questions to the specified topic"),
    response={200: List[QuestionSchema], 404: None, 400: ErrorMessage},
)
def put_questions(request: HttpRequest, slug: str, subslug: str, data: List[SuggestQuestionResponseSchema]):
    topic = get_object_or_404(Topic, slug=subslug, subtopic_of__slug=slug)
    if topic.user and topic.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    if topic.subtopic_of is None:
        return 400, TOPIC_IS_NOT_A_SUBTOPIC()

    return list(map(lambda row: _process_question(topic, request.user, row), data))


@router.get(
    "/{slug}/{subslug}/suggest",
    auth=django_auth,
    tags=["topic"],
    summary=_("Suggest questions for the specified topic"),
    response={200: List[SuggestQuestionResponseSchema], 400: ErrorMessage},
)
def post_question(request: HttpRequest, slug: str, subslug: str, count: int = 5):
    topic = get_object_or_404(Topic, slug=subslug, subtopic_of__slug=slug)
    if topic.user and topic.user != request.user:
        return 400, TOPIC_DOES_NOT_BELONG_TO_YOU()
    if topic.subtopic_of is None:
        return 400, TOPIC_IS_NOT_A_SUBTOPIC()

    json_str = _get_topic_questions(topic.subtopic_of.topic_text, topic.topic_text, topic.topic_level, count)

    try:
        return 200, json.loads(json_str)
    except Exception as e:
        return 400, ErrorMessage(error=str(e), data=json_str)


@router.get(
    "/question/{qid}",
    auth=django_auth,
    summary=_("Get the specified question"),
    tags=["question"],
    response={200: QuestionSchema, 403: ErrorMessage, 404: None},
)
def get_question(request: HttpRequest, qid: int) -> QuestionSchema:
    question = get_object_or_404(Question, pk=qid)
    if (question.topic.user and question.topic.user != request.user) or question.topic.is_hidden:
        return 403, ErrorMessage(error=_("Question does not belong to you."))
    return question.get_randomized_choices()


## Answer History
@router.get(
    "/question/{qid}/answer",
    auth=django_auth,
    tags=["question"],
    summary=_("Get all answers for the specified question"),
    response={200: GetAnswerResponseSchema},
)
def get_answer(request: HttpRequest, qid: int) -> List[AnswerHistorySchema]:
    return AnswerHistory.objects.filter(user=request.user, choice__question__id=qid)


@router.put(
    "/question/{qid}",
    auth=django_auth,
    summary=_("Update the specified question"),
    tags=["question"],
    response={200: QuestionSchema, 403: ErrorMessage, 404: None},
)
def update_question(request: HttpRequest, qid: int, data: QuestionSchemaUpdate):
    question = get_object_or_404(Question, pk=qid)
    if (question.topic.user and question.topic.user != request.user) or question.topic.is_hidden:
        return 403, ErrorMessage(error=_("Question does not belong to you."))
    question.question_text = data.question_text
    question.is_suppressed = data.is_suppressed
    question.save()
    return 204, None


@router.post(
    "/choice/{cid}/answer",
    auth=django_auth,
    tags=["choice"],
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


@router.delete(
    "/answer/{cid}",
    auth=django_auth,
    tags=["answer"],
    summary="Delete answers from the database",
    response={404: None, 403: None, 200: None},
)
@transaction.atomic
def delete_answer(request: HttpRequest, cid: int) -> None:
    answers = AnswerHistory.objects.filter(user=request.user, choice=cid)
    [count, deleted] = answers.delete()
    return 200, f"Deleted {count} records."


@transaction.atomic
def _process_question(topic: Topic, user: User, data: SuggestQuestionResponseSchema) -> QuestionSchema:
    question = Question.objects.create(question_text=data.question, question_type="M", topic=topic)
    bucket = QuestionBucket.objects.create(user=user, question=question, bucket=0)

    for index, answer in enumerate(data.answers):
        choice = question.choice_set.create(choice_text=answer, order=index, is_correct=(index == data.answer_index))
        choice.save()

    question.save()
    bucket.save()

    return question
