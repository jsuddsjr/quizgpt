from django.contrib import admin
from .models import Topic, Question, Choice


# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    min_num = 2
    ordering = "+choice_order"


class QuestionInline(admin.StackedInline):
    model = Question
    inlines = [ChoiceInline]


class SubtopicInline(admin.TabularInline):
    model = Topic
    fk_name = "subtopic"
    verbose_name = "Subtopic"
    extra = 2


class TopicAdmin(admin.ModelAdmin):
    fields = ["topic_text", "slug"]
    list_display = ("topic_text", "modified")
    inlines = [SubtopicInline, QuestionInline]
    prepopulated_fields = {"slug": ["topic_text"]}


admin.site.register(Topic, TopicAdmin)
