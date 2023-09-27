from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from json.decoder import JSONDecoder

import openai

# Create your views here.
promptCreate = "Create 10 {level} 'multiple-choice' and 'fill-in-the-blank' questions about '{topic} {subtopic}'. Avoid using any part of the answer in the question."


@login_required
def get_topic_subtopics(request):
    if "topic" not in request.GET:
        return HttpResponseBadRequest(_("URL parameter 'topic' is required."))

    topic_text = request.GET.get("topic")
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

    json_response = _get_topic_subtopics(topic_text, topic_type, topic_level, topic_count)
    return HttpResponse(json_response, content_type="application/json")


promptTopic = "List {count} {type} of '{topic}' with brief description and estimated difficulty level: 1 is basic, 2 intermediate, and so on up to 5 levels. Response must include a minium of two levels."

promptTopicLevel = "List {count} level {level} {type} of '{topic}' where level 1 is beginner and 5 is complete mastery. Include a brief description."


def _get_topic_subtopics(
    topic_text: str, topic_type: str = "features or subtopics", topic_level: int = 1, topic_count: int = 5
) -> str:
    if topic_level:
        if topic_level == 5:
            topic_type = "esoteric, underrated" + topic_type
        prompt = promptTopicLevel.format(topic=topic_text, type=topic_type, level=topic_level, count=topic_count)
    else:
        prompt = promptTopic.format(topic=topic_text, type=topic_type, count=topic_count)

    messages = [
        {"role": "system", "content": "Act as expert."},
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": "Return ONLY JSON as array of objects with fields 'topic' (string), 'description' (string), 'topic_level' (number).",
        },
    ]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages)
    json_response = completion.choices[0].message.content
    return json_response


@login_required
def get_topic_questions(request):
    from quizdata.models import Topic

    if request != None:
        topic_slug = request.GET["slug"]

    topic = get_object_or_404(Topic, slug=topic_slug)
    messages = [
        {"role": "system", "content": "Act as college tutor."},
        {"role": "user", "content": promptCreate.format(level=topic.topic_level, topic=topic.topic_text, subtopic="")},
        {
            "role": "assistant",
            "content": "Return ONLY JSON as array of objects with fields 'question' (string), 'question_type' ('multiple-choice' or 'fill-in-the-blank'), array of 'answers' (even if only one answer), and 'answer_index' (number).",
        },
    ]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, temperature=1.1)
    json_response = completion["choices"][0]["message"]["content"]
    return HttpResponse(json_response, content_type="application/json")


def parse_json_response(json):
    from quizdata.models import Question, Choice

    quiz = JSONDecoder().decode(json)
    for question in quiz:
        q = Question()
        q.question_text = question.question
        q.save()

        for i, ans in enumerate(question.answers):
            o = Choice()
            o.question = q
            o.option_text = ans
            o.choice_order = i
            if i == question.answer_index:
                o.is_correct = True
            o.save()

    return quiz


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    print(_get_topic_subtopics("c++"))
    print(_get_topic_subtopics("c++", topic_level=3))
    print(_get_topic_subtopics("c++", topic_level=5))

    # get_topic_questions(None, "Vue.js", "databinding", "advanced")

    json_text = '[\n  {\n    "question": "What is databinding in Vue.js?",\n    "question_type": "multiple-choice",\n    "answers": ["A mechanism for synchronizing the data between the view and the model", "A technique for manipulating the DOM directly", "A library for managing state in JavaScript applications"],\n    "answer_index": 0\n  },\n  {\n    "question": "How can you achieve one-way databinding in Vue.js?",\n    "question_type": "multiple-choice",\n    "answers": ["By using v-bind directive", "By using v-model directive", "By using v-on directive"],\n    "answer_index": 0\n  },\n  {\n    "question": "Fill in the blank: Two-way databinding in Vue.js can be accomplished using the ----------- directive.",\n    "question_type": "fill-in-the-blank",\n    "answers": ["v-model"],\n    "answer_index": 0\n  },\n  {\n    "question": "What is the purpose of the v-bind directive in Vue.js?",\n    "question_type": "multiple-choice",\n    "answers": ["To bind an element\'s property or attribute to a JavaScript expression", "To bind an element\'s content to a variable", "To trigger an event when an element is clicked"],\n    "answer_index": 0\n  },\n  {\n    "question": "What is the difference between v-bind and v-model directives in Vue.js?",\n    "question_type": "multiple-choice",\n    "answers": ["v-bind is used for one-way databinding, while v-model enables two-way databinding", "v-bind is used for two-way databinding, while v-model enables one-way databinding", "There is no difference, they can be used interchangeably"],\n    "answer_index": 0\n  }\n]'
    parse_json_response(json_text)
    # print(run_conversation(None, None))

# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Who won the world series in 2020?"},
#         {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#         {"role": "user", "content": "Where was it played?"}
#     ]
# )

# print(completion.choices[0].message.content)
