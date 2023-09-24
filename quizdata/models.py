from django.db import models


# Create your models here.
class Topic(models.Model):
    subtopic = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    topic_text = models.CharField(max_length=150, help_text="A topic or subtopic of study.")
    modified = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)


class Question(models.Model):
    QUESTION_TYPES = [("M", "Multiple Choice"), ("B", "Fill in the Blank")]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES)
    question_text = models.TextField(help_text="The question.")
    is_suppressed = models.BooleanField(default=False)
    modified = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)
    choice_order = models.IntegerField()
    modified = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)
