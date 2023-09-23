from django.db import models


# Create your models here.
class Topic(models.Model):
    topic = models.CharField(max_length=150, help_text="A topic or subtopic of study.")
    superTopic = models.ForeignKey(
        "self", null=True, parent_link=True, on_delete=models.SET_NULL, related_name="super_topic"
    )
    subtopic = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="sub_topics")
    created = models.DateField()

class Question(models.Model):
    topic = models.ForeignKey(Topic, parent_link=True, on_delete=)