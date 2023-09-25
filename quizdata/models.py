from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import string


# Create your models here.
class Topic(models.Model):
    TOPIC_LEVELS = [(1, _("Beginner")), (2, _("Intermediate")), (3, _("Advanced"))]
    slug = models.SlugField(unique=True)
    subtopic = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    topic_text = models.CharField(max_length=150, help_text=_("A topic or subtopic of study."))
    topic_level = models.IntegerField(choices=TOPIC_LEVELS, default=1)
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
    question_text = models.TextField(help_text=_("The question."))
    is_suppressed = models.BooleanField(null=True)
    force_ordered = models.BooleanField(null=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)
    choice_order = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_correct = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["choice_order"]

    def __repr__(self):
        return string.ascii_lowercase[self.choice_order] + ". " + self.choice_text
