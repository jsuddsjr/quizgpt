from django.contrib.admin import TabularInline, ModelAdmin, site
from .models import Topic, Question, Choice
from .forms import AtLeastOneRequiredInlineFormSet


# Register your models here.
class ChoiceInline(TabularInline):
    formset = AtLeastOneRequiredInlineFormSet
    model = Choice
    extra = 1

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.question_type == "B":
            return 1
        return 5


class QuestionAdmin(ModelAdmin):
    model = Question
    inlines = [ChoiceInline]


class QuestionInline(TabularInline):
    fields = ["question_text", "question_type"]
    model = Question
    show_change_link = True


class SubtopicInline(TabularInline):
    model = Topic
    fk_name = "subtopic"
    verbose_name = "Subtopic"
    show_change_link = True
    extra = 0


class TopicAdmin(ModelAdmin):
    fields = ["topic_text", "slug"]
    list_display = ["topic_text", "modified"]
    inlines = [SubtopicInline, QuestionInline]
    prepopulated_fields = {"slug": ["topic_text"]}


site.register(Topic, TopicAdmin)
site.register(Question, QuestionAdmin)
