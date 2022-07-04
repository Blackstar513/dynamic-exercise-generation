from django import forms
from ..models import Category, Course
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple

User = get_user_model()


class ExerciseSearchForm(forms.Form):
    text = forms.CharField(label="Exercise text", widget=forms.Textarea, required=False)
    categories = forms.ModelMultipleChoiceField(label="Categories", queryset=Category.objects.all(),
                                                widget=FilteredSelectMultiple("Categories", is_stacked=False),
                                                required=False)
    category_connect = forms.ChoiceField(label="Search must include", choices=(('all', "All"),
                                                                               ('any', "Any")),
                                         widget=forms.RadioSelect, initial='all', required=True)
    lecturers = forms.ModelMultipleChoiceField(label="Lecturers", queryset=User.objects.all(),
                                               widget=FilteredSelectMultiple("Lecturers", is_stacked=False),
                                               required=False)


class AssemblySearchForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput, required=False)
    categories = forms.ModelMultipleChoiceField(label="Categories", queryset=Category.objects.all(),
                                                widget=FilteredSelectMultiple("Categories", is_stacked=False),
                                                required=False)
    category_connect = forms.ChoiceField(label="Search must include", choices=(('all', "All"),
                                                                               ('any', "Any")),
                                         widget=forms.RadioSelect, initial='all', required=True)
    lecturers = forms.ModelMultipleChoiceField(label="Lecturers", queryset=User.objects.all(),
                                               widget=FilteredSelectMultiple("Lecturers", is_stacked=False),
                                               required=False)

