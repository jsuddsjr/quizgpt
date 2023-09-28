from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import random


# Create your models here.
class Topic(models.Model):
    TOPIC_LEVELS = [(1, _("Basic")), (2, _("Intermediate")), (3, _("Advanced")), (4, _("Expert")), (5, _("Mastery"))]
    slug = models.SlugField(unique=True)
    subtopic_of = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    topic_text = models.CharField(max_length=150, help_text=_("A topic or subtopic of study."))
    description = models.CharField(max_length=1024, null=True, help_text=_("A brief introduction to the topic."))
    topic_level = models.IntegerField(choices=TOPIC_LEVELS, default=1)
    is_hidden = models.BooleanField(default=False, verbose_name=_("Hide from views"))
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_text

    def get_absolute_url(self):
        return reverse("quizdata:topic-detail", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.topic_text)
        super(Topic, self).save(*args, **kwargs)


class Question(models.Model):
    QUESTION_TYPES = [("M", _("Multiple Choice")), ("B", _("Fill in the Blank"))]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES, default="M")
    question_text = models.CharField(max_length=300, help_text=_("The question."))
    is_suppressed = models.BooleanField(null=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text

    def get_randomized_choices(self):
        return sorted(self.choice_set.all(), key=lambda x: random.random())


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)
    order = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.choice_text


class QuestionBucket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    bucket = models.IntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "question"], name="unique_user_question")]


class AnswerHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    question_bucket = models.ForeignKey(QuestionBucket, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "choice"], name="unique_user_choice")]
