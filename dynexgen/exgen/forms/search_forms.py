from django import forms
from ..models import Category, Exercise


class ExerciseSearchForm(forms.Form):
    text = forms.CharField(label="Aufgabentext", widget=forms.Textarea, required=False)
    categories = forms.ModelMultipleChoiceField(label="Kategorien", queryset=Category.objects.all(), required=False)

# class ExerciseSearchForm(forms.ModelForm):
#     class Meta:
#         model = Exercise
#         fields = ['text', 'category']
