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
    model = Question
    fields = ["question_text", "question_type", "is_suppressed"]
    show_change_link = True


class SubtopicInline(TabularInline):
    model = Topic
    fk_name = "subtopic_of"
    verbose_name = "Subtopic"
    show_change_link = True
    extra = 0


class TopicAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("topic_text",)}
    fields = ["topic_text", "description", "slug", "user", "is_hidden"]
    list_display = ["topic_text", "created", "modified", "user", "is_hidden"]
    inlines = [SubtopicInline, QuestionInline]


site.register(Topic, TopicAdmin)
site.register(Question, QuestionAdmin)
