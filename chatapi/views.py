from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from json.decoder import JSONDecoder

import openai

# Create your views here.
promptCreate = "Create 10 {level} 'multiple-choice' and 'fill-in-the-blank' questions about '{topic} {subtopic}'. Avoid using any part of the answer in the question."

promptTopic = "List 5 features or subtopics of '{topic}', with best estimate of level: 1 (basic), 2 (intermediate), or 3 (advanced). Do not include numbers or level names in the subtopic text."

promptTopicLevel = "List 5 level {level} features or subtopics of '{topic}', where level 1 is basic, 2 is intermediate, and 3 is advanced. Do not include numbers or level names in the subtopic text."


@login_required
def get_topic_subtopics(request, **kwargs):
    topic_text = None
    topic_level = None

    if request:
        if "topic" in request.GET:
            topic_text = request.GET["topic"]
        if "level" in request.GET:
            topic_level = request.GET["level"]
    else:
        if "topic" in kwargs:
            topic_text = kwargs["topic"]
        if "level" in kwargs:
            topic_level = kwargs["level"]

    if topic_text and topic_level:
        prompt = promptTopicLevel.format(topic=topic_text, level=topic_level)
    elif topic_text:
        prompt = promptTopic.format(topic=topic_text)
    else:
        return HttpResponseBadRequest("URL parameter 'topic' is required.")

    messages = [
        {"role": "system", "content": "Act as college tutor."},
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": "Format as array of JSON objects with fields 'topic' (string), 'topic_level' (number).",
        },
    ]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages)
    json_response = completion["choices"][0]["message"]["content"]
    return HttpResponse(json_response, content_type="application/json")


@login_required
def get_topic_questions(request, topic_slug):
    from quizdata.models import Topic

    if request != None:
        topic_slug = request.GET["slug"]

    topic = get_object_or_404(Topic, slug=topic_slug)
    messages = [
        {"role": "system", "content": "Act as college tutor."},
        {"role": "user", "content": promptCreate.format(level=topic.topic_level, topic=topic.topic_text, subtopic="")},
        {
            "role": "assistant",
            "content": "Format as JSON objects with fields 'question', 'question_type' ('multiple-choice' or 'fill-in-the-blank'), array of 'answers' (even if only one answer), and 'answer_index'.",
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


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


def run_conversation(request, location):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "What's the weather in Boston?"}]
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    print(get_topic_subtopics(None, topic_text="Vue.js"))
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
