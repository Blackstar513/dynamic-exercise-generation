from django import forms
from ..models import Category, Course
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple

User = get_user_model()


class FullUserNameModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name}, {obj.first_name}" if obj.last_name else str(obj)


class ExerciseSearchForm(forms.Form):
    text = forms.CharField(label="Exercise text", widget=forms.Textarea(attrs={'cols': 136}), required=False)
    categories = forms.ModelMultipleChoiceField(label="Categories", queryset=Category.objects.all(),
                                                widget=FilteredSelectMultiple("Categories", is_stacked=False),
                                                required=False)
    category_connect = forms.ChoiceField(label="Category Constraint", choices=(('all', "All"),
                                                                               ('any', "Any")),
                                         widget=forms.RadioSelect, initial='all', required=True)
    lecturers = FullUserNameModelMultipleChoiceField(label="Lecturers", queryset=User.objects.all(),
                                                     widget=FilteredSelectMultiple("Lecturers", is_stacked=False),
                                                     required=False)
    courses = forms.ModelMultipleChoiceField(label="Courses", queryset=Course.objects.all(),
                                             widget=FilteredSelectMultiple("Courses", is_stacked=False),
                                             required=False)
    only_root = forms.BooleanField(label="Search only for root exercises?", initial=True, required=False)


class AssemblySearchForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput, required=False)
    categories = forms.ModelMultipleChoiceField(label="Categories", queryset=Category.objects.all(),
                                                widget=FilteredSelectMultiple("Categories", is_stacked=False),
                                                required=False)
    category_connect = forms.ChoiceField(label="Category Constraint", choices=(('all', "All"),
                                                                               ('any', "Any")),
                                         widget=forms.RadioSelect, initial='all', required=True)
    lecturers = FullUserNameModelMultipleChoiceField(label="Lecturers", queryset=User.objects.all(),
                                                     widget=FilteredSelectMultiple("Lecturers", is_stacked=False),
                                                     required=False)
    courses = forms.ModelMultipleChoiceField(label="Courses", queryset=Course.objects.all(),
                                             widget=FilteredSelectMultiple("Courses", is_stacked=False),
                                             required=False)

