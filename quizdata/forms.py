from django.forms import Form, CharField, BooleanField, TextInput, ValidationError
from django.forms.models import BaseInlineFormSet


class QuestionAdminForm(Form):
    question_text = TextInput
    option = CharField()
    option_active = BooleanField(initial=True)


class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """Check that at least one item has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get("DELETE", False) for cleaned_data in self.cleaned_data):
            raise ValidationError("At least one item required.")
