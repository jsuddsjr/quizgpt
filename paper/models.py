from django.db import models


class Paper(models.Model):
    title = models.CharField(max_length=255)


class DragQuestion(models.Model):
    description = models.TextField()
    answer = models.TextField()
    papers = models.ManyToManyField(Paper, through="PaperQuestion")


class PaperQuestion(models.Model):
    question = models.ForeignKey(DragQuestion, on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, on_delete=models.PROTECT)
    active = models.BooleanField()
    order = models.IntegerField()

    class Meta:
        ordering = [
            "order",
        ]
