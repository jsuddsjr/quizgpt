# QuizGPT

## Overview

As a software engineer, I'm fascinated by the potential for **AI like ChatGPT** to disrupt the industry. This project is my first attempt at incorporating ChatGPT into a project. Plus, I decided to write it in **Python using the Django web framework**, also my first-ever attempt.

I discovered after I started, that everyone seems to like the Quiz app. I found loads of examples for models that supported Questions and Answers, but none of them did what I wanted to do--namely, store the questions in a way that I could review them on a timeline, a proven way to learn faster. (Look up Leitner Method, if you want to know more. The link is below.)

### Shocking Demo Link

To keep myself honest, I'm going to demonstrate the app almost two weeks after I started. **Brace yourself.** (Remember, this is the first attempt at learning Django and ChatGPT prompt engineering.)

[Software Demo Video](https://somup.com/c0QvrxBbze)

## Review Schedule

Each time you answer a question, its bucket assignment will change depending on whether
you got the answer right or wrong. Each question will then be added to your review schedule
based on its bucket. (This is loosely based on the [Leitner System for flashcard review](https://e-student.org/leitner-system).)

| Bucket | Review again in... |
| ---    | ---                |
| 1      | 1 day              |
| 2      | 3 days             |
| 3      | 7 days             |
| 4      | 14 days            |
| 5      | 28 days            |
| 6      | 60 days            |
| 7      | 90 days            |

## Web Pages

The app has two main pages:

* *Review* - This page is where I hoped you could see the questions you needed to review today.
* *Topics* - This page would let you select new topics of study, and set your desired level of difficulty.

## Development Environment

These are the main technologies used (most were unknown to me two weeks ago).

* *OpenAI* - ChatGPT is the star of this show.
* *Django* - I'm really impressed with this framework, which includes View and Form widgets, as well as database Models.
* *NinjaAPI for Django* - I needed a REST API, and the NinjaAPI decorators and automatic OpenAPI docs were handy.
* *SQLite3* - To keep it simple, I choose to use a basic local database engine.
* *Bootstrap 4* - Still a good choice for adaptive UI design.

And some minor players:

* *CrunchyForms* - They had a form for creating new users and I needed one quick. I only used Crunchy for one page, but WOW! Color me impressed.
* *Poetry* - I'm using the Poetry package manager to take care of my dependencies.

Since I'm using the Django framework to host the service, I also wrote some handy Tasks for Visual Studio code so I could save myself from typing and retying the `manage.py` command line. **Ugh.**

## Useful Websites

Here's a list of websites that I found helpful in this project.

* [Django documentation](https://docs.djangoproject.com/en/4.2/)
* [Introduction to Custom Actions and Bulk Actions in Django](https://dev.to/ahmed__elboshi/introduction-to-custom-actions-and-bulk-actions-in-django-4bgd)
* [How to Use Django's Built-In User Authentication Views and Forms](https://vegibit.com/how-to-use-djangos-built-in-user-authentication-views-and-forms/)
* [BootstrapCDN](https://www.bootstrapcdn.com/bootswatch/)
* [openai-cookbook](https://github.com/openai/openai-cookbook/)
* [ChatGPT and JSON Responses: Prompting and Modifying Code-Friendly Objects](https://medium.com/@bobmain49/chatgpt-and-json-responses-prompting-modifying-code-friendly-objects-ad368822ec86)
* [The Leitner System: What It is, How It Works](https://e-student.org/leitner-system/)

## Future Work

A list of things that I need to fix, improve, and add in the future.

* *Fix the UI* - At two weeks, I'm still not able to do everything I wanted from the user interface.
* *Remove the tight coupling to User object* - Everything you create will be visible to you only. While that's a nice security feature, it means I can't easily share the quizzes with others.
* *Rate the questions* - It's still ChatGPT after all, so not everything you read here is God's honest truth. In fact, ChatGPT is notorious for making stuff up, completely fabricating APIs that don't exist. The data model supports the idea that you can suppress questions, but you should be able to at least verify that the question is valid. After all, **you are trying to learn the subject, so it had better be accurate!**

Anyhow, thanks for visiting.
