from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

import string


# Create your models here.
class Topic(models.Model):
    slug = models.SlugField(unique=True)
    subtopic = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    topic_text = models.CharField(max_length=150, help_text="A topic or subtopic of study.")
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_text

    def get_absolute_url(self):
        return reverse("quizdata:topic_detail", args=[str(self.id), str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.topic_text)
        super(Topic, self).save(*args, **kwargs)


class Question(models.Model):
    QUESTION_TYPES = [("M", "Multiple Choice"), ("B", "Fill in the Blank")]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES, default="M")
    question_text = models.TextField(help_text="The question.")
    is_suppressed = models.BooleanField()
    force_ordered = models.BooleanField()
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    slug = models.SlugField(max_length=40)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)
    choice_order = models.IntegerField()
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["choice_order"]

    def __repr__(self):
        return string.ascii_lowercase[self.choice_order] + ". " + self.choice_text
