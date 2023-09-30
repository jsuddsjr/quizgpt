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


@router.post("/ans", auth=django_auth)
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


@router.post("/top", auth=django_auth)
def post_topic(request: HttpRequest, data: PostTopicSchema) -> PostTopicResponseSchema:
    slug = data.slug or (slugify(data.topic) + "-" + request.user.username)
    topic, _ = Topic.objects.get_or_create(slug=slug, user=request.user)
    topic.slug = slug
    topic.topic_text = data.topic
    topic.topic_level = data.level
    topic.save()

    json_str = _get_topic_subtopics(data.topic)
    blob = json.loads(json_str)

    for entry in blob:
        if entry is str:
            entry = blob[entry]
            continue
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


@router.post("/top/{slug}/qst", auth=django_auth)
def post_question(request: HttpRequest, slug: str, data: PostQuestionSchema) -> PostQuestionResponseSchema:
    topic = get_object_or_404(Topic, slug)

    if topic.user != request.user:
        return ErrorMessage(_("Topic does not belong to you."))
    if topic.is_hidden:
        return ErrorMessage(_("Topic is hidden."))
    if topic.subtopic_of is None:
        return ErrorMessage(_("Topic is not a subtopic."))

    json_str = _get_topic_questions(topic.subtopic_of.topic_text, topic.topic_text, topic.topic_level, data.count)
    records = json.loads(json_str, object_hook=lambda d: TopicQuestionsResponseSchema(**d))
    response = list(map(lambda row: _process_question(topic, request.user, row), records))
    return response


@transaction.atomic
def _process_question(topic: Topic, user: User, data: TopicQuestionsResponseSchema) -> QuestionSchema:
    question = Question.objects.create(question_text=data.question, question_type="M", topic=topic)
    question.save()

    bucket = QuestionBucket.objects.create(user=user, question=question, bucket=0)
    bucket.save()

    for index, choice in enumerate(data.choices):
        choice = Choice.objects.create(
            choice_text=choice,
            question=question,
            order=index,
        )
        if index == data.answer_index:
            choice.is_correct = True
        choice.save()

    return QuestionSchema.from_orm(question)
