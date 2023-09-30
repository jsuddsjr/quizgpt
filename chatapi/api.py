from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from ninja import Router, Schema
from ninja.security import django_auth
from typing import List

import openai

from quizdata.models import Topic

router = Router()

# Create your views here.
promptCreate = """
    Create {count} 'multiple-choice' about '{topic} {subtopic}'.
    All questions must be {level} level or higher.
    Avoid using any part of the answer in the question.
"""

levels = ["", "beginner", "intermediate", "advanced", "expert", "master"]

promptTopic = """
List {count} {type} of '{topic}' with brief description and estimated difficulty level where 1 is beginner,
2 intermediate, and so on up to 5, complete mastery. Response must include at least two levels of topics.
"""

promptTopicLevel = """
List {count} level {level} {type} of '{topic}' where level 1 is beginner and 5 is complete mastery.
Include a brief description.
"""


class TopicSubtopicsResponseSchema(Schema):
    topic: str
    description: str
    topic_level: int


@router.get(
    "/{slug}/subtopics",
    auth=django_auth,
    response=TopicSubtopicsResponseSchema,
    tags=["subtopics"],
    summary="Get subtopics for a topic",
)
def get_topic_subtopics(request, slug: str) -> HttpResponse:
    topic = get_object_or_404(Topic, slug=slug)

    topic_type = request.GET.get("type", "features or subtopics")
    topic_level = request.GET.get("level", 0)
    topic_count = request.GET.get("count", 5)

    try:
        topic_level = int(topic_level)
    except ValueError:
        return HttpResponseBadRequest(_("URL parameter 'level' must be integer."))
    if not (0 <= topic_level <= 5):
        return HttpResponseBadRequest(_("URL parameter 'level' must be in range 0 to 5."))

    try:
        topic_count = int(topic_count)
    except ValueError:
        return HttpResponseBadRequest(_("URL parameter 'count' must be integer."))
    if not (0 < topic_count <= 15):
        return HttpResponseBadRequest(_("URL parameter 'count' must be in range 1 to 15."))

    json_response = _get_topic_subtopics(topic.topic_text, topic_type, topic_level, topic_count)
    return HttpResponse(json_response, content_type="application/json")


def _get_topic_subtopics(
    topic_text: str, topic_type: str = "features or subtopics", topic_level: int = 1, topic_count: int = 5
) -> str:
    if topic_level:
        if topic_level == 5:
            topic_type = "esoteric, underrated " + topic_type
        prompt = promptTopicLevel.format(topic=topic_text, type=topic_type, level=topic_level, count=topic_count)
    else:
        prompt = promptTopic.format(topic=topic_text, type=topic_type, count=topic_count)

    messages = [
        {"role": "system", "content": "Act as expert system."},
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": "Return ONLY JSON array of objects with fields 'topic' (string), 'description' (string), 'topic_level' (number).",
        },
    ]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages)
    json_response = completion.choices[0].message.content
    return json_response


class TopicQuestionsResponseSchema(Schema):
    question: str
    answers: List[str]
    answer_index: int


@router.get(
    "/{slug}/questions",
    auth=django_auth,
    response=TopicQuestionsResponseSchema,
    tags=["questions"],
    summary="Get questions for a subtopic",
)
def get_topic_questions(request, slug: str) -> HttpResponse:
    topic = get_object_or_404(Topic, slug=slug)

    if topic.user != request.user:
        return HttpResponseBadRequest(_("Topic does not belong to user."))
    if topic.is_hidden:
        return HttpResponseBadRequest(_("Topic is hidden."))
    if topic.subtopic_of is None:
        return HttpResponseBadRequest(_("Topic is not a subtopic."))

    topic_level = request.GET.get("level", 0)
    question_count = request.GET.get("count", 5)

    json_response = _get_topic_questions(topic.subtopic_of.topic_text, topic.topic_text, topic_level, question_count)
    return HttpResponse(json_response, content_type="application/json")


def _get_topic_questions(topic_text: str, subtopic_text: str, topic_level: int = 1, question_count: int = 5) -> str:
    messages = [
        {"role": "system", "content": "Act as college tutor."},
        {
            "role": "user",
            "content": promptCreate.format(
                level=levels[topic_level], topic=topic_text, subtopic=subtopic_text, count=question_count
            ),
        },
        {
            "role": "assistant",
            "content": "Return ONLY JSON array of objects with fields 'question' (string), 'answers' (array), and 'answer_index' (number).",
        },
    ]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, temperature=1.1)
    json_response = completion.choices[0].message.content
    return json_response
